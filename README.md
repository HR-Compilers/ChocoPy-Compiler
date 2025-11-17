# ChocoPy Compiler

A Python-based compiler for the ChocoPy programming language - a statically-typed, Python-inspired language designed for educational purposes.

## Overview

ChocoPy is a statically-typed, object-oriented programming language with Python-like syntax, developed to help computer science students learn compiler fundamentals. This compiler implementation provides:

- **Lexical Analysis** - Tokenization and syntax error detection
- **Parsing** - AST construction from source code
- **Semantic Analysis** - Symbol table construction and type checking
- **Error Reporting** - Comprehensive error messages for syntax and semantic errors

## Language Features

### Basic Syntax
- Python-inspired syntax with static typing
- Type annotations for variables, parameters, and return values
- Support for classes, functions, and nested scopes
- Built-in types: `int`, `str`, `bool`, `object`, and lists

### Control Structures
- `if`/`elif`/`else` statements
- `while` loops
- `for` loops with iteration
- Function definitions with return types

### Object-Oriented Features
- Class definitions with inheritance
- Instance methods and attributes
- Constructor methods (`__init__`)
- Member access and method calls

### Built-in Functions
- `print()` - Output to console
- `input()` - Read user input
- `len()` - Get length of collections

## Project Structure

```
├── main.py              # Main compiler entry point
├── lexer.py             # Lexical analyzer
├── parser.py            # Parser and AST construction
├── astree.py            # Abstract Syntax Tree definitions
├── visitor.py           # Base visitor class for AST traversal
├── symtab_visitor.py    # Symbol table construction
├── type_visitor.py      # Type checking implementation
├── semantic_error.py    # Error classes and handling
├── symbol_table.py      # Symbol table data structures
├── type_env.py          # Type environment management
├── print_visitor.py     # AST pretty printer
├── disp_symtable.py     # Symbol table display
├── grammar.txt          # Language grammar specification
└── tests/               # Test cases and examples
```

## Usage

### Running the Compiler

```bash
# Run with default test file
python3 main.py

# Run with specific ChocoPy file
python3 main.py path/to/file.cpy
```

### Example ChocoPy Program

```python
class Counter(object):
    count: int = 0
    
    def increment(self: "Counter") -> int:
        self.count = self.count + 1
        return self.count

c: Counter = None
c = Counter()
print(c.increment())  # Output: 1
```

## Development

### Code Style
- **Imports**: Group standard lib, third-party, local imports with blank lines
- **Formatting**: 4-space indentation, snake_case for functions/variables
- **Types**: Use type hints for function parameters and returns
- **Naming**: PascalCase for classes, snake_case for functions/variables
- **Error Handling**: Raise `semantic_error.CompilerException` subclasses
- **Visitor Pattern**: Extend `visitor.Visitor` class for AST traversal

### Testing
Test files are located in the `tests/` directory. Each `.cpy` file contains ChocoPy code that can be compiled and analyzed.

## Authors

- Bas Laarakker (@BasLaa)
- Matteo Becatti (@meloncruuush)

Developed during an exchange semester at Reykjavik University.

## License

This project is for educational purposes. See individual source files for license information.