from atom.api import Atom, List, Dict, Int, Str, ContainerList, ForwardTyped, Instance, observe


class Attributes(Atom):
    pass


class GraphItem(Atom):

    attributes = Instance(Attributes)

    def serialize(self, archive):
        pass

    @staticmethod
    def deserialize(cls, archive):
        return cls()