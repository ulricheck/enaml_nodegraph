import logging
import math
import networkx as nx

from atom.api import (Atom, Value, Bool, Int, Float, Str, Unicode, Enum, List, Property, Event, ForwardInstance, observe)

from enaml_nodegraph import model

log = logging.getLogger(__name__)


TYPE_MAP = {
    'int': Int,
    'float': Float,
    'text': Unicode,
}


def _import_graph_calculator_controller():
    from .controller import CalculatorGraphController
    return CalculatorGraphController


class ExecutableGraph(model.Graph):
    controller = ForwardInstance(_import_graph_calculator_controller)
    nxgraph = Property(lambda self: self._get_nxgraph(), cached=True)

    topologyChanged = Event()
    valuesChanged = Event()
    attributesChanged = Event()

    def _get_nxgraph(self):
        g = nx.MultiDiGraph()
        for node in self.nodes:
            g.add_node(node.id,
                       id=node.id,
                       name=node.name)
        for edge in self.edges:
            g.add_edge(edge.start_socket.node.id, edge.end_socket.node.id,
                       id=edge.id,
                       source_socket=edge.start_socket.name,
                       target_socket=edge.end_socket.name)
        return g

    def _observe_topologyChanged(self, change):
        self.get_member('nxgraph').reset(self)
        self.execute_graph()

    def _observe_valuesChanged(self, change):
        self.execute_graph()

    def _observe_attributesChanged(self, change):
        self.execute_graph()

    def execute_graph(self):
        for node_id in nx.topological_sort(self.nxgraph):
            self.node_dict[node_id].update()


class OutputSocket(model.Socket):

    def propagate_change(self, value):
        for edge in self.edges:
            if edge.end_socket is not None:
                edge.end_socket.receive_value(value)


class InputSocket(model.Socket):

    def receive_value(self, value):
        self.node.set_value(self.name, value)


class AttrSpec(Atom):
    name = Str()
    display_name = Unicode()
    data_type = Str()
    default = Value()
    attr_type = Enum('property', 'input', 'output')

    def _default_attr_type(self):
        return 'property'

    def _default_display_name(self):
        return name


def make_attributes(parent, spec):
    cls = type(parent)

    attrs = {}
    for s in spec:
        attrs[s.name] = TYPE_MAP[s.data_type](s.default).tag(display_name=s.display_name, attr_type=s.attr_type)

    obj = type("%sAttributes" % cls.__name__, (model.Attributes,), attrs)()

    for s in spec:
        if s.attr_type in ['output', 'property']:
            obj.observe(s.name, parent.notify_change)

    return obj


class NodeBase(model.Node):

    _spec = List(AttrSpec)

    def _default_attributes(self):
        return make_attributes(self, self._spec)

    def _default_inputs(self):
        return [InputSocket(name=s.name, data_type=s.data_type) for s in self._spec if s.attr_type == 'input']

    def _default_outputs(self):
        return [OutputSocket(name=s.name, data_type=s.data_type) for s in self._spec if s.attr_type == 'output']


class InputNode(NodeBase):

    def notify_change(self, change):
        if self.graph is not None:
            self.graph.attributesChanged()

    def update(self):
        for output in self.outputs:
            output.propagate_change(getattr(self.attributes, output.name))


class OutputNode(NodeBase):

    def set_value(self, key, value):
        setattr(self.attributes, key, value)

    def update(self):
        pass


class IntegerInputModel(InputNode):

    def _default__spec(self):
        return [AttrSpec(name='value', display_name='Value', data_type='int', default=0, attr_type='output')]


class FloatInputModel(InputNode):

    def _default__spec(self):
        return [AttrSpec(name='value', display_name='Value', data_type='float', default=0., attr_type='output')]


class TextInputModel(InputNode):

    def _default__spec(self):
        return [AttrSpec(name='value', display_name='Value', data_type='text', default='', attr_type='output')]


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

    @observe("attributes.is_running",
             "attributes.interval",
             "attributes.min_value",
             "attributes.max_value")
    def _handle_attribute_change(self, change):
        if self.graph is not None:
            self.graph.attributesChanged()

    @observe("value")
    def _handle_value_change(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        self.output_dict['value'].propagate_change(self.value)


class IntegerOutputModel(OutputNode):

    def _default__spec(self):
        return [AttrSpec(name='value', display_name='Value', data_type='int', default=0, attr_type='input')]


class FloatOutputModel(OutputNode):

    def _default__spec(self):
        return [AttrSpec(name='value', display_name='Value', data_type='float', default=0., attr_type='input')]


class TextOutputModel(OutputNode):

    def _default__spec(self):
        return [AttrSpec(name='value', display_name='Value', data_type='text', default='', attr_type='input')]


class GraphOutputModel(model.Node):

    def _default_attributes(self):
        attrs = {'values': List(Float()).tag(display_name='Values'),
                 'max_entries': Int().tag(display_name='Max Entries'),
                 }
        return type("GraphOutputAttributes", (model.Attributes,), attrs)()

    def _default_inputs(self):
        return [InputSocket(name="value", degree=1, data_type="float")]

    def set_value(self, key, value):
        start_idx = max(0, len(self.attributes.values)-self.attributes.max_entries+1)
        val = self.attributes.values[start_idx:]
        val.append(value)
        self.attributes.values = val

    def update(self):
        pass


class UnaryOperatorModel(model.Node):

    def _default_attributes(self):
        attrs = {'operator': Enum('deg2rad', 'rad2deg', 'sin', 'cos', 'log10').tag(display_name='Operator')}
        return type("UnaryOperatorAttributes", (model.Attributes,), attrs)()

    in1 = Float()

    result = Float()

    def _default_inputs(self):
        return [InputSocket(name="in1", degree=1, data_type="float")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="float")]

    def set_value(self, key, value):
        setattr(self, key, value)

    @observe("attributes.operator")
    def _handle_operator_change(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        op = self.attributes.operator

        try:
            if op == 'deg2rad':
                self.result = math.radians(self.in1)
            elif op == 'rad2deg':
                self.result = math.degrees(self.in1)
            elif op == 'sin':
                self.result = math.sin(self.in1)
            elif op == 'cos':
                self.result = math.cos(self.in1)
            elif op == 'log10':
                self.result = math.log10(self.in1)
            else:
                log.warning("invalid operator: %s" % op)
        except Exception as e:
            log.error(e)

        self.output_dict['result'].propagate_change(self.result)


class BinaryOperatorModel(model.Node):

    def _default_attributes(self):
        attrs = {'operator': Enum('add', 'sub', 'mul', 'div').tag(display_name='Operator')}
        return type("BinaryOperatorAttributes", (model.Attributes,), attrs)()

    in1 = Float()
    in2 = Float()

    result = Float()

    def _default_inputs(self):
        return [InputSocket(name="in1", degree=1, data_type="float"),
                InputSocket(name="in2", degree=1, data_type="float")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="float")]

    def set_value(self, key, value):
        setattr(self, key, value)

    @observe("attributes.operator")
    def _handle_operator_change(self, change):
        if self.graph is not None:
            self.graph.valuesChanged()

    def update(self):
        op = self.attributes.operator

        try:
            if op == 'add':
                self.result = self.in1 + self.in2
            elif op == 'sub':
                self.result = self.in1 - self.in2
            elif op == 'mul':
                self.result = self.in1 * self.in2
            elif op == 'div':
                self.result = int(self.in1 / self.in2)
            else:
                log.warning("invalid operator: %s" % op)
        except Exception as e:
            log.error(e)

        self.output_dict['result'].propagate_change(self.result)


class IntegerFloatConverter(model.Node):
    in1 = Int()
    result = Float()

    def _default_inputs(self):
        return [InputSocket(name="in1", degree=1, data_type="int")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="float")]

    def set_value(self, key, value):
        setattr(self, key, value)

    def update(self):
        self.result = float(self.in1)
        self.output_dict['result'].propagate_change(self.result)


class FloatIntegerConverter(model.Node):
    in1 = Float()
    result = Int()

    def _default_attributes(self):
        attrs = {'method': Enum('round', 'floor', 'ceil').tag(display_name='Method')}
        return type("FloatIntegerConverterAttributes", (model.Attributes,), attrs)()

    def _default_inputs(self):
        return [InputSocket(name="in1", degree=1, data_type="float")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="int")]

    def set_value(self, key, value):
        setattr(self, key, value)

    def update(self):
        op = self.attributes.method

        try:
            if op == 'round':
                self.result = int(self.in1)
            elif op == 'floor':
                self.result = math.floor(self.in1)
            elif op == 'ceil':
                self.result = math.ceil(self.in1)
            else:
                log.warning("invalid method: %s" % op)
        except Exception as e:
            log.error(e)

        self.output_dict['result'].propagate_change(self.result)


class IntegerTextConverter(model.Node):
    in1 = Int()
    result = Unicode()

    def _default_inputs(self):
        return [InputSocket(name="in1", degree=1, data_type="int")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="text")]

    def set_value(self, key, value):
        setattr(self, key, value)

    def update(self):
        self.result = "%d" % self.in1
        self.output_dict['result'].propagate_change(self.result)


class FloatTextConverter(model.Node):
    in1 = Float()
    result = Unicode()

    def _default_inputs(self):
        return [InputSocket(name="in1", degree=1, data_type="float")]

    def _default_outputs(self):
        return [OutputSocket(name="result", data_type="text")]

    def set_value(self, key, value):
        setattr(self, key, value)

    def update(self):
        self.result = "%.3f" % self.in1
        self.output_dict['result'].propagate_change(self.result)


class EdgeModel(model.Edge):
    pass