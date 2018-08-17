import logging
import networkx as nx

import enaml
from enaml.qt.qt_application import QtApplication

from atom.api import (Atom, AtomMeta, Bool, Int, Enum, Str, Unicode, ContainerList, List, Dict, Typed,
                      Instance, Property, Event, ForwardInstance, observe)

from enaml_nodegraph.controller import GraphControllerBase
from enaml_nodegraph.widgets.node_item import NodeItem
from enaml_nodegraph import model

with enaml.imports():
    from graph_calculator_view import Main
    from graph_item_widgets import (NumberInput, SliderInput, RampGenerator, BinaryOperator,
                                    NumberOutput, GraphOutput, Edge)
    from graph_item_widgets import (NumberInputEditor, SliderInputEditor,
                                    RampGeneratorEditor, BinaryOperatorEditor,
                                    NumberOutputEditor, GraphOutputEditor)

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

    def _default_attributes(self):
        attrs = {'value': Int()}
        return type("NumberInputAttributes", (model.Attributes,), attrs)()

    def _default_outputs(self):
        return [OutputSocket(name="value", data_type="int")]

    @observe("attributes.value")
    def _handle_value_change(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        self.output_dict['value'].propagate_change(self.attributes.value)


class SliderInputModel(model.Node):

    def _default_attributes(self):
        attrs = {'value': Int(),
                 'min_value': Int(),
                 'max_value': Int(),
                 'step': Int(),
                 }
        return type("SliderInputAttributes", (model.Attributes,), attrs)()

    def _default_outputs(self):
        return [OutputSocket(name="value", data_type="int")]

    @observe("attributes.value")
    def _handle_value_change(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        self.output_dict['value'].propagate_change(self.attributes.value)


class RampGeneratorModel(model.Node):

    value = Int()

    def _default_attributes(self):
        attrs = {'is_running': Bool(),
                 'interval': Int(),
                 'min_value': Int(),
                 'max_value': Int()
                 }
        return type("RampGeneratorAttributes", (model.Attributes,), attrs)()

    def _default_outputs(self):
        return [OutputSocket(name="value", data_type="int")]

    @observe("value")
    def _handle_value_change(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        self.output_dict['value'].propagate_change(self.value)


class NumberOutputModel(model.Node):

    def _default_attributes(self):
        attrs = {'value': Int()}
        return type("NumberOutputAttributes", (model.Attributes,), attrs)()

    def _default_inputs(self):
        return [InputSocket(name="value", degree=1, data_type="int")]

    def set_value(self, key, value):
        setattr(self.attributes, key, value)

    def update(self):
        pass


class GraphOutputModel(model.Node):

    def _default_attributes(self):
        attrs = {'values': List(Int()),
                 'max_entries': Int()}
        return type("GraphOutputAttributes", (model.Attributes,), attrs)()

    def _default_inputs(self):
        return [InputSocket(name="value", degree=1, data_type="int")]

    def set_value(self, key, value):
        start_idx = max(0, len(self.attributes.values)-self.attributes.max_entries+1)
        val = self.attributes.values[start_idx:]
        val.append(value)
        self.attributes.values = val

    def update(self):
        pass


class BinaryOperatorModel(model.Node):

    def _default_attributes(self):
        attrs = {'operator': Enum('add', 'sub', 'mul', 'div')}
        return type("BinaryOperatorAttributes", (model.Attributes,), attrs)()

    in1 = Int()
    in2 = Int()

    result = Int()

    def _default_inputs(self):
        return [InputSocket(name="in1", degree=1, data_type="int"),
                InputSocket(name="in2", degree=1, data_type="int")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="int")]

    def set_value(self, key, value):
        setattr(self, key, value)

    @observe("attributes.operator")
    def _handle_operator_change(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        op = self.attributes.operator
        if op == 'add':
            self.result = self.in1 + self.in2
        elif op == 'sub':
            self.result = self.in1 - self.in2
        elif op == 'mul':
            self.result = self.in1 * self.in2
        elif op == 'div':
            try:
                self.result = int(self.in1 / self.in2)
            except Exception as e:
                log.error(e)
        else:
            log.warning("invalid operator: %s" % op)
        self.output_dict['result'].propagate_change(self.result)


class TypeElement(Atom):
    id = Str()
    name = Unicode()
    widget_class = Typed(AtomMeta)
    model_class = Typed(AtomMeta)


class NodeType(TypeElement):
    editor_class = Typed(AtomMeta)


class EdgeType(TypeElement):
    pass


class TypeRegistry(Atom):
    node_types = ContainerList(NodeType)
    edge_types = ContainerList(EdgeType)

    node_type_name_map = Dict()
    edge_type_name_map = Dict()

    node_widget_class_name_map = Dict()
    edge_widget_class_name_map = Dict()

    def _observe_node_types(self, change):
        self.node_type_name_map = {v.id: v for v in self.node_types}
        self.node_widget_class_name_map = {v.widget_class: v.id for v in self.node_types}

    def _observe_edge_types(self, change):
        self.edge_type_name_map = {v.id: v for v in self.edge_types}
        self.edge_widget_class_name_map = {v.widget_class: v.id for v in self.edge_types}

    def register_node_type(self, node_type):
        self.node_types.append(node_type)

    def register_edge_type(self, edge_type):
        self.edge_types.append(edge_type)


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


def test_main():

    app = QtApplication()

    controller = CalculatorGraphController()

    controller.registry.register_node_type(NodeType(id='number_input',
                                                    name='Number Input',
                                                    widget_class=NumberInput,
                                                    editor_class=NumberInputEditor,
                                                    model_class=NumberInputModel))
    controller.registry.register_node_type(NodeType(id='slider_input',
                                                    name='Slider Input',
                                                    widget_class=SliderInput,
                                                    editor_class=SliderInputEditor,
                                                    model_class=SliderInputModel))
    controller.registry.register_node_type(NodeType(id='ramp_generator',
                                                    name='Ramp Generator',
                                                    widget_class=RampGenerator,
                                                    editor_class=RampGeneratorEditor,
                                                    model_class=RampGeneratorModel))
    controller.registry.register_node_type(NodeType(id='binary_operator',
                                                    name='Binary Operator',
                                                    widget_class=BinaryOperator,
                                                    editor_class=BinaryOperatorEditor,
                                                    model_class=BinaryOperatorModel))
    controller.registry.register_node_type(NodeType(id='number_output',
                                                    name='Number Output',
                                                    widget_class=NumberOutput,
                                                    editor_class=NumberOutputEditor,
                                                    model_class=NumberOutputModel))
    controller.registry.register_node_type(NodeType(id='graph_output',
                                                    name='Graph Output',
                                                    widget_class=GraphOutput,
                                                    editor_class=GraphOutputEditor,
                                                    model_class=GraphOutputModel))

    controller.registry.register_edge_type(EdgeType(id='default',
                                                    name='Edge',
                                                    widget_class=Edge,
                                                    model_class=model.Edge))

    view = Main(controller=controller)
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    test_main()