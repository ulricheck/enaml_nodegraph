import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import enaml
from enaml.qt.qt_application import QtApplication


from graph_calculator.registry import NodeType, EdgeType
from graph_calculator.controller import CalculatorGraphController

from graph_calculator.model import (NumberInputModel, SliderInputModel, RampGeneratorModel, BinaryOperatorModel,
                                    NumberOutputModel, GraphOutputModel, EdgeModel)

with enaml.imports():
    from graph_calculator.views.main_view import Main
    from graph_calculator.views.item_widgets import (InputNode, RampGenerator, BinaryOperator,
                                                     NumberOutput, GraphOutput, Edge)
    from graph_calculator.views.item_widgets import (InputEditor, RampGeneratorEditor, BinaryOperatorEditor,
                                                     NumberOutputEditor, GraphOutputEditor)



def main():

    app = QtApplication()

    controller = CalculatorGraphController()

    controller.registry.register_node_type(NodeType(id='number_input',
                                                    name='Number Input',
                                                    widget_class=InputNode,
                                                    editor_class=InputEditor,
                                                    model_class=NumberInputModel))
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
                                                    model_class=EdgeModel))

    view = Main(controller=controller)
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    main()