import parser as parser
import lexer as lexer

filename = 'test.txt'
with open(filename) as f:
    # parser = parser.Parser(f)
    # parser.parse()
    # print("fully parsed")
    lex = lexer.Lexer(f)
    token = lex.next()
    while token.type != lexer.Tokentype.EOI:
        print(token.type, " ", token.lexeme, " ", token.location.line, token.location.col)
        token = lex.next()