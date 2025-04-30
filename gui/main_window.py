from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QApplication,
    QVBoxLayout, QLabel, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from gui.widgets.canvas import Canvas
from gui.dialogs.new_canvas_dialog import NewCanvasDialog
from core.controller import TrenexController

class TrenexMainWindow(QMainWindow):
    def __init__(self, controller: TrenexController):
        super().__init__()
        self.setWindowTitle("Trenex")
        self.resize(1200, 800)
        self.controller = controller
        self._init_ui()

    def _init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.setStyleSheet("QTabWidget::tab-bar { alignment: left; }")
        self.setCentralWidget(self.tabs)
        
        self._add_welcome_tab()
        self._init_menu()

    def _add_welcome_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel(
            "Welcome to Trenex!\n\n"
            "Quick Start: File > New Canvas to begin."
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(lbl)
        self.tabs.addTab(w, "Welcome")

    def _init_menu(self):
        file_menu = self.menuBar().addMenu("File")
        new_act = QAction("New Canvas", self)
        new_act.triggered.connect(self._new_canvas)
        file_menu.addAction(new_act)

    def _new_canvas(self):
        dlg = NewCanvasDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, directory = dlg.get_values()
            if not name or not directory:
                return
            # pass name & directory into your Canvas
            canvas = Canvas(controller=self.controller, name=name, project_dir=directory)
            idx = self.tabs.addTab(canvas, name)
            self.tabs.setCurrentIndex(idx)

    def _close_tab(self, idx: int):
        self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self._add_welcome_tab()
