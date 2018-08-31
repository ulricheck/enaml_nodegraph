from atom.api import Unicode, Property, Str, ContainerList, ForwardTyped

from .socket import Socket, SocketType
from .base import GraphItem


def import_graph_type():
    from .graph import Graph
    return Graph


class Node(GraphItem):
    id = Str()
    name = Unicode()

    graph = ForwardTyped(import_graph_type)

    inputs = ContainerList(Socket)
    outputs = ContainerList(Socket)

    input_dict = Property(lambda self: self._mk_input_dict(), cached=True)
    output_dict = Property(lambda self: self._mk_output_dict(), cached=True)

    def _observe_inputs(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.node = self
                n.socket_type = SocketType.INPUT
                n.index = change['value'].index(n)
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].node = self
                change['item'].socket_type = SocketType.INPUT
                change['item'].index = change['value'].index(n)
            elif change['operation'] == 'remove':
                change['item'].node = None
        self.get_member('input_dict').reset(self)

    def _mk_input_dict(self):
        return {v.name: v for v in self.inputs}

    def _observe_outputs(self, change):
        if change['type'] == 'create':
            for n in change['value']:
                n.node = self
                n.socket_type = SocketType.OUTPUT
                n.index = change['value'].index(n)
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                change['item'].node = self
                change['item'].socket_type = SocketType.OUTPUT
                change['item'].index = change['value'].index(n)
            elif change['operation'] == 'remove':
                change['item'].node = None
        self.get_member('output_dict').reset(self)

    def _mk_output_dict(self):
        return {v.name: v for v in self.outputs}
