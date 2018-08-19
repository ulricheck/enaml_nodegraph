import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import enaml
from enaml.qt.qt_application import QtApplication


from graph_calculator.registry import NodeType, EdgeType
from graph_calculator.controller import CalculatorGraphController

from graph_calculator.model import (IntegerInputModel, FloatInputModel, TextInputModel, RampGeneratorModel,
                                    UnaryOperatorModel, BinaryOperatorModel,
                                    IntegerOutputModel, FloatOutputModel, TextOutputModel, GraphOutputModel,
                                    IntegerFloatConverter, FloatIntegerConverter, IntegerTextConverter, FloatTextConverter,
                                    EdgeModel)

with enaml.imports():
    from graph_calculator.views.main_view import Main
    from graph_calculator.views.item_widgets import (AutoNode, RampGenerator, Edge)
    from graph_calculator.views.attribute_editors import (AttributeEditor, OutputEditor, GraphOutputEditor)



def main():

    app = QtApplication()

    controller = CalculatorGraphController()

    controller.registry.register_node_type(NodeType(id='integer_input',
                                                    name='Set Integer',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=IntegerInputModel))
    controller.registry.register_node_type(NodeType(id='float_input',
                                                    name='Set Float',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=FloatInputModel))
    controller.registry.register_node_type(NodeType(id='text_input',
                                                    name='Set Text',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=TextInputModel))

    controller.registry.register_node_type(NodeType(id='ramp_generator',
                                                    name='Ramp Generator',
                                                    widget_class=RampGenerator,
                                                    editor_class=AttributeEditor,
                                                    model_class=RampGeneratorModel))

    controller.registry.register_node_type(NodeType(id='integer_output',
                                                    name='Display Integer',
                                                    widget_class=AutoNode,
                                                    editor_class=OutputEditor,
                                                    model_class=IntegerOutputModel))
    controller.registry.register_node_type(NodeType(id='float_output',
                                                    name='Display Float',
                                                    widget_class=AutoNode,
                                                    editor_class=OutputEditor,
                                                    model_class=FloatOutputModel))
    controller.registry.register_node_type(NodeType(id='text_output',
                                                    name='Display Text',
                                                    widget_class=AutoNode,
                                                    editor_class=OutputEditor,
                                                    model_class=TextOutputModel))

    controller.registry.register_node_type(NodeType(id='graph_output',
                                                    name='Graph Output',
                                                    widget_class=AutoNode,
                                                    editor_class=GraphOutputEditor,
                                                    model_class=GraphOutputModel))

    controller.registry.register_node_type(NodeType(id='binary_operator',
                                                    name='Binary Operator',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=BinaryOperatorModel))
    controller.registry.register_node_type(NodeType(id='unary_operator',
                                                    name='Unary Operator',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=UnaryOperatorModel))

    controller.registry.register_node_type(NodeType(id='int2float',
                                                    name='Int->Float',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=IntegerFloatConverter))
    controller.registry.register_node_type(NodeType(id='float2int',
                                                    name='Float->Int',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=FloatIntegerConverter))
    controller.registry.register_node_type(NodeType(id='int2text',
                                                    name='Int->Text',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=IntegerTextConverter))
    controller.registry.register_node_type(NodeType(id='float2text',
                                                    name='Float->Text',
                                                    widget_class=AutoNode,
                                                    editor_class=AttributeEditor,
                                                    model_class=FloatTextConverter))

    controller.registry.register_edge_type(EdgeType(id='default',
                                                    name='Edge',
                                                    widget_class=Edge,
                                                    model_class=EdgeModel))

    view = Main(controller=controller)
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    main()