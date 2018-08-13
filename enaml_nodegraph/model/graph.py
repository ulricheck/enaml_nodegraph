from atom.api import Dict, Str, ContainerList

from .base import GraphItem
from .node import Node
from .edge import Edge


class Graph(GraphItem):

    name = Str()

    nodes = ContainerList(Node)
    edges = ContainerList(Edge)

    node_dict = Dict()
    edge_dict = Dict()

    def _observe_nodes(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.graph = self
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].graph = self
            elif change['operation'] == 'remove':
                change['item'].graph = None
        self.node_dict = {v.id: v for v in self.nodes}

    def _observe_edges(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.graph = self
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].graph = self
            elif change['operation'] == 'remove':
                change['item'].graph = None
        self.edge_dict = {v.id: v for v in self.edges}
