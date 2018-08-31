from atom.api import Dict, Str, Property, ContainerList

from .base import GraphItem
from .node import Node
from .edge import Edge


class Graph(GraphItem):

    name = Str()

    nodes = ContainerList(Node)
    edges = ContainerList(Edge)

    node_dict = Property(lambda self: self._mk_node_dict(), cached=True)
    edge_dict = Property(lambda self: self._mk_edge_dict(), cached=True)

    def _observe_nodes(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.graph = self
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].graph = self
            elif change['operation'] == 'remove':
                change['item'].graph = None
        self.get_member("node_dict").reset(self)

    def _mk_node_dict(self):
        return {v.id: v for v in self.nodes}

    def _observe_edges(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.graph = self
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].graph = self
            elif change['operation'] == 'remove':
                change['item'].graph = None
        self.get_member("edge_dict").reset(self)

    def _mk_edge_dict(self):
        return {v.id: v for v in self.edges}
