#
# Symbol table construction visitor. Version 1.0
# Yours to implement.
#
# I've suggested some member variables to use in the constructor, but you are free to implement
# it differently, as long as the interface does not change.
#

import functools
import astree as ast
import visitor
import symbol_table
from symbol_table import Symbol
import semantic_error


class SymbolTableVisitor(visitor.Visitor):

    def __init__(self):
        # Built-in functions and their return types.
        self.built_ins = {'print': "", 'len': "int", 'input': 'str'}
        self.root_sym_table = None
        self.curr_sym_table = None
        self.parent_sym_table = None

    def is_defined(self, node: ast.IdentifierNode):
        found = False
        curr_lvl = self.curr_sym_table

        # If we have reached the root table, we haven't found it
        while not found and curr_lvl is not None:
            syms = curr_lvl.get_symbols()
            for s in syms:
                # If it exists
                if s.get_name() == node.name:
                    found = True
                    break
            if found: break
            curr_lvl = curr_lvl.get_parent()
        return found


    def do_visit(self, node):
        if node:
            self.visit(node)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.IdentifierNode):
        ...

    @visit.register
    def _(self, node: ast.NoneLiteralExprNode):
        ...

    @visit.register
    def _(self, node: ast.StringLiteralExprNode):
        ...

    @visit.register
    def _(self, node: ast.IntegerLiteralExprNode):
        ...

    @visit.register
    def _(self, node: ast.BooleanLiteralExprNode):
        ...

    # This identifier must already exist
    @visit.register
    def _(self, node: ast.IdentifierExprNode):
        # search scopes for variable - local first, then enclosing, then global
        found = False
        curr_lvl = self.curr_sym_table
        while not found and curr_lvl is not None:
            syms = curr_lvl.get_symbols()
            for s in syms:
                if s.get_name() == node.identifier.name:
                    found = True
                    break
            if found: break
            curr_lvl = curr_lvl.get_parent()

        # If we have reached the root table and found nothing
        # The variable is undefined
        if not found:
            raise semantic_error.UndefinedIdentifierException(node.identifier.name, self.curr_sym_table.get_name())
        self.do_visit(node.identifier)

    @visit.register
    def _(self, node: ast.BinaryOpExprNode):
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)

    @visit.register
    def _(self, node: ast.UnaryOpExprNode):
        self.do_visit(node.operand)

    @visit.register
    def _(self, node: ast.IfExprNode):
        self.do_visit(node.condition)
        self.do_visit(node.then_expr)
        self.do_visit(node.else_expr)

    @visit.register
    def _(self, node: ast.IndexExprNode):
        self.do_visit(node.list_expr)
        self.do_visit(node.index)

    @visit.register
    def _(self, node: ast.MemberExprNode):
        self.do_visit(node.expr_object)
        self.do_visit(node.member)

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        self.do_visit(node.identifier)

        # Add the function identifier to the current symbol table,
        # if not already present
        is_present = False
        local_syms = self.curr_sym_table.get_symbols()
        for lsym in local_syms:
            if lsym.get_name() == node.identifier.name:
                is_present = True
                break
        
        if not is_present:

            # check what type the function returns by finding the identifier

            # First check if its a built-in function: these are global and not local
            if node.identifier.name in self.built_ins:
                s = Symbol(node.identifier.name, Symbol.Is.Global, type_str=self.built_ins[node.identifier.name])

            # Else it must be in a parent symbol table
            else:
                found = False
                curr_lvl = self.curr_sym_table

                # If we have reached the root table,
                # The function does not exist
                while not found and curr_lvl is not self.root_sym_table:
                    curr_lvl = curr_lvl.get_parent()
                    syms = curr_lvl.get_symbols()
                    for s in syms:
                        if s.get_name() == node.identifier.name:
                            found = True
                            type_str = s.get_type_str()
                            break
                    if found: break
                
                if not found:
                    raise semantic_error.UndefinedIdentifierException(node.identifier.name, self.curr_sym_table.get_name())

                global_flag = Symbol.Is.Global if curr_lvl == self.root_sym_table else 0
                s = Symbol(node.identifier.name, global_flag, type_str=type_str)
                
            self.curr_sym_table.add_symbol(s)

        for a in node.args:
            self.do_visit(a)

    @visit.register
    def _(self, node: ast.MethodCallExprNode):
        self.do_visit(node.member)
        for a in node.args:
            self.do_visit(a)

    @visit.register
    def _(self, node: ast.ListExprNode):
        for e in node.elements:
            self.do_visit(e)

    @visit.register
    def _(self, node: ast.PassStmtNode):
        pass

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.do_visit(node.expr)

    # For any assignment, all variables must already be in scope
    @visit.register
    def _(self, node: ast.AssignStmtNode):
        for t in node.targets:
            self.do_visit(t)

        self.do_visit(node.expr)

    @visit.register
    def _(self, node: ast.IfStmtNode):
        self.do_visit(node.condition)
        for s in node.then_body:
            self.do_visit(s)
        for e in node.elifs:
            self.do_visit(e[0])
            for s in e[1]:
                self.do_visit(s)
        for s in node.else_body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.do_visit(node.condition)
        for s in node.body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.ForStmtNode):
        self.do_visit(node.identifier)
        self.do_visit(node.iterable)
        for s in node.body:
            self.do_visit(s)

    @visit.register
    def _(self, node: ast.ClassTypeAnnotationNode):
        pass

    @visit.register
    def _(self, node: ast.ListTypeAnnotationNode):
        self.do_visit(node.elem_type)

    @visit.register
    def _(self, node: ast.TypedVarNode):
        self.do_visit(node.identifier)
        self.do_visit(node.id_type)

    @visit.register
    def _(self, node: ast.VarDefNode):
        # We cannot redefine variables
        if self.is_defined(node.var.identifier):
            raise semantic_error.RedefinedIdentifierException(node.name, self.curr_sym_table.get_name())
        self.do_visit(node.var)
        self.do_visit(node.value)

        global_flag = Symbol.Is.Global if self.curr_sym_table == self.root_sym_table else 0
        s = Symbol(node.var.identifier.name, global_flag + Symbol.Is.Local, str(node.var.id_type))
        self.curr_sym_table.add_symbol(s)


    @visit.register
    def _(self, node: ast.GlobalDeclNode):
        self.do_visit(node.variable)

        # It is illegal for a global declaration to occur at the top level,
        # this is taken care of in the grammar

        # Find the corresponding variable in the global scope
        syms = self.root_sym_table.get_symbols()
        type_str = ""
        found = False
        for sym in syms:
            if sym.get_name() == node.variable.name:
                type_str = sym.get_type_str()
                found = True
                break
        
        # Variable does not exist
        if not found:
            raise semantic_error.UndefinedIdentifierException(node.variable.name, self.curr_sym_table.get_name())

        s = Symbol(node.variable.name, Symbol.Is.Global, type_str=type_str)
        self.curr_sym_table.add_symbol(s)

    
    @visit.register
    def _(self, node: ast.NonLocalDeclNode):
        self.do_visit(node.variable)
        
        # it is illegal for a nonlocal declaration to occur outside a nested function, 
        if not self.curr_sym_table.is_nested():
            raise semantic_error.DeclarationException(node.variable.name, self.curr_sym_table.get_name())

        # Find the corresponding variable in the parent scope
        syms = self.parent_sym_table.get_symbols()
        type_str = ""
        found = False
        for sym in syms:
            if sym.get_name() == node.variable.name:
                # Illegal to refer to a global variable
                if sym.is_global():
                    raise semantic_error.DeclarationException(node.variable.name, self.curr_sym_table.get_name())
                else:
                    type_str = sym.get_type_str()
                    found = True
                    break
        
        # Couldn't find variable in enclosing scope
        if not found:
            raise semantic_error.UndefinedIdentifierException(node.variable.name, self.curr_sym_table.get_name())

        s = Symbol(node.variable.name, 0, type_str=type_str)
        self.curr_sym_table.add_symbol(s)

    @visit.register
    def _(self, node: ast.ClassDefNode):
        # We cannot redefine classes
        if self.is_defined(node.name):
            raise semantic_error.RedefinedIdentifierException(node.name, self.curr_sym_table.get_name())
        self.do_visit(node.name)

        # check if super class is defined
        if not self.is_defined(node.super_class) and node.super_class.name != "object":
            raise semantic_error.UndefinedIdentifierException(node.super_class.name, self.curr_sym_table.get_name())
        self.do_visit(node.super_class)

        self.parent_sym_table = self.curr_sym_table
        self.curr_sym_table = symbol_table.Class(node.name.name)
        self.parent_sym_table.add_child(self.curr_sym_table)

        # We need to add the super class to the symbol table if not already there
        super_exists = False
        par_syms = self.parent_sym_table.get_symbols()
        for ps in par_syms:
            if ps.get_name() == node.super_class.name:
                super_exists = True
                break

        if not super_exists:
            # If the super class is not already in the current symbol table, it's not local
            super_symbol = Symbol(node.super_class.name, Symbol.Is.Global, node.super_class.name)
            self.parent_sym_table.add_symbol(super_symbol)

        for d in node.declarations:
            self.do_visit(d)

        s = Symbol(node.name.name, Symbol.Is.Global + Symbol.Is.Local, node.name.name)
        self.parent_sym_table.add_symbol(s)

        self.curr_sym_table = self.curr_sym_table.get_parent()   


    @visit.register
    def _(self, node: ast.FuncDefNode):
        # We cannot overload / redefine functions
        if self.is_defined(node.name):
            raise semantic_error.RedefinedIdentifierException(node.name, self.curr_sym_table.get_name())
        self.do_visit(node.name)
        is_nested = False
        # if_nested true only if symbol table one level up was function
        if isinstance(self.curr_sym_table, symbol_table.Function): is_nested = True
        
        self.parent_sym_table = self.curr_sym_table
        self.curr_sym_table = symbol_table.Function(node.name.name, is_nested=is_nested)
        self.parent_sym_table.add_child(self.curr_sym_table)

        for p in node.params:
            self.do_visit(p)
            s = Symbol(p.identifier.name, Symbol.Is.Parameter + Symbol.Is.Local, str(p.id_type))
            self.curr_sym_table.add_symbol(s)
        self.do_visit(node.return_type)

        ret_type = ""
        if node.return_type is not None:
            ret_type = str(node.return_type)

        global_flag = Symbol.Is.Global if self.parent_sym_table == self.root_sym_table else 0
        ret_s = Symbol(node.name.name, Symbol.Is.Local + global_flag, ret_type)
        self.parent_sym_table.add_symbol(ret_s)

        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        
        self.curr_sym_table = self.parent_sym_table
        self.parent_sym_table = self.curr_sym_table.get_parent()

    @visit.register
    def _(self, node: ast.ProgramNode):
        self.root_sym_table = symbol_table.SymbolTable('top')
        self.curr_sym_table = self.root_sym_table
        for d in node.declarations:
            self.do_visit(d)
        for s in node.statements:
            self.do_visit(s)
        self.curr_sym_table = self.root_sym_table

    def get_symbol_table(self) -> symbol_table.SymbolTable:
        return self.root_sym_table
