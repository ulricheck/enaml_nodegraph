import math
from atom.api import Typed, Int, Float, Instance, observe
from enaml.qt import QtCore, QtGui, QtWidgets
from enaml.qt.QtGui import QFont, QColor

from enaml.qt.q_resource_helpers import (
    get_cached_qcolor, get_cached_qfont, get_cached_qimage
)

from enaml_nodegraph.primitives import Point2D
from enaml_nodegraph.widgets.edge_item import ProxyEdgeItem, EdgeType
from enaml_nodegraph.widgets.node_socket import NodeSocket, SocketPosition, SocketType

from .qt_graphicsitem import QGraphicsItem, QtGraphicsItem


class QEdgeItem(QGraphicsItem):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy

    def paint(self, painter, style_option, widget=None):
        self.setPath(self.calcPath())

        if self.proxy.end_socket is None:
            painter.setPen(self.proxy.pen_dragging)
        else:
            painter.setPen(self.proxy.pen if not self.isSelected() else self.proxy.pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def shape(self):
        return self.calcPath()

    def calcPath(self):
        raise NotImplementedError

    def boundingRect(self):
        return self.shape().boundingRect()

    # @todo: these are expected from toolkitobject - but are not valid for graphics items
    def setObjectName(self, name):
        pass

    def setParent(self, parent):
        pass

    def deleteLater(self):
        pass


class QDirectEdgeItem(QEdgeItem):

    def calcPath(self):
        path = QtGui.QPainterPath(QtCore.QPointF(self.proxy.pos_source.x, self.proxy.pos_source.y))
        path.lineTo(self.proxy.pos_destination.x, self.proxy.pos_destination.y)
        return path


class QBezierEdgeItem(QEdgeItem):

    def calcPath(self):
        s = self.proxy.pos_source
        d = self.proxy.pos_destination
        dist = (d.x - s.x) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.proxy.start_socket is not None:
            sspos = self.proxy.start_socket.socket_position

            if (s.x > d.x and sspos in (SocketPosition.RIGHT_TOP, SocketPosition.RIGHT_BOTTOM)) \
                    or (s.x < d.x and sspos in (SocketPosition.LEFT_BOTTOM, SocketPosition.LEFT_TOP)):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (
                    (s.y - d.y) / math.fabs(
                        (s.y - d.y) if (s.y - d.y) != 0 else 0.00001
                    )
                ) * self.proxy.edge_roundness
                cpy_s = (
                    (d.y - s.y) / math.fabs(
                        (d.y - s.y) if (d.y - s.y) != 0 else 0.00001
                    )
                ) * self.proxy.edge_roundness

        path = QtGui.QPainterPath(QtCore.QPointF(self.proxy.pos_source.x, self.proxy.pos_source.y))
        path.cubicTo( s.x + cpx_s, s.y + cpy_s, d.x + cpx_d, d.y + cpy_d,
                      self.proxy.pos_destination.x, self.proxy.pos_destination.y)

        return path



class QtEdgeItem(QtGraphicsItem, ProxyEdgeItem):
    """ A Qt implementation of an Enaml EdgeItem.

    """

    line_width = Float(2.0)
    edge_roundness = Int(100)
    edge_type = Typed(EdgeType)

    color_default = Typed(QtGui.QColor)
    color_selected = Typed(QtGui.QColor)

    pos_source = Typed(Point2D)
    pos_destination = Typed(Point2D)

    start_socket = Instance(NodeSocket)
    end_socket = Instance(NodeSocket)

    pen_default = Typed(QtGui.QPen)
    pen_selected = Typed(QtGui.QPen)

    #: A reference to the widget created by the proxy.
    widget = Typed(QEdgeItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QComboBox widget.

        """
        item = QEdgeItem(self)
        self.widget = item

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtEdgeItem, self).init_widget()
        d = self.declaration
        self.set_edge_type(d.edge_type)
        self.set_line_width(d.line_width)
        self.set_edge_roundness(d.edge_roundness)
        self.set_color_default(d.color_default)
        self.set_color_selected(d.color_selected)

        self.widget.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.widget.setZValue(-1)

    #--------------------------------------------------------------------------
    # observers
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # ProxyEdgeItem API
    #--------------------------------------------------------------------------
    def set_name(self, name):
        pass

    def set_edge_type(self, edge_type):
        self.edge_type = edge_type

    def set_line_width(self, line_width):
        self.line_width = line_width

    def set_edge_roundness(self, edge_roundness):
        self.edge_roundness = edge_roundness

    def set_color_default(self, color_default):
        self.color_default = QtGui.QColor.fromRgba(color_default.argb)
        self.pen_default = QtGui.QPen(self.color_default)


        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(2.0)
        self._pen_selected.setWidthF(2.0)
        self._pen_dragging.setWidthF(2.0)



    def set_color_selected(self, color_selected):
        raise NotImplementedError


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
