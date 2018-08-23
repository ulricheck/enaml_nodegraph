__author__ = 'jack'
import logging

from atom.api import Typed, List, Instance, ForwardTyped, ForwardInstance, set_default
from enaml.widgets.control import Control, ProxyControl
from enaml.core.declarative import d_

from .graphicsitem import GraphicsItem
from .graphicsscene import GraphicsScene
from .edge_item import EdgeItem, EdgeType
from .node_socket import NodeSocket, SocketType

log = logging.getLogger(__name__)


def import_graph_controller_class():
    from enaml_nodegraph.controller import GraphControllerBase
    return GraphControllerBase


class ProxyGraphicsView(ProxyControl):
    """ The abstract definition of a proxy QtWidgets.QGraphicsScene object.

    """
    #: A reference to the OpenGLWidget declaration.
    declaration = ForwardTyped(lambda: GraphicsView)

    def update(self, *args):
        raise NotImplementedError

    def set_scene(self, scene):
        raise NotImplementedError


class GraphicsView(Control):
    """ A widget for displaying QGraphicsScene.

    """

    controller = d_(ForwardInstance(import_graph_controller_class))

    scene = d_(Typed(GraphicsScene))

    selectedItems = d_(List(GraphicsItem))

    #: An graphicsview widget expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    _dragEdge = Instance(EdgeItem)

    #: A reference to the ProxyGraphicsView object
    proxy = Typed(ProxyGraphicsView)

    #--------------------------------------------------------------------------
    # Content Helpers
    #--------------------------------------------------------------------------

    def child_added(self, child):
        """ Set the scene attribute when a scene child is added """
        super(GraphicsView, self).child_added(child)
        if isinstance(child, GraphicsScene):
            self.scene = child

    def child_removed(self, child):
        """ Reset the scene attribute when a scene child is removed """
        super(GraphicsView, self).child_removed(child)
        if isinstance(child, GraphicsScene):
            self.scene = None

    def activate_top_down(self):
        if not self.scene:
            log.warning("GraphicsView needs a scene to work properly.")
        if not self.controller:
            log.warning("GraphicsView needs controller to work properly.")
        super(GraphicsView, self).activate_top_down()
        if self.scene is not None:
            self.proxy.set_scene(self.scene)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    def _observe_scene(self, change):
        if self.proxy is not None and change['value'] is not None:
            self.proxy.set_scene(change['value'])

    def _observe_controller(self, change):
        ctrl = change['value']
        if ctrl is not None:
            ctrl.set_view(self)
        if self.scene is not None:
            self.scene.controller = ctrl

    #--------------------------------------------------------------------------
    # API
    #--------------------------------------------------------------------------

    def edgeDragStart(self, item):
        if self.controller is None:
            log.warning("GraphicsView has no controller - ignoring request")
            return
        if isinstance(item, NodeSocket) and item.socket_type == SocketType.OUTPUT:
            edge_typename = self.controller.edge_type_for_start_socket(item.parent.id, item.id)
            self._dragEdge = self.controller.create_edge(edge_typename,
                                                         start_socket=item,
                                                         end_socket=None,
                                                         scene=self.scene)
            self._dragEdge.pos_destination = item.absolute_position
        else:
            log.warning("Invalid edge start: ", item)

    def edgeDragEnd(self, item):
        if self._dragEdge is None:
            return

        ss = self._dragEdge.start_socket
        if isinstance(item, NodeSocket) and item.socket_type == SocketType.INPUT and \
                self.controller.edge_can_connect(ss.parent.id, ss.id, item.parent.id, item.id):
            self._dragEdge.end_socket = item
            self.controller.edge_connected(self._dragEdge.id)
        else:
            if self._dragEdge is not None:
                self.controller.destroy_edge(self._dragEdge.id)

        self._dragEdge = None

    def updatePoseEdgeDrag(self, pos):
        if self._dragEdge is not None:
            self._dragEdge.pos_destination = pos

    def handle_selection_changed(self, items):
        self.selectedItems = items
        if self.controller is not None:
            self.controller.itemsSelected(items)

    def getViewportTransform(self):
        if self.proxy is not None:
            return self.proxy.getViewportTransform()

    def setViewportTransform(self, trans):
        if self.proxy is not None:
            self.proxy.setViewportTransform(trans)

    def fitNodesInView(self):
        self.proxy.fitInView(self.scene.bounding_box_all_nodes())

    def resetViewportTransform(self):
        self.proxy.resetViewportTransform()

