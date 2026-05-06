"""
mylang — entry point

Usage:
    python main.py program.mylang      run a file
    python main.py --repl              start the interactive REPL
"""

import sys

from lexer       import Lexer, LexerError
from parser      import Parser, ParseError
from environment import Environment, RuntimeError as LangRuntimeError
from interpreter import Interpreter, _ReturnException


def run_file(path: str) -> None:
    try:
        source = open(path).read()
    except FileNotFoundError:
        print(f"Error: file '{path}' not found.")
        sys.exit(1)

    interp = Interpreter()
    _execute(interp, source, Environment())


def run_repl() -> None:
    print("mylang REPL — type 'exit' to quit")
    interp = Interpreter()
    env    = Environment()          # persistent across REPL lines

    while True:
        try:
            line = input("» ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line or line == "exit":
            break

        _execute(interp, line, env)


def _execute(interp: Interpreter, source: str, env: Environment) -> None:
    """Run source through the full pipeline, printing clean errors on failure."""
    try:
        from parser import Parser
        stmts = Parser.from_source(source).parse_program()
        for stmt in stmts:
            interp.evaluate(stmt, env)

    except LexerError as e:
        print(e)
    except ParseError as e:
        print(e)
    except LangRuntimeError as e:
        print(e)
    except _ReturnException:
        print("RuntimeError: 'return' statement outside of a function")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--repl":
        run_repl()
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        print("Usage:")
        print("  python main.py program.mylang")
        print("  python main.py --repl")
        sys.exit(1)
