from atom.api import Typed, Int, Float, Instance, observe
from enaml.qt import QtCore, QtGui, QtWidgets
from enaml.qt.QtGui import QFont, QColor

from enaml.qt.q_resource_helpers import (
    get_cached_qcolor, get_cached_qfont, get_cached_qimage
)

from enaml_nodegraph.widgets.node_item import ProxyNodeItem
from enaml_nodegraph.widgets.node_content import NodeContent

from .qt_graphicsitem import QGraphicsItem, QtGraphicsItem
from .qt_node_content import QtNodeContent


class QNodeItem(QGraphicsItem):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy
        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.setFont(QFont("Ubuntu", 10))  # @todo: could be configurable as well.

    def paint(self, painter, style_option, widget=None):
        self.proxy.on_paint(painter, style_option, widget)

    def boundingRect(self):
        return QtCore.QRectF(
            0.,
            0.,
            float(self.proxy.width),
            float(self.proxy.height)
        ).normalized()

    # @todo: these are expected from toolkitobject - but are not valid for graphics items
    def setObjectName(self, name):
        pass

    def setParent(self, parent):
        pass

    def deleteLater(self):
        pass


class QtNodeItem(QtGraphicsItem, ProxyNodeItem):
    """ A Qt implementation of an Enaml NodeItem.

    """

    width = Int(180)
    height = Int(240)

    edge_size = Float(10.0)
    title_height = Float(24.0)
    padding = Float(4.0)

    color_default = Typed(QtGui.QColor)
    color_selected = Typed(QtGui.QColor)
    color_title = Typed(QtGui.QColor)
    color_title_background = Typed(QtGui.QColor)
    color_background = Typed(QtGui.QColor)

    content = Instance(QtNodeContent)

    #: A reference to the widget created by the proxy.
    widget = Typed(QNodeItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QComboBox widget.

        """
        item = QNodeItem(self)
        self.widget = item

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtNodeItem, self).init_widget()
        d = self.declaration
        self.set_width(d.width)
        self.set_height(d.height)
        self.set_edge_size(d.edge_size)
        self.set_title_height(d.title_height)
        self.set_padding(d.padding)

        self.set_content(d.content)

        self.set_name(d.name)
        self.set_color_default(d.color_default)
        self.set_color_selected(d.color_selected)
        self.set_color_title(d.color_title)
        self.set_color_title_background(d.color_title_background)
        self.set_color_background(d.color_background)

        self.widget.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.widget.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

    def activate_bottom_up(self):
        """ Activate the proxy tree for the bottom-up pass.

        """
        super(QtNodeItem, self).activate_bottom_up()
        if self.content is not None and self.content.is_active:
            self.setup_content()

    #--------------------------------------------------------------------------
    # observers
    #--------------------------------------------------------------------------
    @observe('padding', 'width')
    def _update_elements(self, change):
        if change['name'] == 'padding':
            self.widget.title_item.setPos(self.padding, 0)
        self.widget.title_item.setTextWidth(self.width - 2 * self.padding)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    def on_paint(self, painter, style_option, widget=None):

        # title
        path_title = QtGui.QPainterPath()
        path_title.setFillRule(QtCore.Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height,
                                  self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size,
                           self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size,
                           self.edge_size, self.edge_size)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.color_title_background)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QtGui.QPainterPath()
        path_content.setFillRule(QtCore.Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.color_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QtGui.QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self.color_default if not self.widget.isSelected() else self.color_selected)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def setup_content(self):
        self.widget.content_item = self.content.widget

    #--------------------------------------------------------------------------
    # ProxyNodeItem API
    #--------------------------------------------------------------------------
    def set_name(self, name):
        self.widget.title_item.setPlainText(name)

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_edge_size(self, edge_size):
        self.edge_size = edge_size

    def set_title_height(self, title_height):
        self.title_height = title_height

    def set_padding(self, padding):
        self.padding = padding

    def set_color_default(self, color_default):
        self.color_default = QtGui.QColor.fromRgba(color_default.argb)

    def set_color_selected(self, color_selected):
        self.color_selected = QtGui.QColor.fromRgba(color_selected.argb)

    def set_color_title(self, color_title):
        self.widget.title_item.setDefaultTextColor(QtGui.QColor.fromRgba(color_title.argb))

    def set_color_title_background(self, color_title_background):
        self.color_title_background = QtGui.QColor.fromRgba(color_title_background.argb)

    def set_color_background(self, color_background):
        self.color_background = QtGui.QColor.fromRgba(color_background.argb)

    def set_content(self, content):
        if isinstance(content, NodeContent):
            self.content = content.proxy
            if self.content.is_active:
                self.setup_content()
