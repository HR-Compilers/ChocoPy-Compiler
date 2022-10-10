#
# Type env. Version 1.0
#
import symbol_table


class TypeEnvironment:

    @staticmethod
    def is_list_type(t: str):
        """
        Returns True if t is a list-type (excluding <Empty>), otherwise False.
        """
        assert len(t) > 2
        return t[0] == '[' and t[-1] == ']'

    @staticmethod
    def list_elem_type(t: str):
        """
        Returns the element-type of a list-type (e.g., given '[int]', returns 'int').
        """
        assert TypeEnvironment.is_list_type(t)
        return t[1:-1]

    @staticmethod
    def list_type(t: str):
        """
        Returns a list-type of element type t (e.g., given 'int', returns '[int]').
        """
        return '[' + t + ']'

    @staticmethod
    def is_built_in_type(t: str):
        """
        Returns true if t is a built-in type, otherwise false.
        """
        return t in ['bool', 'int', 'str', '<None>', '<Empty>', 'object']

    @staticmethod
    def get_built_in_types():
        """
        Returns a list with the names of all 'built-in' types.
        """
        return ['bool', 'int', 'str', '<None>', '<Empty>', 'object']

    ############################################################################################################

    def __init__(self, sym_table: symbol_table.SymbolTable):
        """
        The constructor. Takes a symbol-table as an argument.
        """
        self.symbol_table = sym_table
        self.scope_symbol_table = self.symbol_table
        self.subtype_of = {}
        # Keep track of the user-defined subtypes.
        for st in self.symbol_table.get_children():
            if st.get_type() == 'class':
                self.subtype_of[st.get_name()] = st.get_super_class()

    def get_symbol_table(self):
        """
        Returns the top symbol_table (passed to the constructor).
        """
        return self.symbol_table

    def get_scope_symbol_table(self):
        """
        Returns the symbol_table of current scope.
        """
        return self.scope_symbol_table

    def enter_scope(self, name: str):
        """
        Enter a new scope, adjust the current symbol-table accordingly.
        """
        for st in self.scope_symbol_table.get_children():
            if st.get_name() == name:
                self.scope_symbol_table = st
                return
        assert False, f"Non-existing name '{name}' in enter_scope call."

    def exit_scope(self):
        """
        Exit the current scope, adjust the current symbol-table accordingly.
        """
        if self.scope_symbol_table is not self.symbol_table:
            self.scope_symbol_table = self.scope_symbol_table.get_parent()
            return
        assert False, "exit_scope called when in top-most (module) scope."

    def get_subtypes(self):
        """
        Returns a dictionary of user-defined types/subtypes.
        """
        return self.subtype_of

    def is_user_defined_type(self, t: str):
        """
        Returns True if t is user-defined type, otherwise False.
        """
        return t in self.subtype_of.keys()

    def get_supertypes_of(self, t):
        """
        Returns a list of all supertypes of type t (in order, the 'least' first).
        """
        if not self.is_valid_typename(t) or t == 'object':
            return []
        sub = []
        while t in self.subtype_of:
            t = self.subtype_of[t]
            if t != 'object':
                sub.append(t)
        sub.append('object')
        return sub

    def is_subtype_of(self, t1: str, t2: str):
        """
        Returns True if t1 is a subtype of t2, otherwise False.
        """
        return t2 in self.get_supertypes_of(t1)

    def is_comp(self, t1: str, t2: str):
        """
        Returns True if t1 and t2 are compatible, otherwise False.
        """
        return t1 == t2 or self.is_subtype_of(t1, t2)

    def is_assign_comp(self, t1: str, t2: str):
        """
        Returns True if t1 and t2 are assignment compatible, otherwise False.
        """
        return self.is_comp(t1, t2) \
            or t1 == '<None>' and t2 not in ['bool', 'int', 'str'] \
            or t1 == '<Empty>' and TypeEnvironment.is_list_type(t2) \
            or (t1 == '[<None>]' and TypeEnvironment.is_list_type(t2)
                and self.is_assign_comp('<None>', TypeEnvironment.list_elem_type(t2)))

    def least_upper_bound(self, t1: str, t2: str):
        """
        Returns the least-upper-bound type for types t1 and t2.
        """
        assert self.is_valid_typename(t1) and self.is_valid_typename(t2)
        if t1 == t2:
            return t1
        sup1 = self.get_supertypes_of(t1)
        sup2 = self.get_supertypes_of(t2)
        for t in sup1:
            if t in sup2:
                return t
        assert False, "Should not happen, as object is a base type for all other types."

    def join(self, t1: str, t2: str):
        """
        Returns the join type for types t1 and t2.
        """

        if self.is_assign_comp(t1, t2):
            return t2
        elif self.is_assign_comp(t2, t1):
            return t1
        else:
            return self.least_upper_bound(t1, t2)

    def is_valid_typename(self, t: str):
        """
        Returns True if t is a valid typename, otherwise False.
        """
        return TypeEnvironment.is_built_in_type(t) \
            or self.is_user_defined_type(t) \
            or TypeEnvironment.is_list_type(t) and self.is_valid_typename(TypeEnvironment.list_elem_type(t))
