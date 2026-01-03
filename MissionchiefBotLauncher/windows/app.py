import configparser
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget
)

from widgets.glass_frame import GlassFrame
from widgets.title_bar import TitleBar
from windows.sidebar import Sidebar
from windows.settings import ProfileHandler
from handlers.logging import generate_log_file
from handlers.updates import check_updates

from ui.console_panel import ConsolePanel
from ui.version_bar import VersionBar
from logic.region import ensure_region_selected
from logic.window_drag import WindowDragMixin


class MissionChiefBotApp(QMainWindow, WindowDragMixin):
    def __init__(self):
        super().__init__()
        generate_log_file()

        self.is_running = False
        self.update_declined_this_session = False

        self.setWindowTitle("Mission Helper")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        ensure_region_selected(self)
        self._set_geometry()
        self._build_ui()
        self._setup_updates()

    def _set_geometry(self):
        screen = self.screen().availableGeometry()
        self.setGeometry(
            screen.width() // 4,
            screen.height() // 4,
            screen.width() // 2,
            screen.height() // 2
        )

    def _build_ui(self):
        container = GlassFrame(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(14, 14, 14, 14)
        container_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        container_layout.addWidget(self.title_bar)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        self.console_panel = ConsolePanel(self)
        self.profile_handler = ProfileHandler(self)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.console_panel)
        self.stack.addWidget(self.profile_handler)

        self.sidebar = Sidebar(self, self.stack)

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack, 1)

        container_layout.addWidget(content, 1)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(container)
        root_layout.addLayout(VersionBar(self))

        self.setCentralWidget(root)

    def _setup_updates(self):
        check_updates(self)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(lambda: check_updates(self))
        self.update_timer.start(15 * 60 * 1000)