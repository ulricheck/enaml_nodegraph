#------------------------------------------------------------------------------
# Copyright (c) 2014-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Coerced

from enaml.drag_drop import DropAction
from enaml_nodegraph.widgets.graphicsitem import Feature, ProxyGraphicsItem

from enaml.qt.QtCore import Qt, QPoint
from enaml.qt.QtGui import QDrag, QCursor
from enaml.qt.QtWidgets import QGraphicsItem, QGraphicsPathItem, QApplication

from enaml.qt import focus_registry
from enaml.qt.qt_drag_drop import QtDropEvent
from enaml.qt.qt_toolkit_object import QtToolkitObject


class QtGraphicsItem(QtToolkitObject, ProxyGraphicsItem):
    """ A Qt implementation of an Enaml ProxyGraphicsItem.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QGraphicsItem)

    #: A private copy of the declaration features. This ensures that
    #: feature cleanup will proceed correctly in the event that user
    #: code modifies the declaration features value at runtime.
    _features = Coerced(Feature.Flags)

    #: Internal storage for the drag origin position.
    _drag_origin = Typed(QPoint)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QGraphicsItem object.

        """
        self.widget = QGraphicsItem(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying QGraphicsItem object.

        """
        super(QtGraphicsItem, self).init_widget()
        widget = self.widget
        focus_registry.register(widget, self)
        self._setup_features()
        d = self.declaration
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        if not d.enabled:
            self.set_enabled(d.enabled)
        # Don't make toplevel widgets visible during init or they will
        # flicker onto the screen. This applies particularly for things
        # like status bar widgets which are created with no parent and
        # then reparented by the status bar. Real top-level widgets must
        # be explicitly shown by calling their .show() method after they
        # are created.
        if widget.parentWidget() or not d.visible:
            self.set_visible(d.visible)

    def destroy(self):
        """ Destroy the underlying QtGraphicsItem object.

        """
        if self.widget is not None and self.widget.scene() is not None:
            self.widget.scene().removeItem(self.widget)
        self._teardown_features()
        focus_registry.unregister(self.widget)
        super(QtGraphicsItem, self).destroy()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _setup_features(self):
        """ Setup the advanced widget feature handlers.

        """
        features = self._features = self.declaration.features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.hook_focus_traversal()
        if features & Feature.FocusEvents:
            self.hook_focus_events()
        if features & Feature.DragEnabled:
            self.hook_drag()
        if features & Feature.DropEnabled:
            self.hook_drop()

    def _teardown_features(self):
        """ Teardowns the advanced widget feature handlers.

        """
        features = self._features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.unhook_focus_traversal()
        if features & Feature.FocusEvents:
            self.unhook_focus_events()
        if features & Feature.DragEnabled:
            self.unhook_drag()
        if features & Feature.DropEnabled:
            self.unhook_drop()

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------

    def tab_focus_request(self, reason):
        """ Handle a custom tab focus request.

        This method is called when focus is being set on the proxy
        as a result of a user-implemented focus traversal handler.
        This can be reimplemented by subclasses as needed.

        Parameters
        ----------
        reason : Qt.FocusReason
            The reason value for the focus request.

        Returns
        -------
        result : bool
            True if focus was set, False otherwise.

        """
        widget = self.focus_target()
        if not widget.flags() & QGraphicsItem.ItemIsFocusable:
            return False
        if not widget.isEnabled():
            return False
        if not widget.isVisible():
            return False
        widget.setFocus(reason)
        return False

    def focus_target(self):
        """ Return the current focus target for a focus request.

        This can be reimplemented by subclasses as needed. The default
        implementation of this method returns the current proxy widget.

        """
        return self.widget

    def hook_focus_events(self):
        """ Install the hooks for focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        widget.focusInEvent = self.focusInEvent
        widget.focusOutEvent = self.focusOutEvent

    def unhook_focus_events(self):
        """ Remove the hooks for the focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        del widget.focusInEvent
        del widget.focusOutEvent

    def focusInEvent(self, event):
        """ The default 'focusInEvent' implementation.

        """
        widget = self.widget
        type(widget).focusInEvent(widget, event)
        self.declaration.focus_gained()

    def focusOutEvent(self, event):
        """ The default 'focusOutEvent' implementation.

        """
        widget = self.widget
        type(widget).focusOutEvent(widget, event)
        self.declaration.focus_lost()

    def hook_drag(self):
        """ Install the hooks for drag operations.

        """
        widget = self.widget
        widget.mousePressEvent = self.mousePressEvent
        widget.mouseMoveEvent = self.mouseMoveEvent
        widget.mouseReleaseEvent = self.mouseReleaseEvent

    def unhook_drag(self):
        """ Remove the hooks for drag operations.

        """
        widget = self.widget
        del widget.mousePressEvent
        del widget.mouseMoveEvent
        del widget.mouseReleaseEvent

    def mousePressEvent(self, event):
        """ Handle the mouse press event for a drag operation.

        """
        if event.button() == Qt.LeftButton:
            self._drag_origin = event.pos()
        widget = self.widget
        type(widget).mousePressEvent(widget, event)

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for a drag operation.

        """
        if event.buttons() & Qt.LeftButton and self._drag_origin is not None:
            dist = (event.pos() - self._drag_origin).manhattanLength()
            if dist >= QApplication.startDragDistance():
                self.do_drag()
                self._drag_origin = None
                return
        widget = self.widget
        type(widget).mouseMoveEvent(widget, event)

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the drag operation.

        """
        if event.button() == Qt.LeftButton:
            self._drag_origin = None
        widget = self.widget
        type(widget).mouseReleaseEvent(widget, event)

    def hook_drop(self):
        """ Install hooks for drop operations.

        """
        widget = self.widget
        widget.setAcceptDrops(True)
        widget.dragEnterEvent = self.dragEnterEvent
        widget.dragMoveEvent = self.dragMoveEvent
        widget.dragLeaveEvent = self.dragLeaveEvent
        widget.dropEvent = self.dropEvent

    def unhook_drop(self):
        """ Remove hooks for drop operations.

        """
        widget = self.widget
        widget.setAcceptDrops(False)
        del widget.dragEnterEvent
        del widget.dragMoveEvent
        del widget.dragLeaveEvent
        del widget.dropEvent

    def do_drag(self):
        """ Perform the drag operation for the widget.

        """
        drag_data = self.declaration.drag_start()
        if drag_data is None:
            return
        widget = self.widget
        qdrag = QDrag(widget)
        qdrag.setMimeData(drag_data.mime_data.q_data())
        # if drag_data.image is not None:
        #     qimg = get_cached_qimage(drag_data.image)
        #     qdrag.setPixmap(QPixmap.fromImage(qimg))
        # else:
        #     if __version_info__ < (5, ):
        #         qdrag.setPixmap(QPixmap.grabWidget(widget))
        #     else:
        #         qdrag.setPixmap(widget.grab())
        if drag_data.hotspot:
            qdrag.setHotSpot(QPoint(*drag_data.hotspot))
        else:
            cursor_position = widget.mapFromScene(QCursor.pos())
            qdrag.setHotSpot(cursor_position)
        default = Qt.DropAction(drag_data.default_drop_action)
        supported = Qt.DropActions(drag_data.supported_actions)
        qresult = qdrag.exec_(supported, default)
        self.declaration.drag_end(drag_data, DropAction(int(qresult)))

    def dragEnterEvent(self, event):
        """ Handle the drag enter event for the widget.

        """
        self.declaration.drag_enter(QtDropEvent(event))

    def dragMoveEvent(self, event):
        """ Handle the drag move event for the widget.

        """
        self.declaration.drag_move(QtDropEvent(event))

    def dragLeaveEvent(self, event):
        """ Handle the drag leave event for the widget.

        """
        self.declaration.drag_leave()

    def dropEvent(self, event):
        """ Handle the drop event for the widget.

        """
        self.declaration.drop(QtDropEvent(event))

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # ProxyGraphicsItem API
    #--------------------------------------------------------------------------

    def set_enabled(self, enabled):
        """ Set the enabled state of the widget.

        """
        self.widget.setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visibility of the widget.

        """
        self.widget.setVisible(visible)

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip for the widget.

        """
        self.widget.setToolTip(tool_tip)

    def set_status_tip(self, status_tip):
        """ Set the status tip for the widget.

        """
        self.widget.setStatusTip(status_tip)

    def ensure_visible(self):
        """ Ensure the widget is visible.

        """
        self.widget.setVisible(True)

    def ensure_hidden(self):
        """ Ensure the widget is hidden.

        """
        self.widget.setVisible(False)

    def set_focus(self):
        """ Set the keyboard input focus to this widget.

        """
        self.focus_target().setFocus(Qt.OtherFocusReason)

    def clear_focus(self):
        """ Clear the keyboard input focus from this widget.

        """
        self.focus_target().clearFocus()

    def has_focus(self):
        """ Test whether this widget has input focus.

        """
        return self.focus_target().hasFocus()
