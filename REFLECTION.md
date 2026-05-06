# Reflection — Custom Programming Language Interpreter

---

## (1) What was easy, and what required more thinking and skill?

### What felt manageable

The overall structure of the project was something I could reason through fairly quickly once I understood the pipeline: source text → tokens → AST → evaluation. Each stage has a clear job and a clear output, which made it possible to build and test one layer at a time without worrying about the layers below or above it.

The **lexer** was the most straightforward part. Reading characters one by one, recognising keywords and operators, and producing a flat list of tokens is repetitive work with few surprises. Python's `Enum` and `dataclass` also helped a lot — they removed a lot of boilerplate so the code stayed readable.

The **evaluator** for simple expressions and statements was also not too difficult once the AST was in place. Dispatching on node type and recursively evaluating sub-nodes is a pattern that makes sense once you see it. The `LetStatement`, `PrintStatement`, and `IfStatement` cases were almost self-documenting.

### What required real thinking

**Operator precedence in the parser** was the hardest conceptual problem in the project. The issue is that `2 + 3 * 4` must evaluate to `14`, not `20`, and it is the *tree structure* — not the evaluator — that must encode this. The solution is the recursive descent call chain: `parse_comparison` calls `parse_expr` which calls `parse_term` which calls `parse_unary` which calls `parse_primary`. Each level only handles its own operators and passes everything else up. Once this clicked, the parser almost wrote itself, but it took a while to internalise why the chain had to be in that exact order.

**Function scope and the `_ReturnException` pattern** also needed careful thought. There are two non-obvious design decisions:

- Arguments must be evaluated in the *caller's* environment before the new scope is created, so that parameter names cannot shadow outer variables during argument evaluation. For example, if `x` is both a global variable and a function parameter, `f(x + 1)` should read the global `x`, not the parameter.
- A `return` statement must unwind the call stack through any number of nested blocks, `if` branches, and `while` loops. The cleanest way to do this in Python is to raise a custom exception (`_ReturnException`) that propagates naturally up through everything and is caught only at the `_eval_call` level.

These were not things I had seen before — working them out required reasoning carefully about what the code should do before writing it.

---

## (2) How did class notes and Khan Academy exercises help?

The class notes gave me the vocabulary and mental models I needed before I could make sense of any code. Specifically:

- **Variables and assignment** — understanding that a variable is a name bound to a value in memory directly maps to the `Environment` class: `env.set(name, value)` and `env.get(name)`.
- **Control flow** — practising `if/else` and `while` loops in exercises made me confident about what those constructs should *do*. When I came to implement `IfStatement` and `WhileStatement` in the evaluator, I already had a clear mental model of their semantics.
- **Functions** — the exercises that involved writing and calling functions with parameters and return values built the intuition that a function call creates its own isolated scope. This is exactly what the `Environment(parent=env)` call implements: a fresh dictionary for the function's local variables that can still look up globals through the parent chain.
- **Arithmetic and order of operations** — Khan Academy's order-of-operations exercises turned out to be directly relevant to building the parser's precedence chain. PEMDAS/BODMAS is not just a maths rule; it is the rule that tells you in what order to build the `parse_term` → `parse_expr` hierarchy.

Without that foundation the code would have been impossible to reason about, let alone write.

---

## (3) Other references used

**Robert Nystrom, *Crafting Interpreters*** (craftinginterpreters.com) — this is the main external reference for the overall architecture. The book explains the lexer → parser → evaluator pipeline in detail. I used it to understand the shape of the project and the recursive descent technique before writing anything. I did not copy code directly from it because the book uses Java (Part I) and C (Part II), but the structure of my lexer and parser follows the same principles.

**Python documentation** — specifically the `dataclasses` module and the `Enum` class. Using `@dataclass` for AST nodes and `Enum` for `TokenType` is a Python-specific choice. I read the official docs to understand the `field(default_factory=list)` syntax for mutable default fields, which is needed for nodes like `Block(statements=[])`.

**General internet search** — for the `_ReturnException` pattern (using a Python exception to implement a language-level `return` statement). This is a known technique in interpreter implementation. I looked up how other simple Python interpreters handle this to confirm the approach before using it.

On the question of copying code: I did not copy complete blocks verbatim, but I did use the `_ReturnException` pattern after seeing it described online. The act of reading it, understanding why it works (Python exceptions unwind the call stack naturally), and then implementing it myself was valuable — it is a good example of learning by tracing how someone else's idea works and then applying it in your own context.

---

## (4) Sufficient progress, or could more have been made?

I believe the progress made on this project was genuine and substantial. Starting from zero interpreter knowledge, the project reached a working programming language with variables, arithmetic, booleans, strings, control flow, loops, functions, recursion, scope, and error handling — all in a single codebase of under 850 lines of Python.

The areas where I could have pushed further:

- **More built-in operations** — the language currently has no modulo operator (`%`), no way to convert numbers to strings, and no built-in list or array type. These would make it more practical to write programs in.
- **Better error recovery** — right now the interpreter stops at the first error. A production language reports multiple errors in one pass so the user can fix them all at once.
- **Closures** — the current scoping is dynamic (a function sees variables from its call site). True closures, where a function captures the environment where it was *defined*, would require storing a reference to the defining scope alongside the function declaration. This is the next logical step in understanding how real languages work.

Where I feel I made the most progress is in understanding that a programming language is not magic — it is just a program that reads text and follows rules. The lexer, parser, and evaluator are each solving a clearly defined, manageable problem. That demystification is probably the most valuable outcome of this project.
