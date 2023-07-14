from PySide6 import QtGui, QtWidgets, QtCore

class GraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.transformationAnchor().AnchorUnderMouse)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        self.setTransformationAnchor(self.transformationAnchor().AnchorUnderMouse)
        if event.angleDelta().y() > 0:
            self.scale(1.1, 1.1)
        else:
            self.scale(0.9, 0.9)
        self.setTransformationAnchor(self.transformationAnchor().AnchorUnderMouse)
