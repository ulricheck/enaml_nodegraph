__author__ = 'jack'

from atom.api import Typed, Int, Bool, ForwardTyped, observe, set_default, Signal
from enaml.core.declarative import d_
from enaml.colors import ColorMember, parse_color
from enaml.widgets.control import Control, ProxyControl


class ProxyNodeContent(ProxyControl):
    """ The abstract definition of a proxy QtWidgets.QGraphicsScene object.

    """
    #: A reference to the OpenGLWidget declaration.
    declaration = ForwardTyped(lambda: NodeContent)


class NodeContent(Control):
    """ A widget for displaying QGraphicsScene.

    """

    #: A reference to the ProxyGraphicsView object
    proxy = Typed(ProxyNodeContent)

    #--------------------------------------------------------------------------
    # Content Helpers
    #--------------------------------------------------------------------------

    def child_added(self, child):
        """ Set the scene attribute when a scene child is added """
        super(NodeContent, self).child_added(child)
        child._parent = None

    def child_removed(self, child):
        """ Reset the scene attribute when a scene child is removed """
        super(NodeContent, self).child_removed(child)

    def activate_top_down(self):
        super(NodeContent, self).activate_top_down()
        # if self.scene is not None:
        #     self.proxy.set_scene(self.scene)



    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # API
    #--------------------------------------------------------------------------

