from lexer import Lexer, Tokentype, SyntaxErrorException
import astree as ast


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
        node = self.program()
        self.match(Tokentype.EOI)
        return node

    # program ::= [[var def | func def | class def]]* stmt*

    def program(self):
        decl_nodes = []
        stmt_nodes = []
        while self.token.type in [Tokentype.KwDef, Tokentype.KwClass, Tokentype.Identifier]:
            if self.token.type == Tokentype.KwClass:
                decl_nodes.append(self.class_def())
            elif self.token.type == Tokentype.KwDef:
                decl_nodes.append(self.func_def())
            # we need one more lookahead for var_def as stmt can start with ID as well
            # we need to peek if the next token is a colon
            else:
                if self.peek().type == Tokentype.Colon:
                    decl_nodes.append(self.var_def())
                else:
                    break

        while self.token.type != Tokentype.EOI:
            stmt_nodes.append(self.stmt())

        return ast.ProgramNode(decl_nodes, stmt_nodes)

    # class_def ::= class ID ( ID ) : NEWLINE INDENT class_body DEDENT

    def class_def(self):
        self.match(Tokentype.KwClass)

        id_lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        id_node = ast.IdentifierNode(id_lexeme)

        self.match(Tokentype.ParenthesisL)

        super_id_lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        super_id_node = ast.IdentifierNode(super_id_lexeme)

        self.match(Tokentype.ParenthesisR)
        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)

        decl_nodes = self.class_body()

        self.match(Tokentype.Dedent)

        return ast.ClassDefNode(id_node, super_id_node, decl_nodes)

    # class_body ::= pass NEWLINE | [[var_def | func_def]]+

    def class_body(self):
        decl_nodes = []

        if self.match_if(Tokentype.KwPass):
            self.match(Tokentype.Newline)
            return decl_nodes
        else:
            # we must have at least one var_def or func_def
            if self.token.type == Tokentype.KwDef:
                decl_nodes.append(self.func_def())
            else:
                decl_nodes.append(self.var_def())

            # now we can have zero or more of those
            while self.token.type in [Tokentype.KwDef, Tokentype.Identifier]:
                if self.token.type == Tokentype.KwDef:
                    decl_nodes.append(self.func_def())
                else:
                    decl_nodes.append(self.var_def())

        return decl_nodes

    # func_def ::= def ID ( [[typed var [[, typed var]]* ]]? ) [[-> type]]? : NEWLINE INDENT func_body DEDENT

    def func_def(self):
        self.match(Tokentype.KwDef)

        id_lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        id_node = ast.IdentifierNode(id_lexeme)
        self.match(Tokentype.ParenthesisL)

        # [[typed_var [[, typed_var]]* ]]?
        typed_var_nodes = []
        if self.token.type == Tokentype.Identifier:
            typed_var_nodes.append(self.typed_var())
            while self.match_if(Tokentype.Comma):
                typed_var_nodes.append(self.typed_var())

        self.match(Tokentype.ParenthesisR)

        type_node = None
        # [[-> type]]?
        if self.match_if(Tokentype.Arrow):
            type_node = self._type()

        self.match(Tokentype.Colon)
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        decl_nodes, stmt_nodes = self.func_body()

        self.match(Tokentype.Dedent)

        return ast.FuncDefNode(id_node, typed_var_nodes, type_node, decl_nodes, stmt_nodes)

    # func_body requires a stmt at the end, bit weird?
    # func_body ::= [[global_decl | nonlocal_decl | var def | func def]]* stmt+

    def func_body(self):
        decl_nodes = []
        stmt_nodes = []
        while self.token.type in [Tokentype.KwGlobal, Tokentype.KwNonLocal, Tokentype.KwDef, Tokentype.Identifier]:
            if self.token.type == Tokentype.KwGlobal:
                decl_nodes.append(self.global_decl())
            elif self.token.type == Tokentype.KwNonLocal:
                decl_nodes.append(self.nonlocal_decl())
            elif self.token.type == Tokentype.KwDef:
                decl_nodes.append(self.func_def())
            # Identifier
            elif self.peek().type == Tokentype.Colon:
                decl_nodes.append(self.var_def())
            else:
                break

        # need one or more statements
        stmt_nodes.append(self.stmt())
        while self.token.type != Tokentype.Dedent:
            stmt_nodes.append(self.stmt())

        return decl_nodes, stmt_nodes

    # typed_var ::= ID : type

    def typed_var(self):
        id_lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        id_node = ast.IdentifierNode(id_lexeme)

        self.match(Tokentype.Colon)
        type_node = self._type()
        return ast.TypedVarNode(id_node, type_node)

    # type ::= ID | STRING | [ type ]

    def _type(self):
        if self.match_if(Tokentype.BracketL):
            elem_type = self._type()
            self.match(Tokentype.BracketR)
            return ast.ListTypeAnnotationNode(elem_type)
        else:
            lexeme = self.token.lexeme
            if self.match_if(Tokentype.StringLiteral):
                return ast.ClassTypeAnnotationNode(lexeme)
            else:
                self.match(Tokentype.Identifier)
                return ast.ClassTypeAnnotationNode(str(lexeme))

    # global_decl ::= global ID NEWLINE

    def global_decl(self):
        self.match(Tokentype.KwGlobal)

        lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        id_node = ast.IdentifierNode(lexeme)

        self.match(Tokentype.Newline)

        return ast.GlobalDeclNode(id_node)

    # nonlocal_decl ::= nonlocal ID NEWLINE

    def nonlocal_decl(self):
        self.match(Tokentype.KwNonLocal)

        lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        id_node = ast.IdentifierNode(lexeme)

        self.match(Tokentype.Newline)

        return ast.NonLocalDeclNode(id_node)

    # var_def ::= typed_var = literal NEWLINE

    def var_def(self):
        typed_var_node = self.typed_var()
        self.match(Tokentype.OpAssign)
        literal_expr_node = self.literal()
        self.match(Tokentype.Newline)

        return ast.VarDefNode(typed_var_node, literal_expr_node)

    # stmt ::= simple_stmt NEWLINE
    # | if expr : block [[elif expr : block]]* [[else : block]]?
    # | while expr : block
    # | for ID in expr : block

    def stmt(self):
        if self.match_if(Tokentype.KwIf):
            elifs = []
            else_body = []

            cond_node = self.expr()
            self.match(Tokentype.Colon)
            then_body = self.block()

            while self.match_if(Tokentype.KwElif):
                elif_expr = self.expr()
                self.match(Tokentype.Colon)
                elif_body = self.block()
                elifs.append((elif_expr, elif_body))

            if self.match_if(Tokentype.KwElse):
                self.match(Tokentype.Colon)
                else_body = self.block()

            return ast.IfStmtNode(cond_node, then_body, elifs, else_body)

        elif self.match_if(Tokentype.KwWhile):
            cond_node = self.expr()
            self.match(Tokentype.Colon)
            body = self.block()

            return ast.WhileStmtNode(cond_node, body)

        elif self.match_if(Tokentype.KwFor):
            id_lexeme = self.token.lexeme
            self.match(Tokentype.Identifier)
            id_node = ast.IdentifierNode(id_lexeme)

            self.match(Tokentype.OpIn)
            iterable = self.expr()
            self.match(Tokentype.Colon)
            body = self.block()

            return ast.ForStmtNode(id_node, iterable, body)

        else:
            simple_stmt_node = self.simple_stmt()
            self.match(Tokentype.Newline)
            return simple_stmt_node

    def simple_stmt(self):
        if self.match_if(Tokentype.KwPass):
            return ast.PassStmtNode()

        elif self.match_if(Tokentype.KwReturn):
            expr_node = None
            if self.token.type != Tokentype.Newline:
                expr_node = self.expr()
            return ast.ReturnStmtNode(expr_node)
        # now its either target or expr, so we match on expr
        else:
            expr_or_target_node = self.expr()

            # if the next token is an equals sign, it was actually a target
            # fix with AST: target may only be ID, member_expr, index_expr
            if self.match_if(Tokentype.OpAssign):
                # TODO
                # check if prev node was ID, member_expr or index_expr
                if not (isinstance(expr_or_target_node, ast.IdentifierNode)\
                    or isinstance(expr_or_target_node, ast.IdentifierExprNode)\
                    or isinstance(expr_or_target_node, ast.IndexExprNode)\
                    or isinstance(expr_or_target_node, ast.MemberExprNode)):
                    raise SyntaxErrorException("Invalid target", self.token.location)

                targets = []
                targets.append(expr_or_target_node)

                prev = self.expr()
                while self.match_if(Tokentype.OpAssign):
                    if not (isinstance(expr_or_target_node, ast.IdentifierNode)\
                     or isinstance(expr_or_target_node, ast.IdentifierExprNode)\
                     or isinstance(expr_or_target_node, ast.IndexExprNode)\
                     or isinstance(expr_or_target_node, ast.MemberExprNode)):
                        raise SyntaxErrorException("Invalid target", self.token.location)
                    targets.append(prev)
                    prev = self.expr()
                expr_node = prev

                return ast.AssignStmtNode(targets, expr_node)
            else:
                # otherwise it was just an expr and we are done
                return expr_or_target_node

    def block(self):
        self.match(Tokentype.Newline)
        self.match(Tokentype.Indent)
        stmts = []
        stmts.append(self.stmt())
        while not self.match_if(Tokentype.Dedent):
            stmts.append(self.stmt())
        return stmts

    def literal(self):
        lexeme = self.token.lexeme
        if self.match_if(Tokentype.KwNone):
            return ast.NoneLiteralExprNode()
        elif self.match_if(Tokentype.BoolTrueLiteral) or self.match_if(Tokentype.BoolFalseLiteral):
            return ast.BooleanLiteralExprNode(lexeme)
        elif self.match_if(Tokentype.IntegerLiteral):
            return ast.IntegerLiteralExprNode(lexeme)
        else:
            self.match(Tokentype.StringLiteral)
            return ast.StringLiteralExprNode(lexeme)

    # precedence:
    # expr ::=  or_expr if expr else expr | or_expr
    # or_expr ::= or_expr or and_expr | and_expr
    # and_expr ::= and_expr and not_expr | not_expr
    # not_expr ::= not expr | cexpr
    #
    # rewrite in EBNF to remove left-recursion:
    # expr ::= or_expr [if expr else expr]

    def expr(self):
        then_node = self.or_expr() # for if else... its the then node, else just the or node
        if self.match_if(Tokentype.KwIf):
            cond_node = self.expr()
            self.match(Tokentype.KwElse)
            else_node = self.expr()
            return ast.IfExprNode(cond_node, then_node, else_node)
        else:
            return then_node

    # or_expr ::= and_expr {or and_expr}
    def or_expr(self):
        node = self.and_expr()
        while self.match_if(Tokentype.OpOr):
            rhs = self.and_expr()
            node = ast.BinaryOpExprNode(ast.Operator.Or, node, rhs)
        return node

    # and_expr ::= not_expr {and not_expr}
    def and_expr(self):
        node = self.not_expr()
        while self.match_if(Tokentype.OpAnd):
            rhs = self.not_expr()
            node = ast.BinaryOpExprNode(ast.Operator.And, node, rhs)
        return node

    # not_expr ::= not expr | cexpr
    def not_expr(self):
        if self.match_if(Tokentype.OpNot):
            # NOTE: in lab code we wrote "not expr", we think it is incorrect,
            # and changed it with "expr"
            expr_node = self.expr()
            return ast.UnaryOpExprNode(ast.Operator.Not, expr_node)
        else:
            return self.cexpr()

    # cexpr     -> aexpr [ rel_op aexpr ]
    # rel_op    -> == | != | ... | is
    def cexpr(self):
        lhs_node = self.aexpr()
        opmap = {
            Tokentype.OpEq: ast.Operator.Eq,
            Tokentype.OpNotEq: ast.Operator.NotEq,
            Tokentype.OpGt: ast.Operator.Gt,
            Tokentype.OpGtEq: ast.Operator.GtEq,
            Tokentype.OpLt: ast.Operator.Lt,
            Tokentype.OpLtEq: ast.Operator.LtEq,
            Tokentype.OpIs: ast.Operator.Is,
        }
        if self.token.type in opmap.keys():
            op = opmap[self.token.type]
            self.match(self.token.type)
            rhs_node = self.aexpr()
            return ast.BinaryOpExprNode(op, lhs_node, rhs_node)
        else:
            return lhs_node

    # aexpr     -> mexpr { add_op mexpr }
    # add_op    -> + | -
    def aexpr(self):
        node = self.mexpr()
        opmap = {
            Tokentype.OpPlus: ast.Operator.Plus,
            Tokentype.OpMinus: ast.Operator.Minus
        }
        while self.token.type in opmap.keys():
            op = opmap[self.token.type]
            self.match(self.token.type)
            rhs_node = self.mexpr()
            node = ast.BinaryOpExprNode(op, node, rhs_node)

        return node

    # mexpr     -> nexpr { mul_op nexpr }
    # mul_op    -> * | // | %
    def mexpr(self):
        node = self.nexpr()
        opmap = {
            Tokentype.OpMultiply: ast.Operator.Mult,
            Tokentype.OpIntDivide: ast.Operator.IntDivide,
            Tokentype.OpModulus: ast.Operator.Modulus
        }
        while self.token.type in opmap.keys():
            op = opmap[self.token.type]
            self.match(self.token.type)
            rhs_node = self.nexpr()
            node = ast.BinaryOpExprNode(op, node, rhs_node)

        return node

    # nexpr -> - nexpr | mem_or_ind_expr
    def nexpr(self):
        if self.match_if(Tokentype.OpMinus):
            expr_node = self.nexpr()
            return ast.UnaryOpExprNode(ast.Operator.Minus, expr_node)
        else:
            return self.mem_or_ind_expr()

    # mem_or_ind_expr   -> fexpr { . id_or_func | '[' expr ']' }
    def mem_or_ind_expr(self):
        node = self.fexpr()
        while self.token.type in [Tokentype.Period, Tokentype.BracketL]:
            if self.match_if(Tokentype.Period):
                id_node, args = self.member_id_or_func()
                if args is None:
                    node = ast.MemberExprNode(node, id_node)
                else:
                    mem_expr_node = ast.MemberExprNode(node, id_node)
                    node = ast.MethodCallExprNode(mem_expr_node, args)
            else:
                self.match(Tokentype.BracketL)
                index_node = self.expr()
                self.match(Tokentype.BracketR)
                node = ast.IndexExprNode(node, index_node)
        return node

    def member_id_or_func(self):
        lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        id_or_func_node = ast.IdentifierNode(lexeme)
        args = None
        if self.match_if(Tokentype.ParenthesisL):
            args = []
            if not self.match_if(Tokentype.ParenthesisR):
                args.append(self.expr())
                while self.match_if(Tokentype.Comma):
                    args.append(self.expr())
                self.match(Tokentype.ParenthesisR)
            return id_or_func_node, args
        else:
            return id_or_func_node, args

    # id_or_func -> ID [ '(' [expr {, expr } ] ')' ]
    def id_or_func(self, as_identifier=False):
        lexeme = self.token.lexeme
        self.match(Tokentype.Identifier)
        id_or_func_node = ast.IdentifierNode(lexeme)
        if self.match_if(Tokentype.ParenthesisL):
            args = []
            if not self.match_if(Tokentype.ParenthesisR):
                args.append(self.expr())
                while self.match_if(Tokentype.Comma):
                    args.append(self.expr())
                self.match(Tokentype.ParenthesisR)
            return ast.FunctionCallExprNode(id_or_func_node, args)
        else:
            if as_identifier:
                return id_or_func_node
            return ast.IdentifierExprNode(id_or_func_node)

    # fexpr -> [ [[expr {, expr}]]? ]
    #          | ( expr )
    #          | literal
    #          | id_or_func
    def fexpr(self):
        if self.match_if(Tokentype.BracketL):
            list_elems = []
            if not self.match_if(Tokentype.BracketR):
                list_elems.append(self.expr())
                while self.match_if(Tokentype.Comma):
                    list_elems.append(self.expr())
                self.match(Tokentype.BracketR)
            return ast.ListExprNode(list_elems)
        elif self.match_if(Tokentype.ParenthesisL):
            node = self.expr()
            self.match(Tokentype.ParenthesisR)
            return node
        elif self.token.type in [Tokentype.KwNone, Tokentype.BoolTrueLiteral, Tokentype.BoolFalseLiteral, Tokentype.IntegerLiteral, Tokentype.StringLiteral]:
            return self.literal()
        else:
            return self.id_or_func()

    # target ::= ID
    #          | mem_expr
    #          | index_expr
    def target(self):
        lexeme = self.token.lexeme
        if not self.match_if(Tokentype.Identifier):
            return self.mem_or_ind_expr()
        else:
            return ast.IdentifierNode(lexeme)
