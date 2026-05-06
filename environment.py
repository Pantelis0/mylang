from __future__ import annotations
from typing import Optional


class RuntimeError(Exception):
    def __init__(self, message: str):
        super().__init__(f"RuntimeError: {message}")


class Environment:
    """
    Stores variable bindings for one scope level.

    `parent` points to the enclosing scope. `get` walks the chain upward;
    `set` always writes into the current scope, which is what makes
    `let i = i + 1` inside a loop update the right binding.
    """

    def __init__(self, parent: Optional[Environment] = None):
        self._vars: dict[str, object] = {}
        self.parent = parent

    def set(self, name: str, value: object) -> None:
        self._vars[name] = value

    def get(self, name: str) -> object:
        if name in self._vars:
            return self._vars[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise RuntimeError(f"undefined variable '{name}'")
