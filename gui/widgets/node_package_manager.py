# gui/widgets/node_package_manager.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QInputDialog
from PyQt6.QtCore import Qt

from core.controller import TrenexController
class NodePackageManagerPanel(QWidget):
    """
    A dockable panel for listing and installing node packages.
    """
    def __init__(self, controller: TrenexController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Node Package Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # List of installed packages
        self.pkg_list = QListWidget()
        layout.addWidget(self.pkg_list)

        # Buttons row
        btn_row = QHBoxLayout()
        install_btn = QPushButton("Import")
        install_btn.clicked.connect(self.on_import)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_list)
        btn_row.addWidget(install_btn)
        btn_row.addWidget(refresh_btn)
        layout.addLayout(btn_row)

        # initial population
        self.refresh_list()

    def refresh_list(self):
        """
        Refresh the package list from the controller (stubbed).
        """
        self.pkg_list.clear()
        # For now, stubbed: you might call self.controller.list_packages()
        pkgs = self.controller.npm.list_nodes() if hasattr(self.controller.npm, "list_nodes") else []
        for p in pkgs:
            self.pkg_list.addItem(p)

    def on_import(self):
        """
        Ask for a package name and then install it via the controller (stubbed).
        """
        pkg, ok = QInputDialog.getText(self, "Install Package", "Package name:")
        if ok and pkg:
            # stub: you might call self.controller.install_package(pkg)
            success = getattr(self.controller, "install_package", lambda x: False)(pkg)
            if success:
                self.refresh_list()
