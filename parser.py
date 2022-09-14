from lexer import Lexer, Tokentype, SyntaxErrorException
import ast

class Parser:
    def __init__(self, f):
        self.lexer = Lexer(f)
        self.token = self.lexer.next()
        self.peek_token = None
    
    # for peek function, alter the match
    def peek(self):
        if self.peek_token is None:
            self.peek_token = self.lexer.next()
        return self.peek_token

    # Helper function.
    def match(self, type):
        if self.token.type == type:
            if self.peek_token is None:
                self.token = self.lexer.next()
            else:
                self.token = self.peek_token
                self.peek_token = None
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
        # we need one more lookahead for var_def as stmt can start with ID as well
        # we need to peek if the next token is a colon: elif self.peek() == colon
        while self.token.type in [Tokentype.KwDef, Tokentype.KwClass, Tokentype.Identifier]:
            if self.token.type == Tokentype.KwClass:
                self.class_def()
            elif self.token.type == Tokentype.KwDef:
                self.func_def()
            else:
                if self.peek() == Tokentype.Colon:
                    self.var_def()
                else:
                    break
        
        while self.token.type is not Tokentype.EOI:
            self.stmt()

    # class_def ::= class ID ( ID ) : NEWLINE INDENT class_body DEDENT
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

    # class_body ::= pass NEWLINE
    #               | [[var_def | func_def]]+
    def class_body(self):
        if self.token.type == Tokentype.KwPass:
            self.match(Tokentype.KwPass)
            self.match(Tokentype.Newline)
        else:
            # we must have at least one var_def or func_def
            if self.token.type == Tokentype.KwDef:
                self.func_def()
            else:
                self.var_def()
            
            # now we can have zero or more of those
            while self.token.type in [Tokentype.KwDef, Tokentype.Identifier]:
                if self.token.type == Tokentype.KwDef:
                    self.func_def()
                else:
                    self.var_def()

    def func_def(self):
        self.match(Tokentype.kwDef)
        self.match(Tokentype.Identifier)

    def func_body(self):
        ...
    
    def typed_var(self):
        ...
    
    def _type(self):
        ...

    def var_def(self):
        self.typed_var()
        self.match(Tokentype.OpEq)
        self.literal()
        self.match(Tokentype.Newline)

    def stmt(self):
        ...
