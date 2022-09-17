from os import listdir
from os.path import isfile, join

import parser as parser
import lexer as lexer


mypath = "tests/"
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
filtered_files = ["tests/" + element for element in files if element.endswith('.py') and not element.startswith('bad')]

for filename in filtered_files:
    with open(filename) as f:
        parser = parser.Parser(f)
        parser.parse()
        print("fully parsed")
        # lex = lexer.Lexer(f)
        # token = lex.next()
        # while token.type != lexer.Tokentype.EOI:
        #     print(token.type, " ", token.lexeme, " ", token.location.line, token.location.col)
        #     token = lex.next()
