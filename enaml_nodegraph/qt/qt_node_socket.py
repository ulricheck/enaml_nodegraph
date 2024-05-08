import logging

from atom.api import Str, Int, Bool, Typed, Float, observe
from enaml.qt import QtCore, QtGui, QtWidgets

from enaml_nodegraph.widgets.node_socket import ProxyNodeSocket, SocketPosition, SocketType

from enaml.qt.q_resource_helpers import (
    get_cached_qcolor, get_cached_qfont, get_cached_qimage
)

from .qt_graphicsitem import QGraphicsItem, QtGraphicsItem
from enaml_nodegraph.primitives import Point2D

log = logging.getLogger(__name__)


class QNodeSocket(QGraphicsItem):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy

    def paint(self, painter, style_option, widget=None):
        self.proxy.on_paint(painter, style_option, widget)

    def boundingRect(self):
        p = self.proxy
        return QtCore.QRectF(
            - p.radius - p.outline_width,
            - p.radius - p.outline_width,
            2 * (p.radius + p.outline_width),
            2 * (p.radius + p.outline_width),
        )

    # @todo: these are expected from toolkitobject - but are not valid for graphics items
    def setObjectName(self, name):
        pass

    def setParent(self, parent):
        pass

    def deleteLater(self):
        log.debug("NodeSocket: deleteLater")


class QtNodeSocket(QtGraphicsItem, ProxyNodeSocket):
    """ A Qt implementation of an Enaml NodeSocket.

    """
    name = Str()
    index = Int(0)
    socket_type = Typed(SocketType)
    socket_position = Typed(SocketPosition)
    socket_spacing = Float(22.0)

    radius = Float(6.0)
    outline_width = Float(1.0)

    show_label = Bool(True)

    relative_position = Typed(Point2D)

    font_label = Typed(QtGui.QFont)

    color_background = Typed(QtGui.QColor)
    color_outline = Typed(QtGui.QColor)
    color_label = Typed(QtGui.QColor)

    pen_outline = Typed(QtGui.QPen)
    pen_label = Typed(QtGui.QPen)

    #: A reference to the widget created by the proxy.
    widget = Typed(QNodeSocket)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QComboBox widget.

        """
        item = QNodeSocket(self)
        self.widget = item

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtNodeSocket, self).init_widget()
        d = self.declaration
        self.set_name(d.name)
        self.set_index(d.index)
        self.set_socket_type(d.socket_type)
        self.set_socket_position(d.socket_position)
        self.set_relative_position(d.compute_socket_position())
        self.set_radius(d.radius)
        self.set_outline_width(d.outline_width)
        self.set_show_label(d.show_label)

        self.set_font_label(d.font_label)

        self.set_color_background(d.color_background)
        self.set_color_outline(d.color_outline)
        self.set_color_label(d.color_label)


    #--------------------------------------------------------------------------
    # observers
    #--------------------------------------------------------------------------
    @observe('outline_width', 'color_outline')
    def _update_outline_style(self, change):
        if self.color_outline is not None:
            self.pen_outline = QtGui.QPen(self.color_outline)
            self.pen_outline.setWidthF(self.outline_width)

    @observe('color_label')
    def _update_label_style(self, change):
        if self.color_label is not None:
            self.pen_label = QtGui.QPen(self.color_label)
            self.pen_label.setWidthF(1)

    def _observe_position(self, change):
        if self.widget is not None:
            self.widget.setPos(QtCore.QPointF(self.relative_position.x, self.relative_position.y))

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    def on_paint(self, painter, style_option, widget=None):
        lod = style_option.levelOfDetailFromTransform(painter.worldTransform())

        # painting circle
        painter.setBrush(self.color_background)
        painter.setPen(self.pen_outline)
        painter.drawEllipse(QtCore.QPointF(-self.radius, -self.radius), 2 * self.radius, 2 * self.radius)

        if self.show_label:
            painter.setFont(self.font_label)
            painter.setPen(self.pen_label)
            is_left = self.socket_position in (SocketPosition.LEFT_BOTTOM, SocketPosition.LEFT_TOP)

            alignment = QtCore.Qt.AlignVCenter
            if is_left:
                alignment |= QtCore.Qt.AlignLeft
            else:
                alignment |= QtCore.Qt.AlignRight

            node = self.parent()
            width = node.width / 2 - self.radius - self.outline_width
            height = self.radius * 2

            offset = 2 * self.radius + self.outline_width
            x = offset if is_left else -width - offset
            y = -self.radius

            rect = QtCore.QRectF(x, y,
                                 width,
                                 height)

            painter.drawText(rect, alignment, self.name)

    #--------------------------------------------------------------------------
    # ProxyNodeSocket API
    #--------------------------------------------------------------------------
    def set_name(self, name):
        self.name = name

    def set_index(self, index):
        self.index = index

    def set_socket_type(self, socket_type):
        self.socket_type = socket_type

    def set_socket_position(self, socket_position):
        self.socket_position = socket_position

    def set_relative_position(self, position):
        self.relative_position = position
        if self.widget is not None:
            self.widget.setPos(QtCore.QPointF(self.relative_position.x, self.relative_position.y))

    def set_radius(self, radius):
        self.radius = radius

    def set_outline_width(self, outline_width):
        self.outline_width = outline_width

    def set_color_background(self, color_background):
        self.color_background = get_cached_qcolor(color_background)

    def set_color_outline(self, color_outline):
        self.color_outline = get_cached_qcolor(color_outline)

    def set_color_label(self, color_label):
        self.color_label = get_cached_qcolor(color_label)

    def set_font_label(self, font):
        if font is not None:
            self.font_label = get_cached_qfont(font)
        else:
            self.font_label = QtGui.QFont("Ubuntu", 8)
        self.font_label.setStyleStrategy(QtGui.QFont.ForceOutline)

    def set_show_label(self, show):
        self.show_label = show
