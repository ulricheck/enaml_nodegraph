import math

from atom.api import (
    Atom, Bool, Int, Float, Str, Str, Typed, Dict, List, Instance, Event, Property, ForwardTyped, observe
)

from enaml.core.declarative import d_
from enaml.colors import ColorMember
from enaml.fonts import FontMember

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


# Guard flags
NODE_UPDATE_LAYOUT_GUARD = 0x1


class NodeItem(GraphicsItem):
    """ A node-item in a node graph

    """

    id = d_(Str())
    name = d_(Str())

    width = d_(Int(180))
    height = d_(Int())
    position = d_(Typed(Point2D))

    edge_size = d_(Float(10.0))
    title_height = d_(Float(24.0))
    padding = d_(Float(4.0))

    color_default = d_(ColorMember("#0000007F"))
    color_selected = d_(ColorMember("#FFA637FF"))

    font_title = d_(FontMember('10pt Ubuntu'))

    color_title = d_(ColorMember("#AAAAAAFF"))
    color_title_background = d_(ColorMember("#313131FF"))
    color_background = d_(ColorMember("#212121E3"))

    show_content_inline = d_(Bool(False))

    #: the model item from the underlying graph structure
    model = d_(Typed(Atom))

    context_menu_event = d_(Event())

    recompute_node_layout = d_(Event())

    #: optional Node Content
    content = Instance(NodeContent)
    input_sockets = List(NodeSocket)
    output_sockets = List(NodeSocket)

    input_sockets_visible = Property(lambda self: [s for s in self.input_sockets if s.visible], cached=True)
    output_sockets_visible = Property(lambda self: [s for s in self.output_sockets if s.visible], cached=True)

    input_sockets_dict = Property(lambda self: self._mk_input_dict(), cached=True)
    output_sockets_dict = Property(lambda self: self._mk_output_dict(), cached=True)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyNodeItem)

    def _default_position(self):
        return Point2D(x=0, y=0)

    def _default_height(self):
        return self.compute_height()

    def _default_id(self):
        if self.scene is not None:
            cls = self.__class__
            return self.scene.generate_item_id(cls.__name__, cls)
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
                self.get_member('input_sockets_dict').reset(self)
            elif child.socket_type == SocketType.OUTPUT:
                self.output_sockets.append(child)
                self.get_member('output_sockets_dict').reset(self)

    def child_removed(self, child):
        """ Reset the item cache when a child is removed """
        super(NodeItem, self).child_removed(child)
        if isinstance(child, NodeContent):
            self.content = None
        if isinstance(child, NodeSocket):
            if child.socket_type == SocketType.INPUT:
                self.input_sockets.remove(child)
                self.get_member('input_sockets_dict').reset(self)
            elif child.socket_type == SocketType.OUTPUT:
                self.output_sockets.remove(child)
                self.get_member('output_sockets_dict').reset(self)

    def _mk_input_dict(self):
        return {c.id: c for c in self.children if isinstance(c, NodeSocket) and c.socket_type == SocketType.INPUT}

    def _mk_output_dict(self):
        return {c.id: c for c in self.children if isinstance(c, NodeSocket) and c.socket_type == SocketType.OUTPUT}

    def activate_bottom_up(self):
        self.assign_socket_indices()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    @observe('id', 'name', 'width', 'height', 'edge_size', 'title_height',
             'padding', 'color_default', 'color_selected', 'color_title',
             'color_title_background', 'color_background', 'show_content_inline',
             'content')
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

    def _observe_recompute_node_layout(self, change):
        if self.initialized:
            if not self._guard & NODE_UPDATE_LAYOUT_GUARD:
                self.update_node_layout()

    #--------------------------------------------------------------------------
    # NodeItem API
    #--------------------------------------------------------------------------

    def update_node_layout(self):
        self._guard |= NODE_UPDATE_LAYOUT_GUARD
        self.get_member('input_sockets_visible').reset(self)
        self.get_member('output_sockets_visible').reset(self)
        self.assign_socket_indices()
        self.height = self.compute_height()
        self.update_sockets_and_edges()
        self._guard &= ~NODE_UPDATE_LAYOUT_GUARD

    def assign_socket_indices(self):
        for socket in self.input_sockets:
            if socket in self.input_sockets_visible:
                socket.index = self.input_sockets_visible.index(socket)
            else:
                socket.index = 0
        for socket in self.output_sockets:
            if socket in self.output_sockets_visible:
                socket.index = self.output_sockets_visible.index(socket)
            else:
                socket.index = 0

    def update_sockets_and_edges(self):
        for socket in self.input_sockets_visible + self.output_sockets_visible:
            socket.update_sockets()
            for edge in socket.edges:
                edge.update_positions()

    def compute_height(self):
        socket_space = max(sum(s.socket_spacing for s in self.input_sockets_visible),
                           sum(s.socket_spacing for s in self.output_sockets_visible))
        return math.ceil(self.title_height + 2 * self.padding + 2 * self.edge_size + socket_space)


    # XXX must avoid cyclic updates ..
    def set_position(self, pos):
        self.position = pos
        self.proxy.set_position(pos)

    def getContentView(self):
        if not self.show_content_inline and self.content is not None:
            return self.content.content_objects[:]
        return []