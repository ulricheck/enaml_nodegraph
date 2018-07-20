from atom.api import (
    Int, Float, Unicode, Typed, IntEnum, ForwardTyped, observe
)

from enaml.core.declarative import d_
from enaml.colors import ColorMember

from .graphicsitem import GraphicsItem, ProxyGraphicsItem


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


class NodeSocket(GraphicsItem):
    """ A node-item in a node graph

    """

    name = d_(Unicode())
    index = d_(Int(0))
    socket_type = d_(Typed(SocketType))
    socket_position = d_(Typed(SocketPosition))
    socket_spacing = d_(Float(22))

    radius = d_(Float(6.0))
    outline_width = d_(Float(1.0))

    color_background = d_(ColorMember("#FF7700FF"))
    color_outline = d_(ColorMember("#000000FF"))

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyNodeSocket)

    #--------------------------------------------------------------------------
    # Content Handlers
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    @observe('name', 'socket_type', 'socket_position',
             'radius', 'outline_width', 'color_background', 'color_outline')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(NodeSocket, self)._update_proxy(change)
        # @todo: changes need to propagate to the parent ...
        self.request_update()

