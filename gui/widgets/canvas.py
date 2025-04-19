# gui/widgets/canvas.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from core.controller import TrenexController
from core.trnx import TrenexCanvas

class Canvas(QWidget):
    def __init__(self, controller: TrenexController, name: str, project_dir: str, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.canvas = TrenexCanvas(name=name, project_dir=project_dir)
        self.setWindowTitle(name)
        
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # layout.addWidget(label)
