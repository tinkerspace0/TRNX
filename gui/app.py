import sys
from PyQt6.QtWidgets import QApplication
from .main_window import TrenexMainWindow
from core.controller import TrenexController

def main():
    app = QApplication(sys.argv)
    
    # Optionally set a non-native style to help with QSS consistency
    app.setStyle("Fusion")
    
    # Load and apply the dark theme stylesheet from file.
    try:
        with open("gui/assets/dark_theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Failed to load dark_theme.qss:", e)
    
    controller = TrenexController()
    window = TrenexMainWindow(controller)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
