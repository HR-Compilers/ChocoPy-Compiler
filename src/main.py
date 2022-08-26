#
# T-603-THYD Compilers
# Project: Test driver for lexer
#
import lexer
filename = "src/file.py"
with open(filename) as f:
    lex = lexer.Lexer(f)
    token = lex.next()
    while token.type != lexer.Tokentype.EOI:
        print(token.type, token.lexeme if token.type != lexer.Tokentype.Newline else "\\n", token.location.line)
        token = lex.next()
