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
        self.program()
        self.match(Tokentype.EOI)

    # program ::= [[var def | func def | class def]]* stmt*
    def program(self):
        while True:
            if self.match_if(Tokentype.KwClass):
                self.class_def()
            elif self.match_if(Tokentype.KwDef):
                self.func_def()
            elif self.match_if(Tokentype.Identifier):
                self.var_def()
            else:
                break
        


    def class_def(self):
        self.match(Tokentype.KwClass)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisL)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisR)
        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        self.class_body()
        self.match(Tokentype.Dedent)

    def func_def(self):
        self.match(Tokentype.kwDef)
        ...

    def var_def(self):
        self.typed_var()
        self.match(Tokentype.OpEq)
        self.literal()
        self.match(Tokentype.Newline)

    def stmt(self):
        ...
