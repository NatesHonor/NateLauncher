from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt

class ActionButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2E7CF6;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #3B86F7;
            }
            QPushButton:pressed {
                background-color: #266BE3;
            }
        """)
