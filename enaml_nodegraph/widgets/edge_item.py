from atom.api import (
    Atom, Int, Float, Unicode, Str, Typed, IntEnum, ForwardTyped, ForwardInstance, observe
)

from enaml.core.declarative import d_
from enaml.colors import ColorMember

from .graphicsitem import GraphicsItem, ProxyGraphicsItem
from enaml_nodegraph.primitives import Point2D


def import_node_socket():
    from .node_socket import NodeSocket
    return NodeSocket


class EdgeType(IntEnum):
    EDGE_TYPE_DIRECT = 1
    EDGE_TYPE_BEZIER = 2


class ProxyEdgeItem(ProxyGraphicsItem):
    """ The abstract definition of a proxy edge-item object.

    """
    #: A reference to the ComboBox declaration.
    declaration = ForwardTyped(lambda: EdgeItem)

    def set_name(self, name):
        raise NotImplementedError

    def set_edge_type(self, edge_type):
        raise NotImplementedError

    def set_line_width(self, line_width):
        raise NotImplementedError

    def set_edge_roundness(self, edge_roundness):
        raise NotImplementedError

    def set_color_default(self, color_default):
        raise NotImplementedError

    def set_color_selected(self, color_selected):
        raise NotImplementedError


class EdgeItem(GraphicsItem):
    """ A edge-item in a node graph

    """

    id = d_(Str())
    name = d_(Unicode())

    edge_type = d_(Typed(EdgeType))
    line_width = d_(Float(2.0))
    edge_roundness = d_(Int(100))

    pos_source = d_(Typed(Point2D))
    pos_destination = d_(Typed(Point2D))

    color_default = d_(ColorMember("#001000FF"))
    color_selected = d_(ColorMember("#00ff00FF"))

    start_socket = ForwardInstance(import_node_socket)
    end_socket = ForwardInstance(import_node_socket)

    #: the model item from the underlying graph structure
    model = d_(Typed(Atom))

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyEdgeItem)

    def _default_id(self):
        if self.scene is not None:
            cls = self.__class__
            return "%s-%00d" % (cls.__name__, self.scene.generate_item_id(cls))
        return "<undefined>"

    def _default_name(self):
        return self.id

    def _default_pos_source(self):
        if self.start_socket is not None:
            return self.start_socket.absolute_position
        return Point2D(x=0, y=0)

    def _default_pos_destination(self):
        if self.end_socket is not None:
            return self.end_socket.absolute_position
        return Point2D(x=0, y=0)

    #--------------------------------------------------------------------------
    # Content Handlers
    #--------------------------------------------------------------------------

    def destroy(self):
        if self.scene is not None and self.scene.controller is not None:
            self.scene.controller.edge_disconnect(self.id)

        if self.start_socket and self in self.start_socket.edges:
            self.start_socket.edges.remove(self)
        if self.end_socket and self in self.end_socket.edges:
            self.end_socket.edges.remove(self)

        super(EdgeItem, self).destroy()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    @observe('name', 'color_default', 'color_selected', 'line_width',
             'edge_type', 'edge_roundness', 'pos_source', 'pos_destination')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(EdgeItem, self)._update_proxy(change)
        self.request_update()

    def _observe_start_socket(self, change):
        new_socket = change['value']
        old_socket = change.get('oldvalue', None)
        if old_socket:
            old_socket.parent.unobserve('position', self.update_pos_source)
        if new_socket:
            self.pos_source = new_socket.parent.position + new_socket.relative_position
            new_socket.parent.observe('position', self.update_pos_source)

    def _observe_end_socket(self, change):
        new_socket = change['value']
        old_socket = change.get('oldvalue', None)
        if old_socket:
            old_socket.parent.unobserve('position', self.update_pos_destination)
        if new_socket:
            self.pos_destination = new_socket.parent.position + new_socket.relative_position
            new_socket.parent.observe('position', self.update_pos_destination)

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------

    def update_pos_source(self, change):
        node_position = change['value']
        if self.start_socket is not None:
            self.pos_source = node_position + self.start_socket.relative_position

    def update_pos_destination(self, change):
        node_position = change['value']
        if self.end_socket is not None:
            self.pos_destination = node_position + self.end_socket.relative_position
