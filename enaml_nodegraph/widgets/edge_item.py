from atom.api import (
    Int, Float, Unicode, Typed, IntEnum, ForwardTyped, observe
)

from enaml.core.declarative import d_
from enaml.colors import ColorMember

from .graphicsitem import GraphicsItem, ProxyGraphicsItem


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

    name = d_(Unicode())

    edge_type = d_(Typed(EdgeType))
    line_width = d_(Float(2.0))
    edge_roundness = d_(Int(100))

    color_default = d_(ColorMember("#001000FF"))
    color_selected = d_(ColorMember("#00ff00FF"))

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyEdgeItem)

    #--------------------------------------------------------------------------
    # Content Handlers
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    @observe('name', 'color_default', 'color_selected', 'line_width',
             'edge_type', 'edge_roundness')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(EdgeItem, self)._update_proxy(change)
        self.request_update()

