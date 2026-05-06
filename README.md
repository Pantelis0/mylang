# mylang — Custom Programming Language Interpreter

A complete programming language interpreter built in Python from scratch.

**Pipeline:** `source text → tokens → AST → evaluation`

---

## What the language can do

```
// variables
let x = 10;
let name = "world";

// arithmetic and comparisons
let result = x * 2 + 5;
if result > 20 {
    print("big number");
}

// while loops
let i = 0;
while i < 5 {
    print(i);
    let i = i + 1;
}

// functions and recursion
fn factorial(n) {
    if n < 2 { return 1; }
    return n * factorial(n - 1);
}
print(factorial(10));
```

---

## How to run

**Run a file:**
```bash
python main.py examples/hello.mylang
python main.py examples/fibonacci.mylang
python main.py examples/fizzbuzz.mylang
```

**Interactive REPL:**
```bash
python main.py --repl
```

---

## Project structure

```
mylang/
├── lexer.py          # Turns source text into tokens (TokenType, Token, Lexer)
├── parser.py         # AST node definitions + recursive descent parser
├── environment.py    # Variable scope storage with parent-chain lookup
├── interpreter.py    # Tree-walking evaluator
├── main.py           # File runner and REPL entry point
└── examples/
    ├── hello.mylang      # Variables, arithmetic, strings, comparisons
    ├── fibonacci.mylang  # Recursive function, while loop
    └── fizzbuzz.mylang   # Nested if/else, while loop, helper function
```

---

## Language features

| Feature | Syntax |
|---|---|
| Variable | `let x = 5;` |
| Print | `print(x);` |
| Arithmetic | `+ - * /` |
| Comparison | `< > <= >= == !=` |
| Boolean | `true` / `false` |
| String | `"hello"` and `+` concatenation |
| If / else | `if x > 0 { ... } else { ... }` |
| While loop | `while x < 10 { ... }` |
| Function | `fn add(a, b) { return a + b; }` |
| Recursion | Supported (e.g. factorial, fibonacci) |
| Comments | `// line comment` |

---

## How the interpreter works

The interpreter is built in four stages:

1. **Lexer** (`lexer.py`) — reads source text character by character and produces a flat list of tokens. Handles keywords, identifiers, numbers, strings, operators, and raises a `LexerError` with a line number on unknown input.

2. **Parser** (`parser.py`) — turns the token list into an Abstract Syntax Tree (AST) using recursive descent. Operator precedence is handled by the call chain: `comparison → addition → multiplication → unary → primary`. Each level only handles its own operators and delegates everything higher-priority upward.

3. **Environment** (`environment.py`) — a dictionary that stores variable bindings for one scope level. Has a `parent` reference so inner scopes (function calls) can look up variables from outer scopes.

4. **Interpreter** (`interpreter.py`) — walks the AST and evaluates each node. Statements and expressions are handled in a single `evaluate()` method dispatching on node type. Function calls create a new child Environment and use a `_ReturnException` to unwind the call stack when a `return` statement is hit.

---

## Error messages

Every error includes a clear description — no raw Python tracebacks:

```
[Line 3] LexerError: unexpected character '@'
[Line 5] ParseError: expected 'SEMICOLON' but got 'EOF'
RuntimeError: undefined variable 'x'
RuntimeError: division by zero
RuntimeError: 'factorial' expects 1 argument(s) but got 2
```

---

## Completed milestones

- [x] Lexer — 37 token types, integers, floats, strings, keywords, operators
- [x] AST node definitions — 14 node types for expressions and statements
- [x] Expression parser — correct operator precedence (`*` before `+`)
- [x] Statement parser — `let`, `print`, `if/else`, `while`, `fn`, `return`, blocks
- [x] Expression evaluator — arithmetic, comparisons, string concatenation
- [x] Statement evaluator — variables, control flow, loops
- [x] Functions — declarations, calls, recursion, scoped environments, `return`
- [x] Error messages — `LexerError`, `ParseError`, `RuntimeError` with line numbers
- [x] File runner and interactive REPL
- [x] Example programs

---

## Resources

- Robert Nystrom, *Crafting Interpreters* (overall architecture)
- Python `dataclasses` and `enum` documentation
