from atom.api import (Atom, List, Dict, Int, Str, ForwardTyped, Typed, ForwardInstance,
                      ContainerList, Instance, Signal, observe, IntEnum)


from .widgets.graphicsview import GraphicsView


class GraphControllerBase(Atom):

    view = Typed(GraphicsView)

    itemsSelected = Signal()

    def set_view(self, view):
        self.view = view

    def create_node(self, typename, id=None, **kw):
        raise NotImplementedError

    def destroy_node(self, id):
        raise NotImplementedError

    def create_edge(self, typename, id=None, **kw):
        raise NotImplementedError

    def destroy_edge(self, id):
        raise NotImplementedError

    def edge_type_for_start_socket(self, start_node_id, start_socket_id):
        raise NotImplementedError

    def edge_can_connect(self, start_node_id, start_socket_id, end_node_id, end_socket_id):
        return True

    def edge_connected(self, id):
        pass

    def edge_disconnect(self, id):
        pass



