from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QFileDialog,
    QDialogButtonBox, QFormLayout, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt

class ImportNodeDialog(QDialog):
    """
    Dialog to choose a node package file or directory to import.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Node Package")
        self._build_ui()

    def _build_ui(self):
        self.path_edit = QLineEdit(self)
        browse_btn = QPushButton("Browse…", self)
        browse_btn.clicked.connect(self._browse)

        # Layout for path + browse
        container = QWidget()
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0,0,0,0)
        hl.addWidget(self.path_edit)
        hl.addWidget(browse_btn)

        form = QFormLayout(self)
        form.addRow("Select File or Folder:", container)

        # OK / Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.setLayout(form)

    def _browse(self):
        # Let user choose file or directory
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Node File")
        if not file_path:
            dir_path = QFileDialog.getExistingDirectory(self, "Or Select Node Directory")
            file_path = dir_path if dir_path else ""
        if file_path:
            self.path_edit.setText(file_path)

    def get_path(self) -> str:
        return self.path_edit.text().strip()
