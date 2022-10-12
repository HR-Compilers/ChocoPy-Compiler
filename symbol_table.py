#
#  Symbol table. Version 1.06
#
from enum import IntFlag, Enum, auto
from typing import Optional


class DeclType(Enum):
    Variable = auto(),
    Function = auto(),
    Class = auto()


class Symbol:
    """
    An entry in a SymbolTable corresponding to an identifier in the source.
    """

    class Is(IntFlag):
        ReadOnly = 8
        Parameter = 4
        Local = 2
        Global = 1

    def __init__(self, name, flags, type_str=""):
        self._name = name
        self._flags = flags
        self._type_str = type_str

    def __repr__(self):
        return f"<symbol '{self._name}'>"

    def get_name(self):
        """
        Return the symbol’s name.
        """
        return self._name

    def is_parameter(self):
        """
        Return True if the symbol is a parameter.
        """
        return self._flags & Symbol.Is.Parameter != 0

    def is_global(self):
        """
        Return True if the symbol is global.
        """
        return self._flags & Symbol.Is.Global != 0

    def is_local(self):
        """
        Return True if the symbol is local.
        """
        return self._flags & Symbol.Is.Local != 0

    def is_nonlocal(self):
        """
        Return True if the symbol is nonlocal.
        """
        return not self.is_local() and not self.is_global()

    def is_read_only(self):
        """
        Return True if the symbol is read_only (ChocoPy).
        """
        return self._flags & Symbol.Is.ReadOnly != 0

    def get_flags(self):
        return self._flags

    def set_flags(self, flags):
        self._flags = flags

    def get_type_str(self):
        return self._type_str

    def set_type_str(self, type_str):
        self._type_str = type_str


class SymbolTable:

    def __init__(self, name):
        self._name = name
        self._type = 'module'
        self._symbols = {}
        self._parent = None
        self._children = []
        self._is_nested = False

    def get_type(self):
        """
        Return the type of the symbol table. Possible values are 'class', 'module', and 'function'.
        """
        return self._type

    def get_name(self):
        """
        Return the table’s name. This is the name of the class if the table is for a class, the name
        of the function if the table is for a function, or 'top' if the table is global (get_type() returns 'module').
        """
        return self._name

    def is_nested(self):
        """
        Return True if the block is a nested class or function.
        """
        return self._is_nested

    def has_children(self):
        """
        Return True if the block has nested namespaces within it. These can be obtained with get_children().
        """
        return bool(self._children)

    def get_identifiers(self):
        """
        Return a list of names of symbols in this table.
        """
        return self._symbols.keys()

    def lookup(self, name):
        """
        Lookup name in the table and return a Symbol instance.
        """
        return self._symbols.get(name)

    def get_symbols(self):
        """
        Return a list of Symbol instances for names in the table.
        """
        return list(self._symbols.values())

    def get_parent(self):
        """
        Return the parent symbol table (or None if none).
        """
        return self._parent

    def get_children(self):
        """
        Return a list of the nested symbol tables.
        """
        return self._children

    def add_symbol(self, s: Symbol):
        """
        Add a new symbol to the table.
        """
        self._symbols[s.get_name()] = s

    def add_child(self, st):
        """
        Add a new child symbol table
        """
        assert st._parent is None, "Symbol table can only have one parent table."
        st._parent = self
        self._children.append(st)


class Function(SymbolTable):
    """
    A namespace for a function or method. This class inherits SymbolTable.
    """
    def __init__(self, name, is_nested=False):
        super().__init__(name)
        self._type = 'function'
        self._is_nested = is_nested

    def get_parameters(self):
        """
        Return a tuple containing names of parameters to this function.
        """
        return tuple([s.get_name() for s in self.get_symbols() if s.is_parameter()])

    def get_locals(self):
        """
        Return a tuple containing names of locals in this function.
        """
        return tuple([s.get_name() for s in self.get_symbols() if s.is_local()])

    def get_globals(self):
        """
        Return a tuple containing names of globals in this function.
        """
        return tuple([s.get_name() for s in self.get_symbols() if s.is_global()])

    def get_nonlocals(self):
        """
        Return a tuple containing names of non_locals in this function.
        """
        return tuple([s.get_name() for s in self.get_symbols() if s.is_nonlocal()])


class Class(SymbolTable):
    """
    A namespace of a class. This class inherits SymbolTable.
    """
    def __init__(self, name, super_class):
        super().__init__(name)
        self._type = 'class'
        self._super_class = super_class

    def get_super_class(self):
        """
        Return the name of the superclass.
        """
        return self._super_class

    def get_methods(self):
        """
        Return a tuple containing names of methods declared in the class.
        """
        d = {}
        for st in self._children:
            d[st.get_name()] = 1
        return tuple(d)

    def get_methods_sym_table(self, name: str):
        """
        Return the child symbol-table of the given method if it exists, otherwise None.
        """
        for st in self._children:
            if st.get_name() == name:
                return st
        return None


def built_ins(name: str) -> Optional[tuple[str, DeclType]]:
    """
    Returns information about built-in entities.
    """
    built_ins_info = {'print': ("<None>", DeclType.Function),
                      'len': ("int", DeclType.Function),
                      'input': ('str', DeclType.Function),
                      'object': ('object', DeclType.Class)}
    return built_ins_info.get(name, None)


def symbol_decl_type(st: SymbolTable, name: str) -> Optional[DeclType]:
    """
    Returns DeclType.Variable, DeclType.Function, or DeclType.Class depending on what symbol s defines.
    (or None if s is not in the symbol table).
    """
    if name == "count":
        print(name)

    if not st:
        b_in = built_ins(name)
        return b_in[1] if b_in else None
    symbol = st.lookup(name)
    if symbol and symbol.is_local():
        for cst in st.get_children():
            if name == cst.get_name():
                if cst.get_type() == 'function':
                    return DeclType.Function
                elif cst.get_type() == 'class':
                    return DeclType.Class
        return DeclType.Variable
    else:
        return symbol_decl_type(st.get_parent(), name)
