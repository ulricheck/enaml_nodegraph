from enaml.qt import QtCore, QtGui, QtWidgets
from atom.api import Typed, Int, Event, IntEnum, Bool, Float, Int, Range
from enaml.qt.qt_control import QtControl

from enaml_nodegraph.widgets.graphicsview import ProxyGraphicsView
from enaml_nodegraph.widgets.graphicsscene import GraphicsScene
from enaml_nodegraph.widgets.graphicsitem import GraphicsItem
from enaml_nodegraph.primitives import Point2D

from enaml_nodegraph.qt.qt_node_item import QNodeItem
from enaml_nodegraph.qt.qt_edge_item import QEdgeItem
from enaml_nodegraph.qt.qt_node_socket import QNodeSocket, QtNodeSocket


class EdgeEditMode(IntEnum):
    MODE_NOOP = 1
    MODE_EDGE_DRAG = 2
    MODE_EDGE_CUT = 3


class QGraphicsView(QtWidgets.QGraphicsView):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy

    def getItemAtClick(self, event):
        """ return the object on which we've clicked/release mouse button """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def distanceBetweenClickAndReleaseIsOff(self, event):
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        llmbcsp = QtCore.QPointF(self.proxy.lastLmbClickScenePos.x, self.proxy.lastLmbClickScenePos.y)
        dist_scene = new_lmb_release_scene_pos - llmbcsp
        edge_drag_threshold_sq = self.proxy.edgeDragStartThreshold*self.proxy.edgeDragStartThreshold
        return (dist_scene.x()*dist_scene.x() + dist_scene.y()*dist_scene.y()) > edge_drag_threshold_sq

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        release_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                                          event.localPos(),
                                          event.screenPos(),
                                          QtCore.Qt.LeftButton,
                                          QtCore.Qt.NoButton,
                                          event.modifiers())
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        fake_event = QtGui.QMouseEvent(event.type(),
                                       event.localPos(),
                                       event.screenPos(),
                                       QtCore.Qt.LeftButton,
                                       event.buttons() | QtCore.Qt.LeftButton,
                                       event.modifiers())
        super().mousePressEvent(fake_event)

    def middleMouseButtonRelease(self, event):
        fake_event = QtGui.QMouseEvent(event.type(),
                                       event.localPos(),
                                       event.screenPos(),
                                       QtCore.Qt.LeftButton,
                                       event.buttons() & ~QtCore.Qt.LeftButton,
                                       event.modifiers())
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event):
        # get item which we clicked on
        item = self.getItemAtClick(event)

        # we store the position of last LMB click
        point = self.mapToScene(event.pos())
        self.proxy.lastLmbClickScenePos = Point2D(x=point.x(), y=point.y())

        # logic
        if isinstance(item, QNodeItem) or isinstance(item, QEdgeItem) or item is None:
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                event.ignore()
                fake_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,
                                               event.localPos(),
                                               event.screenPos(),
                                               QtCore.Qt.LeftButton,
                                               event.buttons() | QtCore.Qt.LeftButton,
                                               event.modifiers() | QtCore.Qt.ControlModifier)
                super().mousePressEvent(fake_event)
                return

        if isinstance(item, QNodeSocket):
            if self.proxy.edgeEditMode == EdgeEditMode.MODE_NOOP:
                self.proxy.edgeEditMode = EdgeEditMode.MODE_EDGE_DRAG
                self.proxy.edgeDragStart(item.proxy if item is not None else None)
                return

        if self.proxy.edgeEditMode == EdgeEditMode.MODE_EDGE_DRAG:
            res = self.proxy.edgeDragEnd(item)
            self.proxy.edgeEditMode = EdgeEditMode.MODE_NOOP
            if res:
                return

        if item is None:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self.proxy.edgeEditMode = EdgeEditMode.MODE_EDGE_CUT
                fake_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                                               event.localPos(),
                                               event.screenPos(),
                                               QtCore.Qt.LeftButton,
                                               QtCore.Qt.NoButton,
                                               event.modifiers())
                super().mouseReleaseEvent(fake_event)
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
                return
            else:
                self.proxy.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        # get item which we release mouse button on
        item = self.getItemAtClick(event)

        # logic
        if isinstance(item, QNodeItem) or isinstance(item, QEdgeItem) or item is None:
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                event.ignore()
                fake_event = QtGui.QMouseEvent(event.type(),
                                               event.localPos(),
                                               event.screenPos(),
                                               QtCore.Qt.LeftButton,
                                               QtCore.Qt.NoButton,
                                               event.modifiers() | QtCore.Qt.ControlModifier)
                super().mouseReleaseEvent(fake_event)
                return

        if self.proxy.edgeEditMode == EdgeEditMode.MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.proxy.edgeDragEnd(item.proxy if item is not None else None)
                self.proxy.edgeEditMode = EdgeEditMode.MODE_NOOP
                if res:
                    return

        if self.proxy.edgeEditMode == EdgeEditMode.MODE_EDGE_CUT:
            self.proxy.cutIntersectingEdges()
            # self.proxy.cutline.line_points = []
            # self.proxy.cutline.update()
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            self.proxy.edgeEditMode = EdgeEditMode.MODE_NOOP
            return

        if self.proxy.rubberBandDraggingRectangle:
            # self.grScene.scene.history.storeHistory("Selection changed")
            self.proxy.rubberBandDraggingRectangle = False

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)
        item = self.getItemAtClick(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)
        item = self.getItemAtClick(event)

    def mouseMoveEvent(self, event):
        if self.proxy.edgeEditMode == EdgeEditMode.MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.proxy.updatePoseEdgeDrag(Point2D(x=pos.x(), y=pos.y()))

        if self.proxy.edgeEditMode == EdgeEditMode.MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            # self.cutline.line_points.append(pos)
            # self.cutline.update()

        point = self.mapToScene(event.pos())
        self.proxy.lastSceneMousePosition = Point2D(x=point.x(), y=point.y())

        self.proxy.scenePosChanged(Point2D(x=point.x(), y=point.y()))

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.saveToFile("graph.json.txt")
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.loadFromFile("graph.json.txt")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.redo()
        # elif event.key() == Qt.Key_H:
        #     print("HISTORY:     len(%d)" % len(self.grScene.scene.history.history_stack),
        #           " -- current_step", self.grScene.scene.history.history_current_step)
        #     ix = 0
        #     for item in self.grScene.scene.history.history_stack:
        #         print("#", ix, "--", item['desc'])
        #         ix += 1
        # else:
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        # calculate our zoom Factor

        # @todo: use modifiers to switch between panning and zooming
        zoomOutFactor = 1 / self.proxy.zoomInFactor

        zoom = self.proxy.zoom
        # calculate zoom
        if event.angleDelta().y() > 0:
            zoom_factor = self.proxy.zoomInFactor
            zoom += self.proxy.zoomStep
        else:
            zoom_factor = zoomOutFactor
            zoom -= self.proxy.zoomStep

        try:
            self.proxy.zoom = zoom
            self.scale(zoom_factor, zoom_factor)
        except TypeError:
            pass


class QtGraphicsView(QtControl, ProxyGraphicsView):
    """ A Qt implementation of an Enaml ProxyGraphicsView widget.

    """

    scene = Typed(GraphicsScene)

    #: A reference to the widget created by the proxy.
    widget = Typed(QGraphicsView)

    # state variables to control interaction
    scenePosChanged = Event()
    lastLmbClickScenePos = Typed(Point2D)
    lastSceneMousePosition = Typed(Point2D)
    edgeEditMode = Typed(EdgeEditMode, factory=lambda: EdgeEditMode.MODE_NOOP)
    rubberBandDraggingRectangle = Bool()

    edgeDragStartThreshold = Int(10)

    zoomInFactor = Float(1.05)
    zoomStep = Int(1)
    zoom = Range(low=0, high=100, value=50)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)


    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying html widget.

        """
        self.widget = QGraphicsView(self, self.parent_widget())

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
            self.scene.proxy.widget.selectionChanged.connect(self.handle_selection_changed)
        else:
            print("warning: no scene defined for graphicsview")


    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def set_scene(self, scene):
        if isinstance(scene, GraphicsScene):
            self.scene = scene
            if scene.proxy.widget is not None:
                if self.widget is not None:
                    self.widget.setScene(scene.proxy.widget)

    def edgeDragStart(self, item):
        self.declaration.edgeDragStart(item.declaration if isinstance(item, QtNodeSocket) else None)

    def edgeDragEnd(self, item):
        self.declaration.edgeDragEnd(item.declaration if isinstance(item, QtNodeSocket) else None)

    def updatePoseEdgeDrag(self, pos):
        self.declaration.updatePoseEdgeDrag(pos)

    def handle_selection_changed(self):
        if self.scene is not None and self.scene.proxy is not None:
            items = self.scene.proxy.widget.selectedItems()
            self.declaration.handle_selection_changed([i.proxy.declaration for i in items if isinstance(i.proxy.declaration, GraphicsItem)])
