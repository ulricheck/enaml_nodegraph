from atom.api import Atom, List, Dict, Int, Str, ContainerList, ForwardTyped, Instance, observe


class GraphItem(Atom):

    def serialize(self, archive):
        pass

    @staticmethod
    def deserialize(cls, archive):
        return cls()