from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


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
