from atom.api import (
    Int, Float, Bool, Unicode, Typed, Str, ContainerList, IntEnum, ForwardTyped, Property, Coerced, observe
)

from enaml.core.declarative import d_
from enaml.colors import ColorMember
from enaml.fonts import FontMember

from .graphicsitem import GraphicsItem, ProxyGraphicsItem
from .edge_item import EdgeItem
from enaml_nodegraph.primitives import Point2D


class SocketType(IntEnum):
    INPUT = 1
    OUTPUT = 2


class SocketPosition(IntEnum):
    LEFT_TOP = 1
    LEFT_BOTTOM = 2
    RIGHT_TOP = 3
    RIGHT_BOTTOM = 4


class ProxyNodeSocket(ProxyGraphicsItem):
    """ The abstract definition of a proxy node-item object.

    """
    #: A reference to the ComboBox declaration.
    declaration = ForwardTyped(lambda: NodeSocket)

    def set_name(self, name):
        raise NotImplementedError

    def set_index(self, index):
        raise NotImplementedError

    def set_socket_type(self, socket_type):
        raise NotImplementedError

    def set_socket_position(self, socket_position):
        raise NotImplementedError

    def set_socket_spacing(self, socket_spacing):
        raise NotImplementedError

    def set_radius(self, radius):
        raise NotImplementedError

    def set_outline_width(self, outline_width):
        raise NotImplementedError

    def set_color_background(self, color_background):
        raise NotImplementedError

    def set_color_outline(self, color_outline):
        raise NotImplementedError


# Guard flags
SOCKET_COMPUTE_HEIGHT_GUARD = 0x1


class NodeSocket(GraphicsItem):
    """ A node-item in a node graph

    """

    id = d_(Str())
    name = d_(Unicode())
    index = d_(Int(0))
    socket_type = d_(Typed(SocketType))
    socket_position = d_(Typed(SocketPosition))
    socket_spacing = d_(Float(22))

    radius = d_(Float(6.0))
    outline_width = d_(Float(1.0))

    font_label = d_(FontMember('10pt Ubuntu'))

    color_label = d_(ColorMember("#AAAAAAFF"))
    color_background = d_(ColorMember("#FF7700FF"))
    color_outline = d_(ColorMember("#000000FF"))

    show_label = d_(Bool(True))

    relative_position = Typed(Point2D)
    edges = ContainerList(EdgeItem)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyNodeSocket)

    absolute_position = Property(lambda self: self.parent.position + self.relative_position, cached=False)

    def _default_name(self):
        return self.id

    #--------------------------------------------------------------------------
    # Content Handlers
    #--------------------------------------------------------------------------

    def destroy(self):
        if self.scene is not None:
            for edge in self.edges[:]:
                self.scene.controller.destroy_edge(edge.id)
        super(NodeSocket, self).destroy()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    @observe('name', 'socket_type', 'relative_position',
             'radius', 'outline_width', 'color_background', 'color_outline')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(NodeSocket, self)._update_proxy(change)
        # @todo: changes need to propagate to the parent ...
        self.request_update()

    @observe('socket_position', 'index', 'socket_spacing')
    def _update_relative_position(self, change):
        if not self._guard & SOCKET_COMPUTE_HEIGHT_GUARD:
            self.update_sockets()

    def _observe_visible(self, change):
        if self.initialized:
            from .node_item import NodeItem
            node = self.parent
            if isinstance(node, NodeItem):
                node.recompute_node_layout()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    def update_sockets(self):
        self.relative_position = self.compute_socket_position()

    def compute_socket_position(self):
        self._guard |= SOCKET_COMPUTE_HEIGHT_GUARD
        result = Point2D(x=0, y=0)
        from .node_item import NodeItem
        node = self.parent
        if isinstance(node, NodeItem):
            x = 0 if (self.socket_position in (SocketPosition.LEFT_TOP, SocketPosition.LEFT_BOTTOM)) else node.width

            if self.socket_position in (SocketPosition.LEFT_BOTTOM, SocketPosition.RIGHT_BOTTOM):
                # start from bottom
                y = node.height - node.edge_size - node.padding - self.index * self.socket_spacing
            else :
                # start from top
                y = node.title_height + node.padding + node.edge_size + self.index * self.socket_spacing

            result = Point2D(x=x, y=y)

        self._guard &= ~SOCKET_COMPUTE_HEIGHT_GUARD
        return result
