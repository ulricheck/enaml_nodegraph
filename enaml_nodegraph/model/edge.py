from atom.api import Atom, List, Dict, Int, Str, ForwardInstance, Typed, Instance, observe, IntEnum

def import_socket_type():
    from .socket import Socket
    return Socket

def import_graph_type():
    from .graph import Graph
    return Graph


class EdgeType(IntEnum):
    EDGE_TYPE_DIRECT = 1
    EDGE_TYPE_BEZIER = 2


class Edge(Atom):
    graph = ForwardInstance(import_graph_type)
    start_socket = ForwardInstance(import_socket_type)
    end_socket = ForwardInstance(import_socket_type)

    edge_type = Typed(EdgeType)

    def _default_edge_type(self):
        return EdgeType.EDGE_TYPE_BEZIER

    def _observe_start_socket(self, change):
        if change.get('oldvalue', None) is not None:
            s = change['oldvalue']
            if self in s.edges:
                s.edges.remove(self)
        if change['value'] is not None:
            change['value'].edges.append(self)
            if self.end_socket is not None and change['value'].data_type != self.end_socket.data_type:
                raise TypeError("Incompatible type for connection - %s->%s" % (change['value'].data_type, self.end_socket.data_type))

    def _observe_end_socket(self, change):
        if change.get('oldvalue', None) is not None:
            s = change['oldvalue']
            if self in s.edges:
                s.edges.remove(self)
        if change['value'] is not None:
            change['value'].edges.append(self)
            if self.start_socket is not None and change['value'].data_type != self.start_socket.data_type:
                raise TypeError("Incompatible type for connection - %s->%s" % (self.start_socket.data_type, change['value'].data_type))

    @property
    def data_type(self):
        return getattr(self.start_socket, "data_type", getattr(self.end_socket, "data_type", ""))


    @property
    def is_open(self):
        return self.end_socket is None or self.start_socket is None
