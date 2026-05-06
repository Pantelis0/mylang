from __future__ import annotations

from parser import (
    ASTNode,
    NumberLiteral, BoolLiteral, StringLiteral,
    Identifier, BinaryOp, UnaryOp, FunctionCall,
    LetStatement, PrintStatement, Block,
    IfStatement, WhileStatement, FunctionDecl, ReturnStatement,
)
from environment import Environment, RuntimeError


# ── sentinel used to unwind the call stack on `return` ───────────────────────
# Defined here so Phase 7 can raise it inside function bodies.

class _ReturnException(Exception):
    def __init__(self, value):
        self.value = value


# ── interpreter ───────────────────────────────────────────────────────────────

class Interpreter:

    def evaluate(self, node: ASTNode, env: Environment) -> object:

        # ── literals ──────────────────────────────────────────────────────────
        if isinstance(node, NumberLiteral):  return node.value
        if isinstance(node, BoolLiteral):    return node.value
        if isinstance(node, StringLiteral):  return node.value

        # ── identifier lookup ─────────────────────────────────────────────────
        if isinstance(node, Identifier):
            return env.get(node.name)

        # ── operators ─────────────────────────────────────────────────────────
        if isinstance(node, BinaryOp):
            return self._eval_binary(node, env)

        if isinstance(node, UnaryOp):
            val = self.evaluate(node.operand, env)
            if node.op == '-':
                self._assert_number(val, "unary '-'")
                return -val
            raise RuntimeError(f"unknown unary operator '{node.op}'")

        # ── statements ────────────────────────────────────────────────────────
        if isinstance(node, LetStatement):
            env.set(node.name, self.evaluate(node.value, env))
            return None

        if isinstance(node, PrintStatement):
            val = self.evaluate(node.expr, env)
            print(self._display(val))
            return None

        if isinstance(node, Block):
            for stmt in node.statements:
                self.evaluate(stmt, env)
            return None

        if isinstance(node, IfStatement):
            if self.evaluate(node.condition, env):
                self.evaluate(node.then_block, env)
            elif node.else_block is not None:
                self.evaluate(node.else_block, env)
            return None

        if isinstance(node, WhileStatement):
            while self.evaluate(node.condition, env):
                self.evaluate(node.body, env)
            return None

        raise RuntimeError(f"cannot evaluate node type '{type(node).__name__}'")

    # ── binary operator evaluation ────────────────────────────────────────────

    def _eval_binary(self, node: BinaryOp, env: Environment) -> object:
        left  = self.evaluate(node.left,  env)
        right = self.evaluate(node.right, env)
        op    = node.op

        # + handles both numbers and strings
        if op == '+':
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            raise RuntimeError(
                f"'+' requires two numbers or two strings, "
                f"got {type(left).__name__} and {type(right).__name__}"
            )

        # arithmetic (numbers only)
        if op == '-':
            self._assert_number(left, op); self._assert_number(right, op)
            return left - right

        if op == '*':
            self._assert_number(left, op); self._assert_number(right, op)
            return left * right

        if op == '/':
            self._assert_number(left, op); self._assert_number(right, op)
            if right == 0:
                raise RuntimeError("division by zero")
            result = left / right
            # 10 / 2 → 5 (not 5.0) so the REPL and print stay clean
            return int(result) if isinstance(result, float) and result.is_integer() else result

        # ordered comparisons (numbers only)
        if op in ('<', '>', '<=', '>='):
            self._assert_number(left, op); self._assert_number(right, op)
            if op == '<':  return left <  right
            if op == '>':  return left >  right
            if op == '<=': return left <= right
            if op == '>=': return left >= right

        # equality works for any type
        if op == '==': return left == right
        if op == '!=': return left != right

        raise RuntimeError(f"unknown operator '{op}'")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _assert_number(self, val: object, context: str) -> None:
        if not isinstance(val, (int, float)):
            raise RuntimeError(
                f"'{context}' requires a number, got {type(val).__name__}"
            )

    def _display(self, val: object) -> str:
        """Format a value for print() — booleans show as true/false."""
        if isinstance(val, bool):
            return "true" if val else "false"
        return str(val)

    # ── public runner ─────────────────────────────────────────────────────────

    def run(self, source: str, env: Environment | None = None) -> None:
        """Lex → parse → evaluate a full program string."""
        from parser import Parser
        if env is None:
            env = Environment()
        stmts = Parser.from_source(source).parse_program()
        for stmt in stmts:
            self.evaluate(stmt, env)
