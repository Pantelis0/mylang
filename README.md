# mylang — Custom Programming Language Interpreter

A mini programming language built in Python from scratch.

Pipeline: `source text → tokens → AST → evaluation`

## Project structure

```
mylang/
├── lexer.py        # Tokenizes source text
├── parser.py       # Builds the AST from tokens
├── interpreter.py  # Walks the AST and evaluates it
├── environment.py  # Variable/scope storage
├── main.py         # Entry point (REPL or file runner)
└── examples/       # Sample .mylang programs
```

## Milestone checklist

- [ ] Define token types and implement the lexer
- [ ] Parse numbers, identifiers, and arithmetic expressions
- [ ] Implement correct precedence for `+ - * /`
- [ ] Add variable declarations: `let x = 5`
- [ ] Add `print(...)`
- [ ] Add comparison operators: `< > == !=`
- [ ] Add `if / else`
- [ ] Add `while`
- [ ] Add functions with parameters and return values
- [ ] Add strings
- [ ] Improve error messages
- [ ] Add a REPL and file runner

## Running

```bash
python main.py examples/hello.mylang
```

## Resources

- Robert Nystrom, *Crafting Interpreters*
