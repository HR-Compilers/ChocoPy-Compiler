from lexer import Lexer, Tokentype, SyntaxErrorException
import ast

"""
expr ::=  cexpr
        | not expr
        | expr [[and | or]] expr
        | expr if expr else expr

removing left recursion:
expr ::=  cexpr expr' | not expr expr'
expr' ::= [[and | or]] expr expr'
        | if expr else expr expr' 
        | empty

          B1    B2                    B3                B4           B5          B6
cexpr ::= ID | literal | [ [[expr [[, expr]]* ]]? ] | ( expr ) | member_expr | index_expr
                        B7                                     B8                           a1                B9
        | member_expr ( [[expr [[, expr]]* ]]? ) | ID ( [[expr [[, expr]]* ]]? ) | cexpr bin_op cexpr | | - cexpr

removing left recursion:
cexpr ::= B1 cexpr' | ... | B9 cexpr'
cexpr' ::= bin_op cexpr cexpr' | empty

"""

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
        # we need to peek if the next token is a colon
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
        
        while self.token.type != Tokentype.EOI:
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

    # class_body ::= pass NEWLINE | [[var_def | func_def]]+
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

    # func_def ::= def ID ( [[typed var [[, typed var]]* ]]? ) [[-> type]]? : NEWLINE INDENT func_body DEDENT
    def func_def(self):
        self.match(Tokentype.kwDef)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.ParenthesisL)

        # [[typed_var [[, typed_var]]* ]]?
        if self.token.type == Tokentype.Identifier:
            self.typed_var()
            while self.match_if(Tokentype.Comma):
                self.typed_var()
        
        self.match(Tokentype.ParenthesisR)

        # [[-> type]]?
        if self.match_if(Tokentype.Arrow):
            self._type()

        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.func_body()
        self.match(Tokentype.Dedent)
        
    # func_body ::= [[global_decl | nonlocal_decl | var def | func def]]* stmt+
    def func_body(self):
        while self.token.type in [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]:
            if self.token.type == Tokentype.KwGlobal:
                self.global_decl()
            elif self.token.type == Tokentype.KwNonLocal:
                self.nonlocal_decl()
            elif self.token.type == Tokentype.KwDef:
                self.func_def()
            # Identifier
            else:
                if self.peek() == Tokentype.Colon:
                    self.var_def()
                else:
                    # move on to stmt
                    break
        
        # need one or more statements
        self.stmt()
        while self.token.type != Tokentype.Dedent:
            self.stmt()
    
    # typed_var ::= ID : type
    def typed_var(self):
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Colon)
        self._type()
    
    # type ::= ID | IDSTRING | [ type ]
    def _type(self):
        if self.match_if(Tokentype.BracketL):
            self._type()
            self.match(Tokentype.BracketR)
        else:
            self.match(Tokentype.Identifier)

    # global_decl ::= global ID NEWLINE
    def global_decl(self):
        self.match(Tokentype.KwGlobal)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)
    
    # nonlocal_decl ::= nonlocal ID NEWLINE
    def nonlocal_decl(self):
        self.match(Tokentype.KwNonLocal)
        self.match(Tokentype.Identifier)
        self.match(Tokentype.Newline)

    # var_def ::= typed var = literal NEWLINE
    def var_def(self):
        self.typed_var()
        self.match(Tokentype.OpEq)
        self.literal()
        self.match(Tokentype.Newline)

    # stmt ::= simple_stmt NEWLINE
    # | if expr : block [[elif expr : block]]* [[else : block]]?
    # | while expr : block
    # | for ID in expr : block
    def stmt(self):
        if self.match_if(Tokentype.KwIf):
            self.expr()
            self.match(Tokentype.Colon)
            self.block()
            while self.match_if(Tokentype.KwElif):
                self.expr()
                self.match(Tokentype.Colon)
                self.block()
            if self.match_if(Tokentype.KwElse):
                self.match(Tokentype.Colon)
                self.block()

        elif self.match_if(Tokentype.KwWhile):
            self.expr()
            self.match(Tokentype.Colon)
            self.block()

        elif self.match_if(Tokentype.KwFor):
            self.match(Tokentype.Identifier)
            self.match(Tokentype.OpIn)
            self.expr()
            self.match(Tokentype.Colon)
            self.block()

        else:
            self.simple_stmt()
            self.match(Tokentype.Newline)

    # with target: parse as expr, check if you see = after
    # check to make sure that the expr matches target
    # difficult!!
    def simple_stmt(self):
        if self.match_if(Tokentype.KwPass):
            return
        elif self.match_if(Tokentype.KwReturn):
            if self.token.type != Tokentype.Newline:
                self.expr()
        # now its either target or expr, so we match on expr
        else:
            self.expr()
            # if the next token is an equals sign, it was actually a target
            if self.token.type == Tokentype.OpEq:
                # check that the expr also worked as a token
                ...
            # otherwise it was just an expr and we are done
    
    def block(self):
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)

        self.stmt()
        while not self.match_if(Tokentype.Dedent):
            self.stmt()
    
    def literal(self):
        if self.match_if(Tokentype.KwNone):
            return
        elif self.match_if(Tokentype.BoolTrueLiteral):
            return
        elif self.match_if(Tokentype.BoolFalseLiteral):
            return
        elif self.match_if(Tokentype.IntegerLiteral):
            return
        else:
            self.match(Tokentype.StringLiteral)

    # expr ::=  cexpr expr' | not expr expr'
    def expr(self):
        if self.token.type == Tokentype.OpNot:
            self.expr()
            self.expr_m()
        else:
            self.cexpr()
            self.expr_m()

    # expr' ::= [[and | or]] expr expr'
    #          | if expr else expr expr'
    #          | empty
    def expr_m(self):
        if self.token.type == Tokentype.OpAnd:
            self.expr()
            self.expr_m()
        elif self.token.type == Tokentype.OpOr:
            self.expr()
            self.expr_m()
        elif self.match_if(Tokentype.KwIf):
            self.expr()
            self.match(Tokentype.KwElse)
            self.expr()
            self.expr_m()
        else:
            return
    # cexpr ::= ID | literal | [ [[expr [[, expr]]* ]]? ] | ( expr ) | member_expr | index_expr
    #          | member_expr ( [[expr [[, expr]]* ]]? ) | ID ( [[expr [[, expr]]* ]]? ) | cexpr bin_op cexpr | | - cexpr
    #               
    # removing left recursion:
    # cexpr ::= B1 cexpr' | ... | B9 cexpr'
    # cexpr' ::= bin_op cexpr cexpr' | empty  
    def cexpr(self):
        if self.match_if(Tokentype.Identifier):
            if self.match_if(Tokentype.ParenthesisL):
                ...
            else:
                return
        elif self.match_if(Tokentype.BracketL):
            ...
        elif self.match_if(Tokentype.ParenthesisL):
            self.expr()
        elif self.token.type in [Tokentype.KwNone, Tokentype.BoolTrueLiteral, Tokentype.BoolFalseLiteral\
                                ,Tokentype.IntegerLiteral, Tokentype.StringLiteral]:
            self.literal()
        elif self.match_if(Tokentype.OpMinus):
            self.cexpr()

    def cexpr_m(self):
        if self.token.type in [Tokentype.OpPlus, Tokentype.OpMinus, Tokentype.OpMultiply, Tokentype.OpIntDivide\
                              ,Tokentype.OpModulus, Tokentype.OpGt, Tokentype.OpGtEq, Tokentype.OpLt, Tokentype.OpLtEq\
                              ,Tokentype.OpNotEq, Tokentype.OpEq]:
            self.bin_op()
        else:
            return
    
    def bin_op(self):
        ...

    def member_or_index(self):
        self.cexpr()
        if self.token.type

    def member_expr(self):
        ...
    
    def index_expr(self):
        ...

    def target(self):
        ...
    
        
        

