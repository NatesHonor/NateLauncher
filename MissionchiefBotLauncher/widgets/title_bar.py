import os
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


def resource_path(relative_path):
    import sys
    import os
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(52)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(12)

        self.logo = QLabel()
        self.logo.setFixedSize(32, 32)
        logo_path = resource_path("icons/missionchief_icon.png")
        if os.path.exists(logo_path):
            self.logo.setPixmap(QPixmap(logo_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.title = QLabel("MissionChief Bot")
        self.title.setStyleSheet("color: #EAEAEA;")
        self.title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(self.logo)
        layout.addWidget(self.title, 1)

        self.minimize_btn = QPushButton()
        self.close_btn = QPushButton()
        self._setup_buttons()
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)

        self.dragging = False
        self.offset = QPoint()

    def _setup_buttons(self):
        self.minimize_btn.setIcon(QIcon(resource_path("icons/minimize.png")))
        self.minimize_btn.setText("" if not self.minimize_btn.icon().isNull() else "_")
        self.minimize_btn.setFixedSize(36, 36)
        self.minimize_btn.setStyleSheet(self._btn_style())
        self.minimize_btn.clicked.connect(self.parent.showMinimized)

        self.close_btn.setIcon(QIcon(resource_path("icons/close.png")))
        self.close_btn.setText("" if not self.close_btn.icon().isNull() else "×")
        self.close_btn.setFixedSize(36, 36)
        self.close_btn.setStyleSheet(self._btn_style("#E05454", "#B84444"))
        self.close_btn.clicked.connect(self.parent.close)

    def _btn_style(self, bg="#303030", hover="#3A3A3A"):
        return f"""
            QPushButton {{
                background-color: {bg};
                color: #EAEAEA;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False
