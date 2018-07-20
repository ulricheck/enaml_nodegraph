from enaml.qt import QtCore, QtGui, QtWidgets
from atom.api import Typed, Int
from enaml.qt.qt_control import QtControl

from enaml_nodegraph.widgets.graphicsview import ProxyGraphicsView
from enaml_nodegraph.widgets.graphicsscene import GraphicsScene


class QGraphicsView(QtWidgets.QGraphicsView):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy


class QtGraphicsView(QtControl, ProxyGraphicsView):
    """ A Qt implementation of an Enaml ProxyGraphicsView widget.

    """

    scene = Typed(GraphicsScene)

    #: A reference to the widget created by the proxy.
    widget = Typed(QGraphicsView)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)


    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying html widget.

        """
        widget = QGraphicsView(self, self.parent_widget(),)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underlying widget.
        """
        super(QtGraphicsView, self).init_widget()
        self.widget.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
                                   QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.widget.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.widget.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.widget.setDragMode(QGraphicsView.RubberBandDrag)

    def activate_bottom_up(self):
        super(QtGraphicsView, self).activate_bottom_up()
        if self.scene is not None:
            self.widget.setScene(self.scene.proxy.widget)
        else:
            print("warning: no scene defined for graphicsview")

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def set_scene(self, scene):
        if isinstance(scene, GraphicsScene):
            self.scene = scene
            if self.widget is not None and scene.proxy.widget is not None:
                self.widget.setScene(scene.proxy.widget)

    def update(self, *args):
        pass

