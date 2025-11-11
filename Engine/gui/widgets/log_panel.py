from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

    def append_log(self, message):
        self.log_output.append(message)
