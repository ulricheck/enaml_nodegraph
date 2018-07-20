from atom.api import (
    Int, Float, Unicode, Typed, Instance, ForwardTyped, observe
)

from enaml.core.declarative import d_
from enaml.colors import ColorMember

from .graphicsitem import GraphicsItem, ProxyGraphicsItem
from .node_content import NodeContent


class ProxyNodeItem(ProxyGraphicsItem):
    """ The abstract definition of a proxy node-item object.

    """
    #: A reference to the ComboBox declaration.
    declaration = ForwardTyped(lambda: NodeItem)

    def set_name(self, name):
        raise NotImplementedError

    def set_width(self, width):
        raise NotImplementedError

    def set_height(self, height):
        raise NotImplementedError

    def set_edge_size(self, edge_size):
        raise NotImplementedError

    def set_title_height(self, title_height):
        raise NotImplementedError

    def set_padding(self, padding):
        raise NotImplementedError

    def set_color_default(self, color_default):
        raise NotImplementedError

    def set_color_selected(self, color_selected):
        raise NotImplementedError

    def set_color_title(self, color_title):
        raise NotImplementedError

    def set_color_title_background(self, color_title):
        raise NotImplementedError

    def set_color_background(self, color_background):
        raise NotImplementedError

    def set_content(self, content):
        raise NotImplementedError


class NodeItem(GraphicsItem):
    """ A node-item in a node graph

    """

    name = d_(Unicode())

    width = d_(Int(180))
    height = d_(Int(240))

    edge_size = d_(Float(10.0))
    title_height = d_(Float(24.0))
    padding = d_(Float(4.0))

    color_default = d_(ColorMember("#0000007F"))
    color_selected = d_(ColorMember("#FFA637FF"))

    color_title = d_(ColorMember("#AAAAAAFF"))
    color_title_background = d_(ColorMember("#313131FF"))
    color_background = d_(ColorMember("#212121E3"))

    #: optional Node Content
    content = Instance(NodeContent)

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyNodeItem)

    #--------------------------------------------------------------------------
    # Content Handlers
    #--------------------------------------------------------------------------

    def child_added(self, child):
        """ Reset the item cache when a child is added """
        super(NodeItem, self).child_added(child)
        if isinstance(child, NodeContent):
            self.content = child

    def child_removed(self, child):
        """ Reset the item cache when a child is removed """
        super(NodeItem, self).child_removed(child)
        if isinstance(child, NodeContent):
            self.content = None

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    @observe('name', 'width', 'height', 'edge_size', 'title_height',
             'padding', 'color_default', 'color_selected', 'color_title',
             'color_title_background', 'color_background', 'content')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(NodeItem, self)._update_proxy(change)
        self.request_update()

