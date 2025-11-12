import sys
from PyQt6.QtWidgets import QApplication, QWidget
from windows.main_window import MissionChiefBotApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #101010;
        }
    """)
    window = MissionChiefBotApp()
    window.show()
    sys.exit(app.exec())
