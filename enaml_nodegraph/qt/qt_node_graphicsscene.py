__author__ = 'jack'
import math

from enaml.qt import QtCore, QtGui, QtWidgets
from atom.api import Typed, Int, Bool, observe
from enaml.colors import ColorMember

from enaml_nodegraph.widgets.node_graphicsscene import ProxyNodeGraphicsScene
from enaml_nodegraph.qt.qt_graphicsscene import QtGraphicsScene


class QGraphicsScene(QtWidgets.QGraphicsScene):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy

    def boundingRect(self):
        return self.proxy.boundingRect()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        self.proxy.on_draw_background(painter, rect)


class QtNodeGraphicsScene(QtGraphicsScene, ProxyNodeGraphicsScene):
    """ A Qt implementation of an Enaml ProxyNodeGraphicsScene widget.

    """

    #: A reference to the widget created by the proxy.
    widget = Typed(QGraphicsScene)

    # Background style
    show_background = Bool(True)

    background_grid_size = Int(20)
    background_grid_squares = Int(5)

    # color scheme
    color_light = ColorMember("#2f2f2f")
    color_dark = ColorMember("#292929")

    pen_light = Typed(QtGui.QPen)
    pen_dark = Typed(QtGui.QPen)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)


    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying html widget.

        """
        widget = QGraphicsScene(self, self.parent_widget(),)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underlying widget.
        """
        super(QtNodeGraphicsScene, self).init_widget()
        d = self.declaration
        self.pen_light = QtGui.QPen(QtGui.QColor.fromRgba(d.color_light.argb))
        self.pen_light.setWidth(1)
        self.pen_dark = QtGui.QPen(QtGui.QColor.fromRgba(d.color_dark.argb))
        self.pen_dark.setWidth(2)

        self.show_background = d.show_background
        self.background_grid_size = d.background_grid_size
        self.background_grid_squares = d.background_grid_squares
        self.color_light = d.color_light
        self.color_dark = d.color_dark


    #--------------------------------------------------------------------------
    # QGraphicsScene callbacks
    #--------------------------------------------------------------------------
    def on_draw_background(self, painter, rect):
        if not self.show_background:
            return

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.background_grid_size)
        first_top = top - (top % self.background_grid_size)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.background_grid_size):
            if x % (self.background_grid_size * self.background_grid_squares) != 0:
                lines_light.append(QtCore.QLine(x, top, x, bottom))
            else: 
                lines_dark.append(QtCore.QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.background_grid_size):
            if y % (self.background_grid_size * self.background_grid_squares) != 0:
                lines_light.append(QtCore.QLine(left, y, right, y))
            else: 
                lines_dark.append(QtCore.QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self.pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self.pen_dark)
        painter.drawLines(*lines_dark)


    #--------------------------------------------------------------------------
    # QGraphicsScene API
    #--------------------------------------------------------------------------

    def set_show_background(self, show_background):
        self.show_background = show_background

    def set_background_grid_squares(self, background_grid_squares):
        self.background_grid_squares = background_grid_squares

    def set_background_grid_size(self, background_grid_size):
        self.background_grid_size = background_grid_size

    def set_color_light(self, color_light):
        self.color_light = color_light

    def set_color_dark(self, color_dark):
        self.color_dark = color_dark
