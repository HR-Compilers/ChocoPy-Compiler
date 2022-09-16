import parser as parser
import lexer as lexer

filename = 'test3.txt'
with open(filename) as f:
    parser = parser.Parser(f)
    parser.parse()
    print("fully parsed")