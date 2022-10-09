#
# Semantic error. Version 1.1
#

class CompilerException(Exception):
    pass


class UndefinedIdentifierException(CompilerException):
    def __init__(self, name_id, name_scope):
        self.message = f"Undefined identifier '{name_id}' in scope '{name_scope}'."


class RedefinedIdentifierException(CompilerException):
    def __init__(self, name_id, name_scope):
        self.message = f"Redefining identifier '{name_id}' in scope '{name_scope}'."


# Invalid declarations with global/nonlocal, e.g. where nonlocal refers to a non-local var in enclosing scope.
class DeclarationException(CompilerException):
    def __init__(self, name_id, name_scope):
        self.message = f"Wrong global/nonlocal declaration for '{name_id}' in scope '{name_scope}'."


class InvalidUseException(CompilerException):  # E.g., when using a return statement outside a function.
    def __init__(self, text, name_scope, node):
        self.message = f"Invalid use: '{text}' in scope '{name_scope}' ({str(node)})."


class TypeException(CompilerException):
    def __init__(self, type_str_1, type_str_2, name_scope, node):
        self.message = \
            f"TypeError: Incompatible types '{type_str_1}' and '{type_str_2}' in scope '{name_scope}' ({str(node)})."


class AttributeException(CompilerException):
    def __init__(self, type_str, attribute, name_scope, node):
        self.message = \
            f"AttributeError: '{type_str}' has no attribute '{attribute}' in scope '{name_scope}' ({str(node)})."
