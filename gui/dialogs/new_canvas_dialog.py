from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QFileDialog,
    QDialogButtonBox, QFormLayout, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt

class NewCanvasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Canvas")
        
        self.name_edit = QLineEdit(self)
        self.dir_edit = QLineEdit(self)
        self.dir_edit.setReadOnly(True)
        browse_btn = QPushButton("Browse…", self)
        browse_btn.clicked.connect(self._browse_directory)
        
        form = QFormLayout(self)
        form.addRow("Canvas Name:", self.name_edit)
        h = QWidget()
        hl = QHBoxLayout(h)
        hl.setContentsMargins(0,0,0,0)
        hl.addWidget(self.dir_edit)
        hl.addWidget(browse_btn)
        form.addRow("Project Directory:", h)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self.setLayout(form)

    def _browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.dir_edit.setText(directory)

    def get_values(self):
        return self.name_edit.text().strip(), self.dir_edit.text().strip()
