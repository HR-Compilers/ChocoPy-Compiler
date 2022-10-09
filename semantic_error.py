#
# Semantic error. Version 1.0
#

class ParserException(Exception):
    pass


class UndefinedIdentifierException(ParserException):
    def __init__(self, name_id, name_scope):
        self.message = f"Undefined identifier '{name_id}' in scope '{name_scope}'."


class RedefinedIdentifierException(ParserException):
    def __init__(self, name_id, name_scope):
        self.message = f"Redefining identifier '{name_id}' in scope '{name_scope}'."


# Invalid declarations with global/nonlocal, e.g. where nonlocal refers to a non-local var in enclosing scope
class DeclarationException(ParserException):
    def __init__(self, name_id, name_scope):
        self.message = f"Wrong global/nonlocal declaration for '{name_id}' in scope '{name_scope}'."


class TypeException(ParserException):
    def __init__(self, type_str_1, type_str_2, name_scope, node):
        self.message = f"Incompatible types'{type_str_1}' and {type_str_2} in scope '{name_scope}' ({node})."
