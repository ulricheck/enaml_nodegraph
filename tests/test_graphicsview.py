import enaml
from enaml.qt.qt_application import QtApplication


def test_main():
    with enaml.imports():
        from graphicsview_widget import Main

    app = QtApplication()

    view = Main()
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    test_main()