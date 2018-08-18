import logging

from atom.api import (Bool, List, Typed, Instance, observe)

from enaml_nodegraph.controller import GraphControllerBase
from enaml_nodegraph.widgets.node_item import NodeItem

from .registry import TypeRegistry
from .model import ExecutableGraph

log = logging.getLogger(__name__)


class CalculatorGraphController(GraphControllerBase):

    is_active = Bool(False)

    registry = Typed(TypeRegistry)
    graph = Instance(ExecutableGraph)

    selectedNodes = List(NodeItem)

    def _default_registry(self):
        return TypeRegistry()

    def _default_graph(self):
        return ExecutableGraph(controller=self)

    @observe('view.selectedItems')
    def filter_selected_items(self, change):
        self.selectedNodes = [i for i in change['value'] if isinstance(i, NodeItem)]

    def create_node(self, typename, **kw):
        if self.view.scene is None:
            return

        nt = self.registry.node_type_name_map.get(typename, None)
        if nt is not None:
            node = nt.model_class()
            kw['model'] = node
            n = nt.widget_class(**kw)
            self.view.scene.insert_children(None, [n])
            node.id = n.id
            self.graph.nodes.append(node)
            self.graph.topologyChanged()
            return n

    def destroy_node(self, id):
        if self.view.scene is None:
            return

        if id in self.view.scene.nodes:
            if self.view.scene.nodes[id].model in self.graph.nodes:
                self.graph.nodes.remove(self.graph.node_dict[id])
            self.view.scene.nodes[id].destroy()
            self.graph.topologyChanged()

    def create_edge(self, typename, **kw):
        if self.view.scene is None:
            return

        et = self.registry.edge_type_name_map.get(typename, None)
        if et is not None:
            edge = et.model_class()
            kw['model'] = edge
            e = et.widget_class(**kw)
            self.view.scene.insert_children(None, [e])
            edge.id = e.id
            return e

    def destroy_edge(self, id):
        if self.view.scene is None:
            return

        if id in self.view.scene.edges:
            if self.view.scene.edges[id].model in self.graph.edges:
                self.graph.edges.remove(self.view.scene.edges[id].model)
            self.view.scene.edges[id].destroy()

    def edge_type_for_start_socket(self, start_node, start_socket):
        return 'default'

    def edge_can_connect(self, start_node_id, start_socket_id, end_node_id, end_socket_id):
        if self.view.scene is None:
            return False
        try:
            start_node = self.graph.node_dict[start_node_id]
            end_node = self.graph.node_dict[end_node_id]
            start_socket = start_node.output_dict[start_socket_id]
            end_socket = end_node.input_dict[end_socket_id]
            return end_socket.can_connect(start_socket)
        except KeyError as e:
            log.exception(e)
            return False

    def edge_connected(self, id):
        if id in self.view.scene.edges:
            edge_view = self.view.scene.edges[id]
            edge = edge_view.model
            ss_view = edge_view.start_socket
            edge.start_socket = ss_view.parent.model.output_dict[ss_view.name]
            es_view = edge_view.end_socket
            edge.end_socket = es_view.parent.model.input_dict[es_view.name]
            self.graph.edges.append(edge)
            self.graph.topologyChanged()

    def edge_disconnect(self, id):
        if id in self.view.scene.edges:
            edge = self.view.scene.edges[id].model
            edge.start_socket = None
            edge.end_socket = None
            if edge in self.graph.edges:
                self.graph.edges.remove(edge)
            self.graph.topologyChanged()

