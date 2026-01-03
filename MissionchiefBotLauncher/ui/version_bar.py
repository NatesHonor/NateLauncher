import configparser
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QToolButton


class VersionBar(QHBoxLayout):
    def __init__(self, parent):
        super().__init__()
        self.setContentsMargins(0, 0, 8, 4)
        self.setSpacing(4)

        config = configparser.ConfigParser()
        config.read("launcher_settings.ini")
        version = config.get("Launcher", "version", fallback="0.0.0")

        self.addStretch()

        label = QLabel(f"v{version}")
        label.setStyleSheet("color: #9A9A9A; font-size: 9pt;")

        refresh = QToolButton()
        refresh.setIcon(QIcon.fromTheme("view-refresh"))
        refresh.setToolTip("Checks for updates every hour")

        self.addWidget(label)
        self.addWidget(refresh)