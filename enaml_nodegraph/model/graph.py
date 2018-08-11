from atom.api import Atom, List, Dict, Int, Str, ContainerList, ForwardTyped, Instance, observe

from .node import Node
from .edge import Edge


class Graph(Atom):

    name = Str()

    nodes = ContainerList(Node)
    edges = ContainerList(Edge)

    def _observe_nodes(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.graph = self
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].graph = self
            elif change['operation'] == 'remove':
                change['item'].graph = None

    def _observe_edges(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.graph = self
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].graph = self
            elif change['operation'] == 'remove':
                change['item'].graph = None
