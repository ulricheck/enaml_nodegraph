import logging
import networkx as nx

from atom.api import (Bool, Int, Enum, List, Property, Event, ForwardInstance, observe)

from enaml_nodegraph import model

log = logging.getLogger(__name__)


def _import_graph_calculator_controller():
    from .controller import CalculatorGraphController
    return CalculatorGraphController


class ExecutableGraph(model.Graph):
    controller = ForwardInstance(_import_graph_calculator_controller)
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
        attrs = {'value': Int().tag(display_name='Value')}
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
        attrs = {'value': Int().tag(display_name='Value'),
                 'min_value': Int().tag(display_name='Min Value'),
                 'max_value': Int().tag(display_name='Max Value'),
                 'step': Int().tag(display_name='Step'),
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
        attrs = {'is_running': Bool().tag(display_name='Is Running'),
                 'interval': Int(100).tag(display_name='Interval'),
                 'min_value': Int(0).tag(display_name='Min Value'),
                 'max_value': Int(10).tag(display_name='Max Value'),
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
        attrs = {'value': Int().tag(display_name='Value')}
        return type("NumberOutputAttributes", (model.Attributes,), attrs)()

    def _default_inputs(self):
        return [InputSocket(name="value", degree=1, data_type="int")]

    def set_value(self, key, value):
        setattr(self.attributes, key, value)

    def update(self):
        pass


class GraphOutputModel(model.Node):

    def _default_attributes(self):
        attrs = {'values': List(Int()).tag(display_name='Values'),
                 'max_entries': Int().tag(display_name='Max Entries'),
                 }
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
        attrs = {'operator': Enum('add', 'sub', 'mul', 'div').tag(display_name='Operator')}
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


class EdgeModel(model.Edge):
    pass