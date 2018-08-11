import math
from atom.api import Typed, Int, Float, Unicode, Instance, Property, observe
from enaml.qt import QtCore, QtGui, QtWidgets
from enaml.qt.QtGui import QFont, QColor

from enaml.qt.q_resource_helpers import (
    get_cached_qcolor, get_cached_qfont, get_cached_qimage
)

from enaml_nodegraph.primitives import Point2D
from enaml_nodegraph.widgets.edge_item import ProxyEdgeItem, EdgeType
from enaml_nodegraph.widgets.node_socket import SocketPosition

from .qt_graphicsitem import QGraphicsPathItem, QtGraphicsItem


class QEdgeItem(QGraphicsPathItem):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy

    def paint(self, painter, style_option, widget=None):
        self.setPath(self.calcPath())

        if self.proxy.end_socket is None:
            painter.setPen(self.proxy.pen_dragging)
        else:
            painter.setPen(self.proxy.pen_default if not self.isSelected() else self.proxy.pen_selected)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(self.path())

    def shape(self):
        return self.calcPath()

    def calcPath(self):
        edge_type = self.proxy.edge_type
        if edge_type == EdgeType.EDGE_TYPE_DIRECT:
            path = QtGui.QPainterPath(QtCore.QPointF(self.proxy.pos_source.x, self.proxy.pos_source.y))
            path.lineTo(self.proxy.pos_destination.x, self.proxy.pos_destination.y)
            return path

        elif edge_type == EdgeType.EDGE_TYPE_BEZIER:
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
            path.cubicTo(s.x + cpx_s, s.y + cpy_s, d.x + cpx_d, d.y + cpy_d,
                         self.proxy.pos_destination.x, self.proxy.pos_destination.y)

            return path

    def boundingRect(self):
        return self.shape().boundingRect()

    # @todo: these are expected from toolkitobject - but are not valid for graphics items
    def setObjectName(self, name):
        pass

    def setParent(self, parent):
        pass

    def deleteLater(self):
        pass


class QtEdgeItem(QtGraphicsItem, ProxyEdgeItem):
    """ A Qt implementation of an Enaml EdgeItem.

    """
    name = Unicode()

    line_width = Float(2.0)
    edge_roundness = Int(100)
    edge_type = Typed(EdgeType)

    color_default = Typed(QtGui.QColor)
    color_selected = Typed(QtGui.QColor)

    pos_source = Typed(Point2D)
    pos_destination = Typed(Point2D)

    pen_default = Typed(QtGui.QPen)
    pen_selected = Typed(QtGui.QPen)
    pen_dragging = Typed(QtGui.QPen)

    start_socket = Property(lambda self: self.declaration.start_socket if self.declaration is not None else None, cached=False)
    end_socket = Property(lambda self: self.declaration.end_socket if self.declaration is not None else None, cached=False)

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

        self.set_pos_source(d.pos_source)
        self.set_pos_destination(d.pos_destination)

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
        self.name = name

    def set_edge_type(self, edge_type):
        self.edge_type = edge_type

    def set_line_width(self, line_width):
        self.line_width = line_width

    def set_edge_roundness(self, edge_roundness):
        self.edge_roundness = edge_roundness

    def set_color_default(self, color_default):
        self.color_default = QtGui.QColor.fromRgba(color_default.argb)
        self.pen_default = QtGui.QPen(self.color_default)
        self.pen_default.setWidthF(self.line_width)

        self.pen_dragging = QtGui.QPen(self.color_default)
        self.pen_dragging.setStyle(QtCore.Qt.DashLine)
        self.pen_dragging.setWidthF(self.line_width)

    def set_color_selected(self, color_selected):
        self.color_selected = QtGui.QColor.fromRgba(color_selected.argb)
        self.pen_selected = QtGui.QPen(self.color_selected)
        self.pen_selected.setWidthF(2.0)

    def set_pos_source(self, pos):
        self.pos_source = pos

    def set_pos_destination(self, pos):
        self.pos_destination = pos
