from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QLabel, QDockWidget, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from gui.widgets.canvas import Canvas
from gui.widgets.node_package_manager import NodePackageManagerPanel
from gui.dialogs.new_canvas_dialog import NewCanvasDialog
from gui.dialogs.new_node_template_dialog import NewNodeTemplateDialog
from core.controller import TrenexController

class TrenexMainWindow(QMainWindow):
    def __init__(self, controller: TrenexController):
        super().__init__()
        self.setWindowTitle("Trenex")
        self.resize(1200, 800)
        
        self.controller = controller
        # Keep track of all dock widgets by name
        self._docks: dict[str, QDockWidget] = {}
        
        self._init_ui()

    def _init_ui(self):
        # — Central Tab Widget for canvases —
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.setStyleSheet("QTabWidget::tab-bar { alignment: left; }")
        self.setCentralWidget(self.tabs)
        self._add_welcome_tab()
        
        # — Menus —
        menubar = self.menuBar()
        # File menu
        file_menu = menubar.addMenu("File")
        new_act = QAction("New Canvas", self)
        new_act.triggered.connect(self._new_canvas)
        file_menu.addAction(new_act)
        
        new_node_act = QAction("New Node", self)
        new_node_act.triggered.connect(self._new_node_template)
        file_menu.addAction(new_node_act)
        

        # View menu
        self.view_menu = menubar.addMenu("View")
        
        # — Dockable Panels —
        # Node Package Manager
        npm_panel = NodePackageManagerPanel(controller=self.controller)
        npm_dock = QDockWidget("Node Package Manager", self)
        npm_dock.setWidget(npm_panel)
        npm_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        # register it under 'View' menu
        self.register_dock(npm_dock, "Node Package Manager", Qt.DockWidgetArea.LeftDockWidgetArea)

    def register_dock(self, dock: QDockWidget, name: str, area: Qt.DockWidgetArea):
        """
        Add a QDockWidget to the main window and create a corresponding
        toggle action under the View menu.
        """
        # 1. Add to main window in the given dock area
        self.addDockWidget(area, dock)
        # 2. Keep reference
        self._docks[name] = dock
        # 3. Create a checkable menu action
        act = QAction(name, self, checkable=True)
        act.setChecked(dock.isVisible())
        # toggling the menu action shows/hides the dock
        act.toggled.connect(dock.setVisible)
        # when the dock is shown/hidden by other means, sync the action
        dock.visibilityChanged.connect(lambda vis, a=act: a.setChecked(vis))
        # 4. Add to View menu
        self.view_menu.addAction(act)

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

    def _new_canvas(self):
        dlg = NewCanvasDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, directory = dlg.get_values()
            if not name or not directory:
                return
            canvas = Canvas(
                controller=self.controller,
                name=name,
                project_dir=directory
            )
            idx = self.tabs.addTab(canvas, name)
            self.tabs.setCurrentIndex(idx)

    def _close_tab(self, idx: int):
        self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self._add_welcome_tab()

    def _new_node_template(self):
        dlg = NewNodeTemplateDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            node_name, node_des_dir = dlg.get_values()
            if not node_name or not node_des_dir:
                return  # missing input
            try:
                # Call the controller's npm method
                self.controller.npm.create_node_template(node_des_dir, node_name)
                self.statusBar().showMessage(
                    f"Created new node: '{node_name}' in {node_des_dir}", 3000
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error Creating Template",
                    f"Could not create node template:\n{e}"
                )