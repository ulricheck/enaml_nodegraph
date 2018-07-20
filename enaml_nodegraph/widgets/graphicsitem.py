#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, IntEnum, Unicode, Coerced, Typed, ForwardTyped, Event, observe
)

from enaml.core.declarative import d_, d_func

from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject


def import_scene():
    from .graphicsscene import GraphicsScene
    return GraphicsScene


class ProxyGraphicsItem(ProxyToolkitObject):
    """ The abstract definition of a proxy GraphicsItem object.

    """
    #: A reference to the Widget declaration.
    declaration = ForwardTyped(lambda: GraphicsItem)

    def set_enabled(self, enabled):
        raise NotImplementedError

    def set_visible(self, visible):
        raise NotImplementedError

    def set_tool_tip(self, tool_tip):
        raise NotImplementedError

    def set_status_tip(self, status_tip):
        raise NotImplementedError

    def ensure_visible(self):
        raise NotImplementedError

    def ensure_hidden(self):
        raise NotImplementedError

    def set_focus(self):
        raise NotImplementedError

    def clear_focus(self):
        raise NotImplementedError

    def has_focus(self):
        raise NotImplementedError


class Feature(IntEnum):
    """ An IntEnum defining the advanced GraphicsItem features.

    """
    #: Enables support for custom focus traversal functions.
    FocusTraversal = 0x1

    #: Enables support for focus events.
    FocusEvents = 0x2

    #: Enables support for drag operations.
    DragEnabled = 0x4

    #: Enables support for drop operations.
    DropEnabled = 0x8


class GraphicsItem(ToolkitObject):
    """ The base class of visible graphicsitem in Enaml.

    """
    #: Whether or not the widget is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the widget is visible.
    visible = d_(Bool(True))

    #: The tool tip to show when the user hovers over the widget.
    tool_tip = d_(Unicode())

    #: The status tip to show when the user hovers over the widget.
    status_tip = d_(Unicode())

    #: Request a scene redraw
    request_update = Event()

    #: The scene the item is member of
    scene = ForwardTyped(import_scene)

    #: Set the extra features to enable for this widget. This value must
    #: be provided when the widget is instantiated. Runtime changes to
    #: this value are ignored.
    features = d_(Coerced(Feature.Flags))

    #: A reference to the ProxyWidget object.
    proxy = Typed(ProxyGraphicsItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------

    def child_added(self, child):
        """ Reset the item cache when a child is added """
        if isinstance(child, GraphicsItem):
            child.set_scene(self.scene)
        super(GraphicsItem, self).child_added(child)

    def child_removed(self, child):
        """ Reset the item cache when a child is removed """
        super(GraphicsItem, self).child_removed(child)
        if isinstance(child, GraphicsItem):
            child.set_scene(None)

    def activate_top_down(self):
        super(GraphicsItem, self).activate_top_down()
        if isinstance(self.parent, GraphicsItem):
            self.proxy.widget.setParentItem(self.parent.proxy.widget)
        if self.scene is not None:
            scene = self.scene
            scene.proxy.add_item(self.proxy)
            self.observe("request_update", scene.update)
        else:
            self.unobserve("request_update")

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('enabled', 'visible', 'tool_tip', 'status_tip')
    def _update_proxy(self, change):
        """ Update the proxy widget when the Widget data changes.

        This method only updates the proxy when an attribute is updated;
        not when it is created or deleted.

        """
        # The superclass implementation is sufficient.
        super(GraphicsItem, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------

    def set_scene(self, scene):
        self.scene = scene

        for child in self.children:
            if isinstance(child, GraphicsItem):
                child.set_scene(scene)

    def show(self):
        """ Ensure the widget is shown.

        Calling this method will also set the widget visibility to True.

        """
        self.visible = True
        if self.proxy_is_active:
            self.proxy.ensure_visible()

    def hide(self):
        """ Ensure the widget is hidden.

        Calling this method will also set the widget visibility to False.

        """
        self.visible = False
        if self.proxy_is_active:
            self.proxy.ensure_hidden()

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
