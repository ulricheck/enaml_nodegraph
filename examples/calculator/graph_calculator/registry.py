from atom.api import (Atom, AtomMeta, Str, Str, ContainerList, Dict, Typed)


class TypeElement(Atom):
    id = Str()
    name = Str()
    widget_class = Typed(AtomMeta)
    model_class = Typed(AtomMeta)


class NodeType(TypeElement):
    editor_class = Typed(AtomMeta)


class EdgeType(TypeElement):
    pass


class TypeRegistry(Atom):
    node_types = ContainerList(NodeType)
    edge_types = ContainerList(EdgeType)

    node_type_name_map = Dict()
    edge_type_name_map = Dict()

    def _observe_node_types(self, change):
        self.node_type_name_map = {v.id: v for v in self.node_types}

    def _observe_edge_types(self, change):
        self.edge_type_name_map = {v.id: v for v in self.edge_types}

    def register_node_type(self, node_type):
        self.node_types.append(node_type)

    def register_edge_type(self, edge_type):
        self.edge_types.append(edge_type)

