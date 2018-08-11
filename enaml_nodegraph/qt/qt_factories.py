# Register factories for Qt widgets with enaml.


from enaml.qt.qt_factories import QT_FACTORIES


def graphics_view_factory():
    from .qt_graphicsview import QtGraphicsView
    return QtGraphicsView


def graphics_scene_factory():
    from .qt_graphicsscene import QtGraphicsScene
    return QtGraphicsScene


def node_graphics_scene_factory():
    from .qt_node_graphicsscene import QtNodeGraphicsScene
    return QtNodeGraphicsScene


def node_item_factory():
    from .qt_node_item import QtNodeItem
    return QtNodeItem


def node_content_factory():
    from .qt_node_content import QtNodeContent
    return QtNodeContent


def node_socket_factory():
    from .qt_node_socket import QtNodeSocket
    return QtNodeSocket


def edge_item_factory():
    from .qt_edge_item import QtEdgeItem
    return QtEdgeItem


# Inject the factory
QT_FACTORIES.update({
    'NodeItem': node_item_factory,
    'NodeContent': node_content_factory,
    'NodeSocket': node_socket_factory,
    'EdgeItem': edge_item_factory,
    'NodeGraphicsScene': node_graphics_scene_factory,
    'GraphicsScene': graphics_scene_factory,
    'GraphicsView': graphics_view_factory,
})