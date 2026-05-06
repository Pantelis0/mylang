from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from lexer import Lexer, Token, TokenType


# ── Base ──────────────────────────────────────────────────────────────────────

class ASTNode:
    """Base class for every node in the syntax tree."""


# ── Expression nodes ──────────────────────────────────────────────────────────

@dataclass
class NumberLiteral(ASTNode):
    value: int | float


@dataclass
class BoolLiteral(ASTNode):
    value: bool


@dataclass
class StringLiteral(ASTNode):
    value: str


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class BinaryOp(ASTNode):
    left:  ASTNode
    op:    str       # '+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>='
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    op:      str     # '-' (negation) — expandable later
    operand: ASTNode


@dataclass
class FunctionCall(ASTNode):
    name: str
    args: list[ASTNode] = field(default_factory=list)


# ── Statement nodes ───────────────────────────────────────────────────────────

@dataclass
class LetStatement(ASTNode):
    name:  str
    value: ASTNode


@dataclass
class PrintStatement(ASTNode):
    expr: ASTNode


@dataclass
class Block(ASTNode):
    statements: list[ASTNode] = field(default_factory=list)


@dataclass
class IfStatement(ASTNode):
    condition:  ASTNode
    then_block: Block
    else_block: Optional[Block] = None


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body:      Block


@dataclass
class FunctionDecl(ASTNode):
    name:   str
    params: list[str] = field(default_factory=list)
    body:   Optional[Block] = None


@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode] = None


# ── Operator token → string map ───────────────────────────────────────────────

_OP = {
    TokenType.PLUS:   '+',  TokenType.MINUS:  '-',
    TokenType.STAR:   '*',  TokenType.SLASH:  '/',
    TokenType.EQEQ:  '==',  TokenType.BANGEQ: '!=',
    TokenType.LT:    '<',   TokenType.GT:     '>',
    TokenType.LTEQ:  '<=',  TokenType.GTEQ:   '>=',
}

_CMP_OPS = {TokenType.LT, TokenType.GT, TokenType.LTEQ,
            TokenType.GTEQ, TokenType.EQEQ, TokenType.BANGEQ}


# ── Errors ────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    def __init__(self, message, line):
        super().__init__(f"[Line {line}] ParseError: {message}")
        self.line = line


# ── Parser ────────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos    = 0

    # ── navigation helpers ────────────────────────────────────────────────────

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _check(self, *types: TokenType) -> bool:
        return self._current().type in types

    def _match(self, *types: TokenType) -> Optional[Token]:
        """Consume and return the current token if its type is in `types`."""
        if self._check(*types):
            return self._advance()
        return None

    def _expect(self, ttype: TokenType) -> Token:
        tok = self._current()
        if tok.type != ttype:
            raise ParseError(
                f"expected '{ttype.name}' but got '{tok.type.name}'", tok.line
            )
        return self._advance()

    # ── expression grammar (low → high precedence) ────────────────────────────
    #
    #   parse_comparison  →  parse_expr  (op: < > <= >= == !=)
    #   parse_expr        →  parse_term  (op: + -)
    #   parse_term        →  parse_unary (op: * /)
    #   parse_unary       →  parse_primary (op: unary -)
    #   parse_primary     →  literal | identifier | call | ( expr )
    #
    # Each level calls the level above it for its operands, which is what
    # makes * bind tighter than + without any special-casing.

    def parse_comparison(self) -> ASTNode:
        left = self.parse_expr()
        while self._check(*_CMP_OPS):
            op  = _OP[self._advance().type]
            right = self.parse_expr()
            left  = BinaryOp(left, op, right)
        return left

    def parse_expr(self) -> ASTNode:
        left = self.parse_term()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op    = _OP[self._advance().type]
            right = self.parse_term()
            left  = BinaryOp(left, op, right)
        return left

    def parse_term(self) -> ASTNode:
        left = self.parse_unary()
        while self._check(TokenType.STAR, TokenType.SLASH):
            op    = _OP[self._advance().type]
            right = self.parse_unary()
            left  = BinaryOp(left, op, right)
        return left

    def parse_unary(self) -> ASTNode:
        if self._check(TokenType.MINUS):
            self._advance()
            return UnaryOp('-', self.parse_unary())   # right-associative
        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        tok = self._current()

        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberLiteral(tok.value)

        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteral(tok.value)

        if tok.type == TokenType.TRUE:
            self._advance()
            return BoolLiteral(True)

        if tok.type == TokenType.FALSE:
            self._advance()
            return BoolLiteral(False)

        if tok.type == TokenType.IDENT:
            self._advance()
            if self._check(TokenType.LPAREN):       # function call
                self._advance()                     # consume (
                args = []
                if not self._check(TokenType.RPAREN):
                    args.append(self.parse_comparison())
                    while self._match(TokenType.COMMA):
                        args.append(self.parse_comparison())
                self._expect(TokenType.RPAREN)
                return FunctionCall(tok.value, args)
            return Identifier(tok.value)

        if tok.type == TokenType.LPAREN:
            self._advance()                         # consume (
            expr = self.parse_comparison()
            self._expect(TokenType.RPAREN)
            return expr

        raise ParseError(
            f"unexpected token '{tok.type.name}'"
            + (f" (value={tok.value!r})" if tok.value is not None else ""),
            tok.line,
        )

    # ── statement parsers ─────────────────────────────────────────────────────

    def parse_block(self) -> Block:
        """Parse `{ statement* }` and return a Block."""
        self._expect(TokenType.LBRACE)
        stmts = []
        while not self._check(TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.parse_statement())
        self._expect(TokenType.RBRACE)
        return Block(stmts)

    def parse_statement(self) -> ASTNode:
        tok = self._current()

        if tok.type == TokenType.LET:
            return self._parse_let()
        if tok.type == TokenType.PRINT:
            return self._parse_print()
        if tok.type == TokenType.IF:
            return self._parse_if()
        if tok.type == TokenType.WHILE:
            return self._parse_while()
        if tok.type == TokenType.FN:
            return self._parse_fn()
        if tok.type == TokenType.RETURN:
            return self._parse_return()

        # expression statement — e.g. a bare function call like foo(x);
        expr = self.parse_comparison()
        self._expect(TokenType.SEMICOLON)
        return expr

    def _parse_let(self) -> LetStatement:
        self._advance()                          # consume 'let'
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.EQ)
        value = self.parse_comparison()
        self._expect(TokenType.SEMICOLON)
        return LetStatement(name, value)

    def _parse_print(self) -> PrintStatement:
        self._advance()                          # consume 'print'
        self._expect(TokenType.LPAREN)
        expr = self.parse_comparison()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.SEMICOLON)
        return PrintStatement(expr)

    def _parse_if(self) -> IfStatement:
        self._advance()                          # consume 'if'
        condition  = self.parse_comparison()
        then_block = self.parse_block()
        else_block = None
        if self._match(TokenType.ELSE):
            else_block = self.parse_block()
        return IfStatement(condition, then_block, else_block)

    def _parse_while(self) -> WhileStatement:
        self._advance()                          # consume 'while'
        condition = self.parse_comparison()
        body      = self.parse_block()
        return WhileStatement(condition, body)

    def _parse_fn(self) -> FunctionDecl:
        self._advance()                          # consume 'fn'
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.LPAREN)
        params = []
        if not self._check(TokenType.RPAREN):
            params.append(self._expect(TokenType.IDENT).value)
            while self._match(TokenType.COMMA):
                params.append(self._expect(TokenType.IDENT).value)
        self._expect(TokenType.RPAREN)
        body = self.parse_block()
        return FunctionDecl(name, params, body)

    def _parse_return(self) -> ReturnStatement:
        self._advance()                          # consume 'return'
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self.parse_comparison()
        self._expect(TokenType.SEMICOLON)
        return ReturnStatement(value)

    # ── public entry points ───────────────────────────────────────────────────

    def parse_program(self) -> list[ASTNode]:
        """Parse a full program — a sequence of statements until EOF."""
        stmts = []
        while not self._check(TokenType.EOF):
            stmts.append(self.parse_statement())
        return stmts

    @classmethod
    def from_source(cls, source: str) -> "Parser":
        tokens = Lexer(source).tokenize()
        return cls(tokens)
