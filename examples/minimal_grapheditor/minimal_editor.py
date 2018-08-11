import enaml
from enaml.qt.qt_application import QtApplication

with enaml.imports():
    from minimal_editor_view import Main
    from graph_item_widgets import TestNode1, TestNode2, TestEdge

from enaml_nodegraph.controller import GraphControllerBase

node_type_map = {'node1': TestNode1,
                 'node2': TestNode2}

edge_type_map = {'default': TestEdge}


class TestGraphController(GraphControllerBase):

    def create_node(self, typename, **kw):
        if self.view.scene is None:
            return

        cls = node_type_map.get(typename, None)
        if cls is not None:
            n = cls(**kw)
            self.view.scene.insert_children(None, [n])
            return n

    def destroy_node(self, id):
        if self.view.scene is None:
            return

        if id in self.view.scene.nodes:
            self.view.scene.nodes[id].destroy()

    def create_edge(self, typename, **kw):
        if self.view.scene is None:
            return

        cls = edge_type_map.get(typename, None)
        if cls is not None:
            e = cls(**kw)
            self.view.scene.insert_children(None, [e])
            return e

    def destroy_edge(self, id):
        if self.view.scene is None:
            return

        if id in self.view.scene.edges:
            self.view.scene.edges[id].destroy()

    def edge_type_for_start_socket(self, start_node, start_socket):
        return 'default'

    def edge_can_connect(self, start_node, start_socket, end_node, end_socket):
        if self.view.scene is None:
            return

        return True

    def edge_connected(self, id):
        print("Edge was connected: ", id)


def test_main():

    app = QtApplication()

    controller = TestGraphController()
    view = Main(controller=controller)
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    test_main()