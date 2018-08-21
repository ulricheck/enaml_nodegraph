#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, IntEnum, Int, Unicode, Coerced, Property, Typed, ForwardTyped, ForwardInstance, Dict, observe
)
from enaml.colors import ColorMember
from enaml.fonts import FontMember
from enaml.core.declarative import d_, d_func
from enaml.styling import Stylable

from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject

from enaml_nodegraph.widgets.graphicsitem import GraphicsItem
from enaml_nodegraph.widgets.node_item import NodeItem
from enaml_nodegraph.widgets.edge_item import EdgeItem


def import_graph_controller_class():
    from enaml_nodegraph.controller import GraphControllerBase
    return GraphControllerBase


class ProxyGraphicsScene(ProxyToolkitObject):
    """ The abstract definition of a proxy GraphicsScene object.

    """
    #: A reference to the Widget declaration.
    declaration = ForwardTyped(lambda: GraphicsScene)

    def set_background(self, background):
        raise NotImplementedError

    def set_font(self, font):
        raise NotImplementedError

    def set_minimum_render_size(self, minimum_size):
        raise NotImplementedError

    def set_tool_tip(self, tool_tip):
        raise NotImplementedError

    def set_status_tip(self, status_tip):
        raise NotImplementedError

    def set_focus(self):
        raise NotImplementedError

    def clear_focus(self):
        raise NotImplementedError

    def has_focus(self):
        raise NotImplementedError

    def add_item(self, item):
        raise NotImplementedError


class SceneGuard(IntEnum):
    NOOP = 0x01
    INITIALIZING = 0x02
    ACTIVATING = 0x04


class Feature(IntEnum):
    """ An IntEnum defining the advanced GraphicsScene features.

    """
    #: Enables support for custom focus traversal functions.
    FocusTraversal = 0x1

    #: Enables support for focus events.
    FocusEvents = 0x2

    #: Enables support for drag operations.
    DragEnabled = 0x4

    #: Enables support for drop operations.
    DropEnabled = 0x8


class GraphicsScene(ToolkitObject, Stylable):
    """ The base class of visible GraphicsScene in Enaml.

    """

    # dimensions
    width = d_(Int(640))
    height = d_(Int(480))

    #: The background color of the widget.
    background = d_(ColorMember())

    #: The font used for the widget.
    font = d_(FontMember())

    #: The minimum render size for the scene.
    minimum_render_size = d_(Int(0))

    #: The tool tip to show when the user hovers over the widget.
    tool_tip = d_(Unicode())

    #: The status tip to show when the user hovers over the widget.
    status_tip = d_(Unicode())

    def _get_items(self):
        return [c for c in self.children if isinstance(c, GraphicsItem)]

    #: Internal item reference
    _items = Property(lambda self: self._get_items(), cached=True)

    #: Set the extra features to enable for this widget. This value must
    #: be provided when the widget is instantiated. Runtime changes to
    #: this value are ignored.
    features = d_(Coerced(Feature.Flags))

    guard = d_(Coerced(SceneGuard.Flags))

    #: Nodegraph Controller
    controller = d_(ForwardInstance(import_graph_controller_class))

    nodes = Dict(Unicode(), NodeItem)
    edges = Dict(Unicode(), EdgeItem)

    #: private dict to generate consecutive ids for item types
    _item_id_generator = Dict()

    #: A reference to the ProxyGraphicsScene object.
    proxy = Typed(ProxyGraphicsScene)

    #--------------------------------------------------------------------------
    # Content Handlers
    #--------------------------------------------------------------------------

    def child_added(self, child):
        """ Reset the item cache when a child is added """
        self.guard = SceneGuard.INITIALIZING
        if isinstance(child, GraphicsItem):
            self.add_item(child)
        super(GraphicsScene, self).child_added(child)
        self.get_member('_items').reset(self)
        self.guard = SceneGuard.NOOP

    def child_removed(self, child):
        """ Reset the item cache when a child is removed """
        self.guard = SceneGuard.INITIALIZING
        super(GraphicsScene, self).child_removed(child)
        self.get_member('_items').reset(self)
        if isinstance(child, GraphicsItem):
            self.delete_item(child)
        self.guard = SceneGuard.NOOP

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('width', 'height', 'background', 'font', 'minimum_render_size',
             'tool_tip', 'status_tip')
    def _update_proxy(self, change):
        """ Update the proxy widget when the Widget data changes.

        This method only updates the proxy when an attribute is updated;
        not when it is created or deleted.

        """
        # The superclass implementation is sufficient.
        super(GraphicsScene, self)._update_proxy(change)
        self.proxy.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def restyle(self):
        """ Restyle the toolkit graphicsscene.

        This method is invoked by the Stylable class when the style
        dependencies have changed for the graphicsscene. This will trigger a
        proxy restyle if necessary. This method should not typically be
        called directly by user code.

        """
        if self.proxy_is_active:
            self.proxy.restyle()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------

    def update(self, *args):
        self.proxy.update(*args)

    def add_item(self, item):
        item.set_scene(self)

        if isinstance(item, NodeItem):
            self.nodes[item.id] = item
        elif isinstance(item, EdgeItem):
            self.edges[item.id] = item

    def delete_item(self, item):
        item.set_scene(None)

        if isinstance(item, NodeItem):
            self.nodes.pop(item.id, None)
        elif isinstance(item, EdgeItem):
            self.edges.pop(item.id, None)

    def clear_all(self):
        for edge in list(self.edges.values())[:]:
            edge.destroy()
        for node in list(self.nodes.values())[:]:
            node.destroy()

    def generate_item_id(self, cls):
        id = self._item_id_generator.get(cls, 0)
        id += 1
        self._item_id_generator[cls] = id
        return id

    def set_focus(self):
        """ Set the keyboard input focus to this widget.

        FOR ADVANCED USE CASES ONLY: DO NOT ABUSE THIS!

        """
        if self.proxy_is_active:
            self.proxy.set_focus()

    def clear_focus(self):
        """ Clear the keyboard input focus from this widget.

        FOR ADVANCED USE CASES ONLY: DO NOT ABUSE THIS!

        """
        if self.proxy_is_active:
            self.proxy.clear_focus()

    def has_focus(self):
        """ Test whether this widget has input focus.

        FOR ADVANCED USE CASES ONLY: DO NOT ABUSE THIS!

        Returns
        -------
        result : bool
            True if this widget has input focus, False otherwise.

        """
        if self.proxy_is_active:
            return self.proxy.has_focus()
        return False

    @d_func
    def focus_gained(self):
        """ A method invoked when the widget gains input focus.

        ** The FocusEvents feature must be enabled for the widget in
        order for this method to be called. **

        """
        pass

    @d_func
    def focus_lost(self):
        """ A method invoked when the widget loses input focus.

        ** The FocusEvents feature must be enabled for the widget in
        order for this method to be called. **

        """
        pass

    @d_func
    def drag_start(self):
        """ A method called at the start of a drag-drop operation.

        This method is called when the user starts a drag operation
        by dragging the widget with the left mouse button. It returns
        the drag data for the drag operation.

        ** The DragEnabled feature must be enabled for the widget in
        order for this method to be called. **

        Returns
        -------
        result : DragData
            An Enaml DragData object which holds the drag data. If
            this is not provided, no drag operation will occur.

        """
        return None

    @d_func
    def drag_end(self, drag_data, result):
        """ A method called at the end of a drag-drop operation.

        This method is called after the user has completed the drop
        operation by releasing the left mouse button. It is passed
        the original drag data object along with the resulting drop
        action of the operation.

        ** The DragEnabled feature must be enabled for the widget in
        order for this method to be called. **

        Parameters
        ----------
        data : DragData
            The drag data created by the `drag_start` method.

        result : DropAction
            The requested drop action when the drop completed.

        """
        pass

    @d_func
    def drag_enter(self, event):
        """ A method invoked when a drag operation enters the widget.

        The widget should inspect the mime data of the event and
        accept the event if it can handle the drop action. The event
        must be accepted in order to receive further drag-drop events.

        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **

        Parameters
        ----------
        event : DropEvent
            The event representing the drag-drop operation.

        """
        pass

    @d_func
    def drag_move(self, event):
        """ A method invoked when a drag operation moves in the widget.

        This method will not normally be implemented, but it can be
        useful for supporting advanced drag-drop interactions.

        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **

        Parameters
        ----------
        event : DropEvent
            The event representing the drag-drop operation.

        """
        pass

    @d_func
    def drag_leave(self):
        """ A method invoked when a drag operation leaves the widget.

        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **

        """
        pass

    @d_func
    def drop(self, event):
        """ A method invoked when the user drops the data on the widget.

        The widget should either accept the proposed action, or set
        the drop action to an appropriate action before accepting the
        event, or set the drop action to DropAction.Ignore and then
        ignore the event.

        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **

        Parameters
        ----------
        event : DropEvent
            The event representing the drag-drop operation.

        """
        pass
