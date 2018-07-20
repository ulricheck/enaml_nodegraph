from enaml.qt import QtCore, QtGui, QtWidgets
from atom.api import Typed, Int
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_widget import QtWidget
from enaml_nodegraph.widgets.node_content import ProxyNodeContent


class QGraphicsProxyWidget(QtWidgets.QGraphicsProxyWidget):

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy = proxy

    # not implemented by QGraphicsProxyWidget
    def setStyleSheet(self, stylesheet):
        pass


class QtNodeContent(QtControl, ProxyNodeContent):
    """ A Qt implementation of an Enaml ProxyNodeContent widget.

    """

    content = Typed(QtWidget)

    #: A reference to the widget created by the proxy.
    widget = Typed(QGraphicsProxyWidget)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying html widget.

        """
        parent = self.parent_widget()
        widget = QGraphicsProxyWidget(self, parent,)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underlying widget.
        """
        super(QtNodeContent, self).init_widget()

    def activate_bottom_up(self):
        super(QtNodeContent, self).activate_bottom_up()
        for c in self.children():
            self.content = c
            break

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    def _observe_content(self, change):
        content = change['value']
        if content is not None:
            self.widget.setWidget(content.widget)
            self.set_content_geometry()
        else:
            self.widget.setWidget(None)

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def set_content_geometry(self):
        n = self.parent()
        self.content.widget.setGeometry(n.edge_size,
                                        n.title_height + n.edge_size,
                                        n.width - 2 * n.edge_size,
                                        n.height - 2 * n.edge_size - n.title_height)
