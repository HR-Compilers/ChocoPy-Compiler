#
# ASTree version 1.02
#

from enum import Enum
from typing import Optional


class Operator(Enum):
    Or = 0
    And = 1
    Not = 2
    Eq = 3
    NotEq = 4
    Lt = 5
    Gt = 6
    LtEq = 7
    GtEq = 8
    Is = 9
    Plus = 10
    Minus = 11
    Mult = 12
    IntDivide = 13
    Modulus = 14


class Node:
    pass


class IdentifierNode(Node):

    def __init__(self, name: str):
        self.name = name


#######################################################


class ExprNode:
    pass


class LiteralExprNode(ExprNode):
    pass


class NoneLiteralExprNode(LiteralExprNode):
    pass


class StringLiteralExprNode(LiteralExprNode):

    def __init__(self, value: str):
        self.value = value


class IntegerLiteralExprNode(LiteralExprNode):

    def __init__(self, value: int):
        self.value = value


class BooleanLiteralExprNode(LiteralExprNode):

    def __init__(self, value: bool):
        self.value = value


class IdentifierExprNode(ExprNode):

    def __init__(self, identifier: IdentifierNode):
        self.identifier = identifier


class BinaryOpExprNode(ExprNode):

    def __init__(self, op: Operator, lhs: ExprNode, rhs: ExprNode):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs


class UnaryOpExprNode(ExprNode):

    def __init__(self, op: Operator, operand: ExprNode):
        self.op = op
        self.operand = operand


class IfExprNode(ExprNode):

    def __init__(self, condition: ExprNode, then_expr: ExprNode, else_expr: ExprNode):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr


class IndexExprNode(ExprNode):

    def __init__(self, list_expr: ExprNode, index: ExprNode):
        self.list_expr = list_expr
        self.index = index


class MemberExprNode(ExprNode):

    def __init__(self, expr_object: ExprNode, member: IdentifierNode):
        self.expr_object = expr_object
        self.member = member


class FunctionCallExprNode(ExprNode):

    def __init__(self, identifier: IdentifierNode, args: list[ExprNode]):
        self.identifier = identifier
        self.args = args


class MethodCallExprNode(ExprNode):

    def __init__(self, member: MemberExprNode, args: list[Optional[ExprNode]]):
        self.member = member
        self.args = args


class ListExprNode(ExprNode):

    def __init__(self, elements: list[ExprNode]):
        self.elements = elements


#######################################################


class StmtNode:
    pass


class ExprStmt(StmtNode):

    def __init__(self, expr: ExprNode):
        self.expr = expr


class PassStmtNode(StmtNode):

    def __init__(self):
        pass


class ReturnStmtNode(StmtNode):

    def __init__(self, expr: ExprNode):
        self.expr = expr


class AssignStmtNode(StmtNode):

    def __init__(self, targets: list[ExprNode], expr: ExprNode):
        self.targets = targets
        self.expr = expr


class IfStmtNode(StmtNode):

    def __init__(self, condition: ExprNode, then_body: list[StmtNode],
                 elifs: list[Optional[tuple[ExprNode, StmtNode]]], else_body: list[StmtNode]):
        self.condition = condition
        self.then_body = then_body
        self.elifs = elifs
        self.else_body = else_body


class WhileStmtNode(StmtNode):

    def __init__(self, condition: ExprNode, body: list[StmtNode]):
        self.condition = condition
        self.body = body


class ForStmtNode(StmtNode):

    def __init__(self, identifier: IdentifierNode, iterable: ExprNode, body: list[StmtNode]):
        self.identifier = identifier
        self.iterable = iterable
        self.body = body


#######################################################


class TypeAnnotationNode(Node):
    pass


class ClassTypeAnnotationNode(TypeAnnotationNode):

    def __init__(self, name: str):
        self.name = name


class ListTypeAnnotationNode(TypeAnnotationNode):

    def __init__(self, elem_type: TypeAnnotationNode):
        self.elem_type = elem_type


class TypedVarNode(Node):

    def __init__(self, identifier: IdentifierNode, id_type: TypeAnnotationNode):
        self.identifier = identifier
        self.id_type = id_type


class DeclarationNode(Node):
    pass


class VarDefNode(DeclarationNode):

    def __init__(self, var: TypedVarNode, value: LiteralExprNode):
        self.var = var
        self.value = value


class GlobalDeclNode(DeclarationNode):

    def __init__(self, variable: IdentifierNode):
        self.variable = variable


class NonLocalDeclNode(DeclarationNode):

    def __init__(self, variable: IdentifierNode):
        self.variable = variable


class ClassDefNode(DeclarationNode):

    def __init__(self, name: IdentifierNode, super_class: IdentifierNode, declarations: list[DeclarationNode]):
        self.name = name
        self.super_class = super_class
        self.declarations = declarations


class FuncDefNode(DeclarationNode):

    def __init__(self, name: IdentifierNode, params: list[Optional[TypedVarNode]],
                 return_type: Optional[TypeAnnotationNode], declarations: list[Optional[DeclarationNode]],
                 statements: list[StmtNode]):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.declarations = declarations
        self.statements = statements


class ProgramNode(Node):

    def __init__(self, declarations: list[Optional[DeclarationNode]], statements: list[Optional[StmtNode]]):
        self.declarations = declarations
        self.statements = statements
