from atom.api import Atom, List, Dict, Int, Str, ForwardTyped, Typed, ForwardInstance, ContainerList, Instance, observe
from enum import IntEnum

from .base import GraphItem
from .edge import Edge


def import_node_type():
    from .node import Node
    return Node


class SocketType(IntEnum):
    INPUT = 1
    OUTPUT = 2


class Socket(GraphItem):
    name = Str()
    index = Int()

    node = ForwardTyped(import_node_type)
    edges = ContainerList(Edge)

    degree = Int(0)
    data_type = Str()
    socket_type = Typed(SocketType)

    def _observe_edges(self, change):
        if self.degree > 0:
            if len(change['value']) > self.degree:
                raise ValueError("Too many links - %s:%s" % (self.node.name, self.name))

    def can_connect(self, edge_or_socket):
        data_types_match = self.data_type == edge_or_socket.data_type
        degree_ok = len(self.edges) < self.degree if self.degree > 0 else True 
        return data_types_match and degree_ok