import abc


class Visitor(abc.ABC):

    @abc.abstractmethod
    def visit(self, node):
        return
