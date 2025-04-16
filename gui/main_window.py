from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt

from gui.widgets.session_panel import SessionPanel
from gui.widgets.node_editor import NodeEditor
from gui.widgets.log_panel import LogPanel


from core.controller import TrenexController

class TrenexMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trenex")
        self.resize(1200, 800)
        
        # Instantiate our Trenex Controller
        self.trenex = TrenexController()
        
        self.init_ui()

    def init_ui(self):
        # Create a container widget and layout
        container = QWidget()
        main_layout = QVBoxLayout(container)

        # Create a horizontal splitter for the session panel and node editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create the session panel on the left
        self.session_panel = SessionPanel(backend=self.trenex, parent=self)
        splitter.addWidget(self.session_panel)
        splitter.setStretchFactor(0, 1)

        # Create the node editor widget for the center area
        self.node_editor = NodeEditor()
        splitter.addWidget(self.node_editor)
        splitter.setStretchFactor(1, 4)

        main_layout.addWidget(splitter)

        # # Create the log panel at the bottom
        # self.log_panel = LogPanel()
        # main_layout.addWidget(self.log_panel)

        self.setCentralWidget(container)

    # def log(self, message):
        # self.log_panel.append_log(message)
