import sys
from PyQt6.QtWidgets import QApplication
from .main_window import TrenexMainWindow

def main():
    app = QApplication(sys.argv)

    # Load dark theme stylesheet if available
    try:
        with open("gui/assets/dark_theme.qss", "r") as f:
            style = f.read()
            app.setStyleSheet(style)
    except Exception as e:
        print("Could not load stylesheet:", e)

    window = TrenexMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
