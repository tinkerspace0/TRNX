
from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QFormLayout,
    QDialogButtonBox, QWidget, QHBoxLayout, QFileDialog
)

class NewNodeTemplateDialog(QDialog):
    """
    Dialog to collect a node template name and destination folder.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Node Template")
        self._build_ui()

    def _build_ui(self):
         # Name input
        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("Enter new node name")

        # Folder input + browse button
        self.dir_edit = QLineEdit(self)
        self.dir_edit.setPlaceholderText("Browse or enter destination folder")
        browse_btn = QPushButton("Browse…", self)
        browse_btn.clicked.connect(self._browse_directory)

        container = QWidget()
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self.dir_edit)
        hl.addWidget(browse_btn)

        # Layout
        form = QFormLayout(self)
        form.addRow("Node Name:", self.name_edit)
        form.addRow("Destination Folder:", container)

        # OK / Cancel
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
        directory = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if directory:
            self.dir_edit.setText(directory)

    def get_values(self) -> tuple[str, str]:
        """
        Returns (node_template_name, destination_folder)
        """
        return self.name_edit.text().strip(), self.dir_edit.text().strip()