__author__ = 'jack'

from atom.api import Typed, Int, Bool, ForwardTyped, observe, set_default, Signal
from enaml.core.declarative import d_
from enaml.colors import ColorMember, parse_color
from enaml.widgets.control import Control, ProxyControl

from .graphicsscene import GraphicsScene


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

    scene = Typed(GraphicsScene)

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
        super(GraphicsView, self).activate_top_down()
        if self.scene is not None:
            self.proxy.set_scene(self.scene)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    def _observe_scene(self, change):
        if self.proxy is not None and change['value'] is not None:
            self.proxy.set_scene(change['value'])

    #--------------------------------------------------------------------------
    # API
    #--------------------------------------------------------------------------

