__author__ = 'jack'

from atom.api import Typed, Int, Bool, ForwardTyped, observe
from enaml.core.declarative import d_
from enaml.colors import ColorMember

from enaml_nodegraph.widgets.graphicsscene import GraphicsScene, ProxyGraphicsScene
from enaml_nodegraph.widgets.node_item import NodeItem

class ProxyNodeGraphicsScene(ProxyGraphicsScene):
    """ The abstract definition of a proxy QtWidgets.QGraphicsScene object.

    """
    #: A reference to the OpenGLWidget declaration.
    declaration = ForwardTyped(lambda: NodeGraphicsScene)

    def update(self, *args):
        raise NotImplementedError()

    def boundingRect(self):
        raise NotImplementedError()

    def set_width(self, width):
        raise NotImplementedError

    def set_height(self, height):
        raise NotImplementedError

    def set_show_background(self, show_background):
        raise NotImplementedError

    def set_background_grid_squares(self, background_grid_squares):
        raise NotImplementedError

    def set_background_grid_size(self, background_grid_size):
        raise NotImplementedError

    def set_background(self, background):
        raise NotImplementedError

    def set_color_light(self, color_light):
        raise NotImplementedError

    def set_color_dark(self, color_dark):
        raise NotImplementedError


class NodeGraphicsScene(GraphicsScene):
    """ A widget for displaying QGraphicsScene.

    """

    # Background style
    show_background = d_(Bool(True))

    background_grid_size = d_(Int(20))
    background_grid_squares = d_(Int(5))

    # color scheme
    color_light = d_(ColorMember("#2f2f2f"))
    color_dark = d_(ColorMember("#292929"))

    #: A reference to the ProxyNodeGraphicsScene object
    proxy = Typed(ProxyNodeGraphicsScene)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(
        'show_background', 'background_grid_squares',
        'background_grid_size', 'background', 'color_light', 'color_dark'
        )
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        super(NodeGraphicsScene, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # API
    #--------------------------------------------------------------------------

