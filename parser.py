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
            # fix with node by AST: ID, member_expr, index_expr
            if self.token.type == Tokentype.OpEq:
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

    # precedence:
    # expr ::=  or_expr if expr else expr | or_expr
    # or_expr ::= or_expr or and_expr | and_expr
    # and_expr ::= and_expr and not_expr | not_expr
    # not_expr ::= not expr | cexpr
    #
    # rewrite in EBNF to remove left-recursion:
    # expr ::= or_expr [if expr else expr]
    # or_expr ::= and_expr {or and_expr}
    # and_expr ::= not_expr {and not_expr}
    # not_expr ::= not expr | cexpr
    def expr(self):        
        self.or_expr()
        if self.match_if(Tokentype.KwIf):
            self.expr()
            self.match(Tokentype.KwElse)
            self.expr()

    def or_expr(self):
        self.and_expr()
        while self.token.type == Tokentype.OpOr:
            self.and_expr()
    
    def and_expr(self):
        self.not_expr()
        while self.token.type == Tokentype.OpAnd:
            self.not_expr()
    
    def not_expr(self):
        if self.match_if(Tokentype.OpNot):
            # NOTE: Yngvi-sama in his code wrote "not expr", we think it is incorrect, 
            # and changed it with "expr" 
            self.expr()
        else:
            self.cexpr()
            
    # cexpr     -> aexpr [ rel_op aexpr ]
    # rel_op    -> == | != | ... | is
    def cexpr(self):
        self.aexpr()
        if self.token.type in [Tokentype.OpEq, Tokentype.OpNotEq, Tokentype.OpGt, Tokentype.OpIs\
                              ,Tokentype.OpGtEq,Tokentype.OpLt, Tokentype.OpLtEq]:
            self.aexpr()

    # aexpr     -> mexpr { add_op mexpr }
    # add_op    -> + | -  
    def aexpr(self):
        self.mexpr()
        while self.token.type in [Tokentype.OpPlus, Tokentype.OpMinus]:
            self.mexpr()
    
    # mexpr     -> nexpr { mul_op nexpr }
    # mul_op    -> * | // | %
    def mexpr(self):
        self.nexpr()
        while self.token.type in [Tokentype.OpMultiply, Tokentype.OpIntDivide, Tokentype.OpModulus]:
            self.nexpr()

    # nexpr     -> - nexpr | mi_expr
    def nexpr(self):
        if self.match_if(Tokentype.OpMinus):
            self.nexpr()
        self.mi_expr()
    
    # mi_expr   -> fexpr { . i_or_f | '[' expr ']' }
    def mem_or_ind_expr(self):
        self.fexpr()
        while self.token.type in [Tokentype.Period, Tokentype.BracketL]:
            if self.token.type == Tokentype.Period:
                self.id_or_func()
            else:
                self.expr()
                self.match(Tokentype.BracketR)

    # id_or_func -> ID [ '(' arguments ')' ]
    def id_or_func(self):
        self.match(Tokentype.Identifier)
        if self.match_if(Tokentype.ParenthesisL):
            self.args()
            self.match(Tokentype.ParenthesisR)
    
    # args ::= expr [[, expr]]*
    def args(self):
        self.expr()
        if self.match_if(Tokentype.Comma):
            self.expr()
    
    def fexpr(self):
        ...
    



    def target(self):
        ...