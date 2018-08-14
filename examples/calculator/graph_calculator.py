import logging

import networkx as nx

import enaml
from enaml.qt.qt_application import QtApplication

from atom.api import Int, Enum, Instance, Property, Event, ForwardInstance, observe

from enaml_nodegraph.controller import GraphControllerBase
from enaml_nodegraph import model

with enaml.imports():
    from graph_calculator_view import Main
    from graph_item_widgets import (NumberInput, SliderInput, RampGenerator, BinaryOperator,
                                    NumberOutput, GraphOutput, Edge)

log = logging.getLogger(__name__)


class ExecutableGraph(model.Graph):
    controller = ForwardInstance(lambda: CalculatorGraphController)
    nxgraph = Property(lambda self: self._get_nxgraph(), cached=True)

    topologyChanged = Event()
    valuesChanged = Event()

    def _get_nxgraph(self):
        g = nx.DiGraph()
        for node in self.nodes:
            g.add_node(node)
        for edge in self.edges:
            g.add_edge(edge.start_socket.node, edge.end_socket.node)
        return g

    def _observe_topologyChanged(self, change):
        self.get_member('nxgraph').reset(self)
        self.execute_graph()

    def _observe_valuesChanged(self, change):
        self.execute_graph()

    def execute_graph(self):
        for node in nx.topological_sort(self.nxgraph):
            node.update()


class OutputSocket(model.Socket):

    def propagate_change(self, value):
        for edge in self.edges:
            if edge.end_socket is not None:
                edge.end_socket.receive_value(value)


class InputSocket(model.Socket):

    def receive_value(self, value):
        self.node.set_value(self.name, value)


class NumberInputModel(model.Node):
    value = Int()

    def _default_outputs(self):
        return [OutputSocket(name="value", data_type="int")]

    def _observe_value(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        self.output_dict['value'].propagate_change(self.value)


class NumberOutputModel(model.Node):
    value = Int()

    def _default_inputs(self):
        return [InputSocket(name="value", data_type="int")]

    def set_value(self, key, value):
        setattr(self, key, value)

    def update(self):
        pass


class BinaryOperatorModel(model.Node):

    operator = Enum('add', 'sub', 'mul', 'div')
    in1 = Int()
    in2 = Int()

    result = Int()

    def _default_inputs(self):
        return [InputSocket(name="in1", data_type="int"), InputSocket(name="in2", data_type="int")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="int")]

    def set_value(self, key, value):
        setattr(self, key, value)

    def _observe_operator(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        if self.operator == 'add':
            self.result = self.in1 + self.in2
        elif self.operator == 'sub':
            self.result = self.in1 - self.in2
        elif self.operator == 'mul':
            self.result = self.in1 * self.in2
        elif self.operator == 'div':
            try:
                self.result = int(self.in1 / self.in2)
            except Exception as e:
                log.error(e)
        else:
            log.warning("invalid operator: %s" % self.operator)
        self.output_dict['result'].propagate_change(self.result)


node_type_map = {'number_input': (NumberInput, NumberInputModel),
                 'slider_input': (SliderInput, NumberInputModel),
                 'ramp_generator': (RampGenerator, NumberInputModel),
                 'binary_operator': (BinaryOperator, BinaryOperatorModel),
                 'number_output': (NumberOutput, NumberOutputModel),
                 'graph_output': (GraphOutput, NumberOutputModel),
                 }

edge_type_map = {'default': (Edge, model.Edge)}


class CalculatorGraphController(GraphControllerBase):

    graph = Instance(ExecutableGraph)

    def _default_graph(self):
        return ExecutableGraph(controller=self)

    def create_node(self, typename, **kw):
        if self.view.scene is None:
            return

        cls, mdl = node_type_map.get(typename, (None, None))
        if cls is not None:
            node = mdl()
            kw['model'] = node
            n = cls(**kw)
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

        cls, mdl = edge_type_map.get(typename, (None, None))
        if cls is not None:
            edge = mdl()
            kw['model'] = edge
            e = cls(**kw)
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


def test_main():

    app = QtApplication()

    controller = CalculatorGraphController()
    view = Main(controller=controller)
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    test_main()