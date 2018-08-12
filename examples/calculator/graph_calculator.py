import logging

import enaml
from enaml.qt.qt_application import QtApplication

from atom.api import Int, Enum, Instance, observe

from enaml_nodegraph.controller import GraphControllerBase
from enaml_nodegraph import model

with enaml.imports():
    from graph_calculator_view import Main
    from graph_item_widgets import NumberInput, SliderInput, BinaryOperator, NumberOutput, Edge

log = logging.getLogger(__name__)


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
        for socket in self.outputs:
            if socket.name == change['name']:
                socket.propagate_change(change['value'])

    def update(self):
        self.outputs[0].propagate_change(self.value)


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

    @observe('in1', 'in2', 'operator')
    def _handle_change(self, change):
        self.update()

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

    def _observe_result(self, change):
        for socket in self.outputs:
            if socket.name == change['name']:
                socket.propagate_change(change['value'])


node_type_map = {'number_input': (NumberInput, NumberInputModel),
                 'slider_input': (SliderInput, NumberInputModel),
                 'binary_operator': (BinaryOperator, BinaryOperatorModel),
                 'number_output': (NumberOutput, NumberOutputModel),
                 }

edge_type_map = {'default': (Edge, model.Edge)}


class CalculatorGraphController(GraphControllerBase):

    graph_model = Instance(model.Graph)

    def _default_graph_model(self):
        return model.Graph()

    def create_node(self, typename, **kw):
        if self.view.scene is None:
            return

        cls, mdl = node_type_map.get(typename, (None, None))
        if cls is not None:
            node = mdl()
            self.graph_model.nodes.append(node)
            kw['model'] = node
            n = cls(**kw)
            self.view.scene.insert_children(None, [n])
            return n

    def destroy_node(self, id):
        if self.view.scene is None:
            return

        if id in self.view.scene.nodes:
            if self.view.scene.nodes[id].model in self.graph_model.nodes:
                self.graph_model.nodes.remove(self.view.scene.nodes[id].model)
            self.view.scene.nodes[id].destroy()

    def create_edge(self, typename, **kw):
        if self.view.scene is None:
            return

        cls, mdl = edge_type_map.get(typename, (None, None))
        if cls is not None:
            edge = mdl()
            kw['model'] = edge
            e = cls(**kw)
            self.view.scene.insert_children(None, [e])
            return e

    def destroy_edge(self, id):
        if self.view.scene is None:
            return

        if id in self.view.scene.edges:
            if self.view.scene.edges[id].model in self.graph_model.edges:
                self.graph_model.edges.remove(self.view.scene.edges[id].model)
            self.view.scene.edges[id].destroy()

    def edge_type_for_start_socket(self, start_node, start_socket):
        return 'default'

    def edge_can_connect(self, start_node, start_socket, end_node, end_socket):
        if self.view.scene is None:
            return
        # @todo: check data_types ...
        return True

    def edge_connected(self, id):
        if id in self.view.scene.edges:
            edge_view = self.view.scene.edges[id]
            edge = edge_view.model
            ss_view = edge_view.start_socket
            edge.start_socket = [s for s in ss_view.parent.model.outputs if s.name == ss_view.name][0]
            es_view = edge_view.end_socket
            edge.end_socket = [s for s in es_view.parent.model.inputs if s.name == es_view.name][0]
            self.graph_model.edges.append(edge)

    def edge_disconnect(self, id):
        if id in self.view.scene.edges:
            if self.view.scene.edges[id].model in self.graph_model.edges:
                self.graph_model.edges.remove(self.view.scene.edges[id].model)


def test_main():

    app = QtApplication()

    controller = CalculatorGraphController()
    view = Main(controller=controller)
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    test_main()