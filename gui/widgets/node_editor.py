from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class NodeEditor(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Node Editor Placeholder")
        layout.addWidget(label)
