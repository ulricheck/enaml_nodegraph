import pytest


from enaml_nodegraph.model import Edge, Socket, SocketType, Node, Graph



def test_simple_graph():
    print("Simple Graph Test")

    n1 = Node(name="node1", 
              inputs=[Socket(name="in1", data_type="a"), Socket(name="in2", data_type="a")],
              outputs=[Socket(name="out1", degree=1, data_type="a"), Socket(name="out2", data_type="a")],
              )

    assert len(n1.inputs) == 2
    assert n1.inputs[0].node is n1
    assert n1.inputs[0].socket_type == SocketType.INPUT
    assert n1.inputs[1].node is n1
    assert n1.inputs[1].socket_type == SocketType.INPUT

    assert len(n1.outputs) == 2
    assert n1.outputs[0].node is n1
    assert n1.outputs[0].socket_type == SocketType.OUTPUT
    assert n1.outputs[1].node is n1
    assert n1.outputs[1].socket_type == SocketType.OUTPUT

    n2 = Node(name="node2", 
              inputs=[Socket(name="in1", data_type="a"), Socket(name="in2", data_type="a")],
              outputs=[Socket(name="out1", data_type="a"), Socket(name="out2", data_type="b")],
              )


    assert len(n2.inputs) == 2
    assert n2.inputs[0].node is n2
    assert n2.inputs[0].socket_type == SocketType.INPUT
    assert n2.inputs[0].index == 0
    assert n2.inputs[1].node is n2
    assert n2.inputs[1].socket_type == SocketType.INPUT
    assert n2.inputs[1].index == 1

    assert len(n2.outputs) == 2
    assert n2.outputs[0].node is n2
    assert n2.outputs[0].socket_type == SocketType.OUTPUT
    assert n2.outputs[0].index == 0
    assert n2.outputs[1].node is n2
    assert n2.outputs[1].socket_type == SocketType.OUTPUT
    assert n2.outputs[1].index == 1

    e1 = Edge(start_socket=n1.outputs[0], end_socket=n2.inputs[0])

    assert e1.start_socket.node is n1
    assert e1.end_socket.node is n2
    assert len(n1.outputs[0].edges) == 1
    assert len(n2.inputs[0].edges) == 1

    e2 = Edge(start_socket=n1.outputs[1], end_socket=n2.inputs[0])

    assert e2.start_socket.node is n1
    assert e2.end_socket.node is n2
    assert len(n1.outputs[1].edges) == 1
    assert len(n2.inputs[0].edges) == 2

    g = Graph(name="test graph",
              nodes=[n1,n2],
              edges=[e1,e2],
              )

    assert n1.graph is g
    assert n2.graph is g
    assert e1.graph is g
    assert e2.graph is g

    e3 = Edge(start_socket=n2.outputs[0], end_socket=n1.inputs[1])
    g.edges.append(e3)

    assert e3.graph is g

    assert e3.start_socket.node is n2
    assert e3.end_socket.node is n1

    # check degree=1 on node1:out1
    assert n1.outputs[0].can_connect(n2.inputs[0]) == False
    with pytest.raises(ValueError):
        e4 = Edge(start_socket=n1.outputs[0], end_socket=n2.inputs[0])
    
    # check for compatible data types
    e4_half = Edge(start_socket=n2.outputs[1])
    assert n2.inputs[1].can_connect(e4_half) == False
    assert n2.inputs[1].can_connect(n2.outputs[1]) == False
    with pytest.raises(TypeError):
        e4 = Edge(start_socket=n2.outputs[1], end_socket=n2.inputs[1])
    