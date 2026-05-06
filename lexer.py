from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Literals
    NUMBER     = auto()
    STRING     = auto()
    TRUE       = auto()
    FALSE      = auto()

    # Identifier
    IDENT      = auto()

    # Keywords
    LET        = auto()
    IF         = auto()
    ELSE       = auto()
    WHILE      = auto()
    FN         = auto()
    RETURN     = auto()
    PRINT      = auto()

    # Arithmetic operators
    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()

    # Comparison operators
    EQ         = auto()   # =
    EQEQ       = auto()   # ==
    BANGEQ     = auto()   # !=
    LT         = auto()   # <
    GT         = auto()   # >
    LTEQ       = auto()   # <=
    GTEQ       = auto()   # >=

    # Punctuation
    LPAREN     = auto()   # (
    RPAREN     = auto()   # )
    LBRACE     = auto()   # {
    RBRACE     = auto()   # }
    COMMA      = auto()   # ,
    SEMICOLON  = auto()   # ;

    EOF        = auto()


KEYWORDS = {
    "let":    TokenType.LET,
    "if":     TokenType.IF,
    "else":   TokenType.ELSE,
    "while":  TokenType.WHILE,
    "fn":     TokenType.FN,
    "return": TokenType.RETURN,
    "print":  TokenType.PRINT,
    "true":   TokenType.TRUE,
    "false":  TokenType.FALSE,
}


@dataclass
class Token:
    type:  TokenType
    value: object   # str or int/float, None for punctuation/keywords
    line:  int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


class LexerError(Exception):
    def __init__(self, message, line):
        super().__init__(f"[Line {line}] LexerError: {message}")
        self.line = line


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1

    # ── internal helpers ──────────────────────────────────────────────────────

    def _at_end(self):
        return self.pos >= len(self.source)

    def _current(self):
        return self.source[self.pos] if not self._at_end() else "\0"

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def _match(self, expected):
        """Consume the next character only if it equals `expected`."""
        if self._at_end() or self._current() != expected:
            return False
        self.pos += 1
        return True

    # ── individual token readers ──────────────────────────────────────────────

    def _read_number(self):
        start = self.pos - 1          # first digit already consumed
        has_dot = False
        while self._current().isdigit() or (self._current() == "." and not has_dot):
            if self._current() == ".":
                has_dot = True
            self._advance()
        raw = self.source[start:self.pos]
        return float(raw) if has_dot else int(raw)

    def _read_string(self):
        start_line = self.line
        chars = []
        while not self._at_end() and self._current() != '"':
            chars.append(self._advance())
        if self._at_end():
            raise LexerError("unterminated string literal", start_line)
        self._advance()               # consume closing "
        return "".join(chars)

    def _read_ident(self):
        start = self.pos - 1          # first char already consumed
        while self._current().isalnum() or self._current() == "_":
            self._advance()
        return self.source[start:self.pos]

    # ── main tokenise loop ────────────────────────────────────────────────────

    def tokenize(self) -> list[Token]:
        tokens = []

        while not self._at_end():
            ch = self._advance()

            # whitespace — newlines tracked inside _advance
            if ch in (" ", "\t", "\r", "\n"):
                continue

            # line comments  // ...
            if ch == "/" and self._current() == "/":
                while not self._at_end() and self._current() != "\n":
                    self._advance()
                continue

            line = self.line   # snapshot line for this token

            # ── literals ──────────────────────────────────────────────────────
            if ch.isdigit():
                value = self._read_number()
                tokens.append(Token(TokenType.NUMBER, value, line))

            elif ch == '"':
                value = self._read_string()
                tokens.append(Token(TokenType.STRING, value, line))

            # ── identifiers / keywords ────────────────────────────────────────
            elif ch.isalpha() or ch == "_":
                name  = self._read_ident()
                ttype = KEYWORDS.get(name, TokenType.IDENT)
                # only store the string value for plain identifiers
                value = name if ttype == TokenType.IDENT else None
                tokens.append(Token(ttype, value, line))

            # ── two-char operators then single-char fallback ───────────────────
            elif ch == "=":
                tokens.append(Token(TokenType.EQEQ   if self._match("=") else TokenType.EQ,    None, line))
            elif ch == "!":
                if not self._match("="):
                    raise LexerError("unexpected character '!'", line)
                tokens.append(Token(TokenType.BANGEQ, None, line))
            elif ch == "<":
                tokens.append(Token(TokenType.LTEQ   if self._match("=") else TokenType.LT,    None, line))
            elif ch == ">":
                tokens.append(Token(TokenType.GTEQ   if self._match("=") else TokenType.GT,    None, line))

            # ── single-char punctuation ───────────────────────────────────────
            elif ch == "+":  tokens.append(Token(TokenType.PLUS,      None, line))
            elif ch == "-":  tokens.append(Token(TokenType.MINUS,     None, line))
            elif ch == "*":  tokens.append(Token(TokenType.STAR,      None, line))
            elif ch == "/":  tokens.append(Token(TokenType.SLASH,     None, line))
            elif ch == "(":  tokens.append(Token(TokenType.LPAREN,    None, line))
            elif ch == ")":  tokens.append(Token(TokenType.RPAREN,    None, line))
            elif ch == "{":  tokens.append(Token(TokenType.LBRACE,    None, line))
            elif ch == "}":  tokens.append(Token(TokenType.RBRACE,    None, line))
            elif ch == ",":  tokens.append(Token(TokenType.COMMA,     None, line))
            elif ch == ";":  tokens.append(Token(TokenType.SEMICOLON, None, line))

            else:
                raise LexerError(f"unexpected character '{ch}'", line)

        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens
