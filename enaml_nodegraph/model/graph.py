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

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
            self.get_member("node_dict").reset(self)
        else:
            raise ValueError("Node already contained in graph")

    def delete_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            self.get_member("node_dict").reset(self)
        else:
            raise KeyError("Node not contained in graph")

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)
            self.get_member("edge_dict").reset(self)
        else:
            raise ValueError("Edge already contained in graph")

    def delete_edge(self, edge):
        edge.start_socket = None
        edge.end_socket = None
        if edge in self.edges:
            self.edges.remove(edge)
            self.get_member("edge_dict").reset(self)
        else:
            raise KeyError("Edge not contained in graph")
