from atom.api import Unicode, Int, Typed, Float, observe
from enaml.qt import QtCore, QtGui

from enaml_nodegraph.widgets.node_socket import ProxyNodeSocket, SocketPosition, SocketType

from .qt_graphicsitem import QGraphicsItem, QtGraphicsItem
from .qt_node_item import QtNodeItem
from enaml_nodegraph.primitives import Point2D


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
        pass


class QtNodeSocket(QtGraphicsItem, ProxyNodeSocket):
    """ A Qt implementation of an Enaml NodeSocket.

    """
    name = Unicode()
    index = Int(0)
    socket_type = Typed(SocketType)
    socket_position = Typed(SocketPosition)
    socket_spacing = Float(22.0)

    radius = Float(6.0)
    outline_width = Float(1.0)

    relative_position = Typed(Point2D)

    color_background = Typed(QtGui.QColor)
    color_outline = Typed(QtGui.QColor)
    pen_outline = Typed(QtGui.QPen)

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

        self.set_color_background(d.color_background)
        self.set_color_outline(d.color_outline)


    #--------------------------------------------------------------------------
    # observers
    #--------------------------------------------------------------------------
    @observe('outline_width', 'color_outline')
    def _update_style(self, change):
        if self.color_outline is not None:
            self.pen_outline = QtGui.QPen(self.color_outline)
            self.pen_outline.setWidthF(self.outline_width)

    def _observe_position(self, change):
        if self.widget is not None:
            self.widget.setPos(QtCore.QPointF(self.relative_position.x, self.relative_position.y))

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    def on_paint(self, painter, style_option, widget=None):
        # painting circle
        painter.setBrush(self.color_background)
        painter.setPen(self.pen_outline)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

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
        self.color_background = QtGui.QColor.fromRgba(color_background.argb)

    def set_color_outline(self, color_outline):
        self.color_outline = QtGui.QColor.fromRgba(color_outline.argb)
