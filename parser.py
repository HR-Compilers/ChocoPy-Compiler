from lexer import Lexer, Tokentype, SyntaxErrorException
import ast

class Parser:
    def __init__(self, f):
        self.lexer = Lexer(f)
        self.token = self.lexer.next()
    # Helper function.
    def match(self, type):
        if self.token.type == type:
            self.token = self.lexer.next()
        else:
            text = "Syntax error: expected {:s} but got {:s} ({:s}).".format(
                type, self.token.type, self.token.lexeme
            )
            raise SyntaxErrorException(text, self.token.location)
    # Helper function
    def match_if(self, type):
        if self.token.type == type:
            self.match(type)
            return True
        return False

    # Finish implementing the parser.
    # The file should return an AST if parsing is successful, 
    # otherwise a syntax-error exception is thrown.
    def parse(self):
        return None