import logging
import os
import networkx as nx
import json

from atom.api import (Bool, List, Str, Typed, Instance, Event, observe)

from enaml_nodegraph.controller import GraphControllerBase
from enaml_nodegraph.widgets.node_item import NodeItem
from enaml_nodegraph.primitives import Point2D, Transform2D

from .registry import TypeRegistry
from .model import ExecutableGraph

log = logging.getLogger(__name__)


class CalculatorGraphController(GraphControllerBase):

    is_active = Bool(False)
    is_dirty = Bool(False)

    current_path = Str()
    filename = Str()

    registry = Typed(TypeRegistry)
    graph = Instance(ExecutableGraph)

    selectedNodes = List(NodeItem)

    def default_current_path(self):
        return os.curdir

    def _default_registry(self):
        return TypeRegistry()

    def _default_graph(self):
        return ExecutableGraph(controller=self)

    @observe('view.selectedItems')
    def filter_selected_items(self, change):
        self.selectedNodes = [i for i in change['value'] if isinstance(i, NodeItem)]

    @observe('graph.topologyChanged', 'graph.attributesChanged')
    def mark_dirty(self, change):
        self.is_dirty = True

    def create_node(self, typename, **kw):
        if self.view.scene is None:
            return

        nt = self.registry.node_type_name_map.get(typename, None)
        if nt is not None:
            node = nt.model_class()
            kw['model'] = node
            kw['type_name'] = typename
            n = nt.widget_class(**kw)
            self.view.scene.insert_children(None, [n])
            node.id = n.id
            n.name = "%s (%s)" % (nt.name, n.id.split("-")[-1])
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
            kw['type_name'] = typename
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

    def serialize_graph(self):
        G = self.graph.nxgraph.copy()
        G.graph['viewport_transform'] = self.view.getViewportTransform().to_list()
        for node_id in G.nodes():
            node_view = self.view.scene.nodes[node_id]
            node_data = {}
            self.serialize_node(node_data, node_view)
            G.nodes[node_id].update(node_data)

        for start_node_id, end_node_id, key, edge_id in G.edges(data='id', keys=True):
            if edge_id is None:
                continue
            edge_view = self.view.scene.edges[edge_id]
            edge_data = {}
            self.serialize_edge(edge_data, edge_view)
            G.edges[start_node_id, end_node_id, key].update(edge_data)

        return G

    def serialize_node(self, archive, node_view):
        archive['type_name'] = node_view.type_name
        archive['position'] = node_view.position.to_list()
        if node_view.model is not None:
            node_view.model.serialize(archive)

    def serialize_edge(self, archive,  edge_view):
        archive['type_name'] = edge_view.type_name
        if edge_view.model is not None:
            edge_view.model.serialize(archive)

    def deserialize_graph(self, G, replace=True):
        if 'viewport_transform' in G.graph:
            self.view.setViewportTransform(Transform2D.from_list(G.graph['viewport_transform']))

        for node_id in G.nodes.keys():
            data = G.nodes[node_id]
            type_name = data.get('type_name', None)
            if type_name is None:
                log.error("Invalid Node (missing type_name): %s" % node_id)
                continue

            position = Point2D.from_list(data['position'])
            name = data['name']

            n = self.create_node(type_name, id=node_id, name=name, position=position)
            if n.model is not None:
                n.model.deserialize(data)

        for start_node_id, end_node_id, key, edge_id in G.edges(data='id', keys=True):
            data = G.edges[start_node_id, end_node_id, key]
            type_name = data.get('type_name', None)
            if type_name is None:
                log.error("Invalid Edge (missing type_name): %s" % edge_id)
                continue

            source_socket_name = data['source_socket']
            target_socket_name = data['target_socket']
            source_socket = None
            target_socket = None
            for socket in self.view.scene.nodes[start_node_id].output_sockets:
                if socket.name == source_socket_name:
                    source_socket = socket
                    break
            for socket in self.view.scene.nodes[end_node_id].input_sockets:
                if socket.name == target_socket_name:
                    target_socket = socket
                    break
            if source_socket is None or target_socket is None:
                log.error("Invalid edge - missing socket: %s" % edge_id)
                continue

            e = self.create_edge(type_name, id=edge_id)
            e.start_socket = source_socket
            e.end_socket = target_socket

            if e.model is not None:
                e.model.deserialize(data)

            self.edge_connected(edge_id)

    def file_new(self):
        self.filename = ""
        self.view.scene.clear_all()
        self.is_dirty = False

    def file_open(self, filename, replace=True):
        self.current_path = os.path.dirname(filename)
        self.filename = os.path.basename(filename)
        if replace:
            self.view.scene.clear_all()
        g = nx.node_link_graph(json.load(open(os.path.join(self.current_path, self.filename), 'r')))
        self.deserialize_graph(g, replace=replace)
        self.is_dirty = False

    def file_save(self, filename):
        self.current_path = os.path.dirname(filename)
        self.filename = os.path.basename(filename)
        g = self.serialize_graph()
        json.dump(nx.node_link_data(g), open(os.path.join(self.current_path, self.filename), 'w'))
        self.is_dirty = False
