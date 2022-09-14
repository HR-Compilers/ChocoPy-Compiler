import functools
import ast
import visitor


class PrintVisitor(visitor.Visitor):

    def __init__(self):
        self.indent = 0

    def do_visit(self, node):
        if node:
            self.visit(node)

    def print(self, text):
        for _ in range(self.indent):
            print('   ', sep='', end='')
        print(text)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.IdentifierNode):
        self.print(node.name)

    @visit.register
    def _(self, node: ast.NoneLiteralExprNode):
        self.print('None')

    @visit.register
    def _(self, node: ast.StringLiteralExprNode):
        self.print(node.value)

    @visit.register
    def _(self, node: ast.IntegerLiteralExprNode):
        self.print(node.value)

    @visit.register
    def _(self, node: ast.BooleanLiteralExprNode):
        self.print(node.value)

    @visit.register
    def _(self, node: ast.IdentifierExprNode):
        self.print('expr:')
        self.indent += 1
        self.do_visit(node.identifier)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.BinaryOpExprNode):
        self.print(node.op)
        self.indent += 1
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.UnaryOpExprNode):
        self.print(node.op)
        self.indent += 1
        self.do_visit(node.operand)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.IfExprNode):
        self.print('expr if')
        self.indent += 1
        self.do_visit(node.condition)
        self.do_visit(node.then_expr)
        self.do_visit(node.else_expr)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.IndexExprNode):
        self.print('[]')
        self.indent += 1
        self.do_visit(node.list_expr)
        self.do_visit(node.index)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.MemberExprNode):
        self.print('.')
        self.indent += 1
        self.do_visit(node.expr_object)
        self.do_visit(node.member)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        self.print(node.identifier)
        self.indent += 1
        for a in node.args:
            self.do_visit(a)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.MethodCallExprNode):
        self.print(node.member)
        self.indent += 1
        for a in node.args:
            self.do_visit(a)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ListExprNode):
        self.print('list')
        self.indent += 1
        for e in node.elements:
            self.do_visit(e)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.print('return')
        self.indent += 1
        self.do_visit(node.expr)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.AssignStmtNode):
        self.print('')
        self.indent += 1
        for t in node.targets:
            self.do_visit(t)
        self.do_visit(node.expr)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.IfStmtNode):
        self.print('if')
        self.indent += 1
        self.do_visit(node.condition)
        self.print('then')
        for s in node.then_body:
            self.do_visit(s)
        self.print('else')
        for s in node.else_body:
            self.do_visit(s)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.print('while')
        self.indent += 1
        self.do_visit(node.condition)
        for s in node.body:
            self.do_visit(s)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ForStmtNode):
        self.print('for')
        self.indent += 1
        self.do_visit(node.identifier)
        self.do_visit(node.iterable)
        for s in node.body:
            self.do_visit(s)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ClassTypeAnnotationNode):
        self.print(f'CTA {node.name}')

    @visit.register
    def _(self, node: ast.ListTypeAnnotationNode):
        self.print('LTA')
        self.indent += 1
        self.do_visit(node.elem_type)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.TypedVarNode):
        self.print('TV')
        self.indent += 1
        self.do_visit(node.identifier)
        self.do_visit(node.id_type)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.VarDefNode):
        self.print('VDN')
        self.indent += 1
        self.do_visit(node.var)
        self.do_visit(node.value)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.GlobalDeclNode):
        self.print('global')
        self.indent += 1
        self.do_visit(node.variable)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.NonLocalDeclNode):
        self.print('nonlocal')
        self.indent += 1
        self.do_visit(node.variable)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ClassDefNode):
        self.print('class')
        self.indent += 1
        self.do_visit(node.name)
        self.do_visit(node.super_class)
        for d in node.declarations:
            self.do_visit(d)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.FuncDefNode):
        self.print('func')
        self.indent += 1
        self.do_visit(node.name)
        for p in node.params:
            self.do_visit(p)
        self.do_visit(node.return_type)
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ProgramNode):
        self.print('program')
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
