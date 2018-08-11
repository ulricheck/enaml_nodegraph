from atom.api import Atom, List, Dict, Int, Str, ContainerList, ForwardTyped, Instance, observe

from .socket import Socket, SocketType

def import_graph_type():
    from .graph import Graph
    return Graph


class Node(Atom):
    name = Str()

    graph = ForwardTyped(import_graph_type)

    inputs = ContainerList(Socket)
    outputs = ContainerList(Socket)

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

