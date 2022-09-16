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
        print(self.token.type)
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
                if self.peek().type == Tokentype.Colon:
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
        if self.match_if(Tokentype.KwPass):
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
        self.match(Tokentype.KwDef)
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
        self.match(Tokentype.Indent)
        self.func_body()

        # NOTE: Should we have a newline match here?
        self.match(Tokentype.Dedent)
        
    # func_body requires a stmt at the end, bit weird??
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
            elif self.peek().type == Tokentype.Colon:
                self.var_def()

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
        elif not self.match_if(Tokentype.StringLiteral):
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

    # var_def ::= typed_var = literal NEWLINE
    def var_def(self):
        self.typed_var()
        self.match(Tokentype.OpAssign)
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
            if self.match_if(Tokentype.OpAssign):
                # TODO
                self.expr()
            
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
    def expr(self):        
        self.or_expr()
        if self.match_if(Tokentype.KwIf):
            self.expr()
            self.match(Tokentype.KwElse)
            self.expr()

    # or_expr ::= and_expr {or and_expr}
    def or_expr(self):
        self.and_expr()
        while self.match_if(Tokentype.OpOr):
            self.and_expr()

    # and_expr ::= not_expr {and not_expr}
    def and_expr(self):
        self.not_expr()
        while self.match_if(Tokentype.OpAnd):
            self.not_expr()

    # not_expr ::= not expr | cexpr
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
        if self.match_if(Tokentype.OpEq):
            self.aexpr()
        elif self.match_if(Tokentype.OpNotEq):
            self.aexpr()
        elif self.match_if(Tokentype.OpGt):
            self.aexpr()
        elif self.match_if(Tokentype.OpGtEq):
            self.aexpr()
        elif self.match_if(Tokentype.OpLt):
            self.aexpr()
        elif self.match_if(Tokentype.OpLtEq):
            self.aexpr()
        elif self.match_if(Tokentype.OpIs):
            self.aexpr()

    # aexpr     -> mexpr { add_op mexpr }
    # add_op    -> + | -  
    def aexpr(self):
        self.mexpr()
        while self.match_if(Tokentype.OpPlus) or self.match_if(Tokentype.OpMinus):
            self.mexpr()
    
    # mexpr     -> nexpr { mul_op nexpr }
    # mul_op    -> * | // | %
    def mexpr(self):
        self.nexpr()
        while self.match_if(Tokentype.OpMultiply) or self.match_if(Tokentype.OpIntDivide) or self.match_if(Tokentype.OpModulus):
            self.nexpr()

    # nexpr -> - nexpr | mem_or_ind_expr
    def nexpr(self):
        if self.match_if(Tokentype.OpMinus):
            self.nexpr()
        else:
            self.mem_or_ind_expr()
    
    # mem_or_ind_expr   -> fexpr { . id_or_func | '[' expr ']' }
    def mem_or_ind_expr(self):
        self.fexpr()
        while self.token.type in [Tokentype.Period, Tokentype.BracketL]:
            if self.match_if(Tokentype.Period):
                self.id_or_func()
            else:
                self.match(Tokentype.BracketL)
                self.expr()
                self.match(Tokentype.BracketR)

    # id_or_func -> ID [ '(' [expr {, expr } ] ')' ]
    def id_or_func(self):
        self.match(Tokentype.Identifier)
        if self.match_if(Tokentype.ParenthesisL):
            while not self.match_if(Tokentype.ParenthesisR):
                self.expr()
                while self.match_if(Tokentype.Comma):
                    self.expr()

    # fexpr -> [ [[expr {, expr}]] ]
    #          | ( expr )
    #          | literal
    #          | id_or_func
    def fexpr(self):
        if self.match_if(Tokentype.BracketL):
            if not self.match_if(Tokentype.BracketR):
                self.expr()
                while self.match_if(Tokentype.Comma):
                    self.expr()
        elif self.match_if(Tokentype.ParenthesisL):
            self.expr()
            self.match(Tokentype.ParenthesisR)
        elif self.token.type in [Tokentype.KwNone, Tokentype.BoolTrueLiteral, Tokentype.BoolFalseLiteral\
                                ,Tokentype.IntegerLiteral, Tokentype.StringLiteral]:
            self.literal()
        else:
            self.id_or_func()
    
    # target ::= ID
    #          | mem_expr
    #          | index_expr
    def target(self):
        if not self.match_if(Tokentype.Identifier):
            self.mem_or_ind_expr()