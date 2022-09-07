#
# A recursive-descent parser for parsing boolean expressions.
#
# E -> E or E | E and E | not E | ( E ) | True | False

# 1. Rewrite your grammar to be suitable for recursive-descent parsing:
#
"""
    E -> E or E | E and E | not E | ( E ) | True | False

    becomes:


"""

from lab01.lexer import Lexer, Tokentype, SyntaxErrorException

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

    # Finish implementing the parser. A call to parse, parses a single Boolean expression.
    def parse(self):
        ...
