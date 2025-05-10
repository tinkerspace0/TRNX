from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt

from gui.dialogs.import_node_dialog import ImportNodeDialog

from core.controller import TrenexController

class NodePackageManagerPanel(QWidget):
    """
    A dockable panel for listing and importing node packages.
    """
    def __init__(self, controller: TrenexController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # title = QLabel("Node Package Manager")
        # title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(title)

        # List of installed packages
        self.pkg_list = QListWidget()
        layout.addWidget(self.pkg_list)

        # Buttons row
        btn_row = QWidget()
        hl = QHBoxLayout(btn_row)
        hl.setContentsMargins(0,0,0,0)
        install_btn = QPushButton("Import…")
        install_btn.clicked.connect(self.on_import)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_list)
        hl.addWidget(install_btn)
        hl.addWidget(refresh_btn)
        layout.addWidget(btn_row)

        # initial population
        self.refresh_list()

    def refresh_list(self):
        """
        Refresh the package list from the controller.
        """
        self.pkg_list.clear()
        if hasattr(self.controller.npm, "list_nodes"):
            for p in self.controller.npm.list_nodes():
                self.pkg_list.addItem(p)

    def on_import(self):
        """
        Show ImportNodeDialog to pick a file/folder, then import.
        """
        dlg = ImportNodeDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            path = dlg.get_path()
            if not path:
                return
            # Delegate to your controller/npm
            try:
                self.controller.npm.import_node_package(path)
            except:
                # Handle import error
                print(f"Failed to import node package from {path}")
            
            self.refresh_list()
