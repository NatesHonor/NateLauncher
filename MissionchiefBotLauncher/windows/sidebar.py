import os
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

def resource_path(relative_path):
    import sys
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class Sidebar(QFrame):
    def __init__(self, parent, stack):
        super().__init__()
        self.parent = parent
        self.stack = stack
        self.setFixedWidth(220)
        self.setStyleSheet("background-color: #121212; border-radius: 14px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        user_block = QFrame()
        user_block.setStyleSheet("background-color: #1E1E1E; border-radius: 12px;")
        user_layout = QHBoxLayout(user_block)
        user_layout.setContentsMargins(10, 10, 10, 10)

        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar_path = resource_path("icons/user_icon.png")
        if os.path.exists(avatar_path):
            avatar.setPixmap(QPixmap(avatar_path).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        name_label = QLabel("User")
        name_label.setStyleSheet("color: #EAEAEA;")
        name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        user_layout.addWidget(avatar)
        user_layout.addWidget(name_label, 1)
        layout.addWidget(user_block)

        self.settings_btn = self._make_btn("Settings", resource_path("icons/settings.png"))
        self.signout_btn = self._make_btn("Sign Out", resource_path("icons/signout.png"))
        self.exit_btn = self._make_btn("Exit", resource_path("icons/close.png"))


        self.settings_btn.clicked.connect(self.show_settings)
        self.exit_btn.clicked.connect(parent.close)

        layout.addWidget(self.settings_btn)
        layout.addWidget(self.signout_btn)
        layout.addStretch(1)
        layout.addWidget(self.exit_btn)

    def _make_btn(self, text, icon):
        btn = QPushButton(text)
        if icon and os.path.exists(icon):
            btn.setIcon(QIcon(icon))
            btn.setIconSize(QSize(18, 18))
        btn.setFixedHeight(40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #202020;
                color: #CFCFCF;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #2A2A2A;
            }
        """)
        return btn

    def show_settings(self):
        self.settings_btn.setText("Home")
        self.settings_btn.setIcon(QIcon(resource_path("icons/home.png")))
        self.stack.setCurrentIndex(1)
        self.settings_btn.clicked.disconnect()
        self.settings_btn.clicked.connect(self.show_home)

    def show_home(self):
        self.settings_btn.setText("Settings")
        self.settings_btn.setIcon(QIcon(resource_path("icons/settings.png")))
        self.stack.setCurrentIndex(0)
        self.settings_btn.clicked.disconnect()
        self.settings_btn.clicked.connect(self.show_settings)
