from atom.api import Unicode, Int, Typed, Float, observe
from enaml.qt import QtCore, QtGui

from enaml_nodegraph.widgets.node_socket import ProxyNodeSocket, SocketPosition, SocketType

from .qt_graphicsitem import QGraphicsItem, QtGraphicsItem
from .qt_node_item import QtNodeItem


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

    position = Typed(QtCore.QPointF)
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
        self.set_socket_spacing(d.socket_spacing)
        self.set_socket_position(d.socket_position)
        self.set_radius(d.radius)
        self.set_outline_width(d.outline_width)

        self.set_color_background(d.color_background)
        self.set_color_outline(d.color_outline)

        self.widget.setPos(self.position)

    #--------------------------------------------------------------------------
    # observers
    #--------------------------------------------------------------------------
    @observe('outline_width', 'color_outline')
    def _update_style(self, change):
        if self.color_outline is not None:
            self.pen_outline = QtGui.QPen(self.color_outline)
            self.pen_outline.setWidthF(self.outline_width)

    @observe('socket_position', 'index')
    def _update_position(self, change):
        self.position = QtCore.QPointF(*self.compute_socket_position())

    def _observe_position(self, change):
        if self.widget is not None:
            self.widget.setPos(self.position)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    def on_paint(self, painter, style_option, widget=None):
        # painting circle
        painter.setBrush(self.color_background)
        painter.setPen(self.pen_outline)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def compute_socket_position(self):
        node = self.parent()
        if isinstance(node, QtNodeItem):
            x = 0 if (self.socket_position in (SocketPosition.LEFT_TOP, SocketPosition.LEFT_BOTTOM)) else node.width

            if self.socket_position in (SocketPosition.LEFT_BOTTOM, SocketPosition.RIGHT_BOTTOM):
                # start from bottom
                y = node.height - node.edge_size - node.padding - self.index * self.socket_spacing
            else :
                # start from top
                y = node.title_height + node.padding + node.edge_size + self.index * self.socket_spacing

            return [x, y]
        else:
            return [0, 0]


    #--------------------------------------------------------------------------
    # ProxyNodeSocket API
    #--------------------------------------------------------------------------
    def set_name(self, name):
        self.name = name

    def set_index(self, index):
        self.index = index

    def set_socket_type(self, socket_type):
        self.socket_type = socket_type

    def set_socket_spacing(self, socket_spacing):
        self.socket_spacing = socket_spacing

    def set_socket_position(self, socket_position):
        self.socket_position = socket_position

    def set_radius(self, radius):
        self.radius = radius

    def set_outline_width(self, outline_width):
        self.outline_width = outline_width

    def set_color_background(self, color_background):
        self.color_background = QtGui.QColor.fromRgba(color_background.argb)

    def set_color_outline(self, color_outline):
        self.color_outline = QtGui.QColor.fromRgba(color_outline.argb)
