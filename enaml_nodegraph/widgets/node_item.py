from atom.api import (
    Atom, Int, Float, Unicode, Str, Typed, List, Instance, ForwardTyped, observe
)

from enaml.core.declarative import d_
from enaml.colors import ColorMember

from .graphicsitem import GraphicsItem, ProxyGraphicsItem
from .node_content import NodeContent
from .node_socket import NodeSocket, SocketType
from enaml_nodegraph.primitives import Point2D


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

    id = d_(Str())
    name = d_(Unicode())

    width = d_(Int(180))
    height = d_(Int(240))
    position = d_(Typed(Point2D))

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
    input_sockets = List(NodeSocket)
    output_sockets = List(NodeSocket)

    #: the model item from the underlying graph structure
    model = d_(Typed(Atom))

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyNodeItem)

    def _default_position(self):
        return Point2D(x=0, y=0)

    def _default_id(self):
        if self.scene is not None:
            cls = self.__class__
            return "%s-%00d" % (cls.__name__, self.scene.generate_item_id(cls))
        return "<undefined>"

    def _default_name(self):
        return self.id

    #--------------------------------------------------------------------------
    # Content Handlers
    #--------------------------------------------------------------------------

    def child_added(self, child):
        """ Reset the item cache when a child is added """
        super(NodeItem, self).child_added(child)
        if isinstance(child, NodeContent):
            self.content = child
        if isinstance(child, NodeSocket):
            if child.socket_type == SocketType.INPUT:
                self.input_sockets.append(child)
            elif child.socket_type == SocketType.OUTPUT:
                self.output_sockets.append(child)

    def child_removed(self, child):
        """ Reset the item cache when a child is removed """
        super(NodeItem, self).child_removed(child)
        if isinstance(child, NodeContent):
            self.content = None
        if isinstance(child, NodeSocket):
            if child.socket_type == SocketType.INPUT:
                self.input_sockets.remove(child)
            elif child.socket_type == SocketType.OUTPUT:
                self.output_sockets.remove(child)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    @observe('id', 'name', 'width', 'height', 'edge_size', 'title_height',
             'padding', 'color_default', 'color_selected', 'color_title',
             'color_title_background', 'color_background', 'content')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(NodeItem, self)._update_proxy(change)
        self.request_update()

    @observe('width', 'height', 'edge_size', 'title_height', 'padding')
    def _update_layout(self, change):
        for s in self.input_sockets + self.output_sockets:
            s.update_sockets()
        if self.content is not None:
            self.content.update_content_geometry()

    #--------------------------------------------------------------------------
    # NodeItem API
    #--------------------------------------------------------------------------

    # XXX must avoid cyclic updates ..
    def set_position(self, pos):
        self.position = pos
        self.proxy.set_position(pos)