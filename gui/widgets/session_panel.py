from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QFileDialog

class SessionPanel(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.backend = controller
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Active Sessions")
        layout.addWidget(title)

        self.session_list = QListWidget()
        self.session_list.setMinimumWidth(200)
        layout.addWidget(self.session_list)

        self.create_btn = QPushButton("Create Bot")
        self.create_btn.clicked.connect(self.create_bot)
        layout.addWidget(self.create_btn)

        self.stop_btn = QPushButton("Stop Selected Bot")
        self.stop_btn.clicked.connect(self.stop_selected_bot)
        layout.addWidget(self.stop_btn)

    def create_bot(self):
        # Open a file dialog to simulate bot name entry
        name, ok = QFileDialog.getSaveFileName(self, "Create Bot Session", "", "Bot Files (*.bot)")
        if ok and name:
            bot_name = name.split("/")[-1]
            self.backend.create_bot(bot_name)
            self.session_list.addItem(bot_name)
            if self.parent_window:
                self.parent_window.log(f"Created bot: {bot_name}")

    def stop_selected_bot(self):
        selected_item = self.session_list.currentItem()
        if selected_item:
            bot_name = selected_item.text()
            self.backend.stop_bot(bot_name)
            self.session_list.takeItem(self.session_list.row(selected_item))
            if self.parent_window:
                self.parent_window.log(f"Stopped bot: {bot_name}")
