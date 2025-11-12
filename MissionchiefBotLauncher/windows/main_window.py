from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QFrame, QStatusBar, QStackedWidget
)
from widgets.glass_frame import GlassFrame
from widgets.title_bar import TitleBar
from widgets.action_button import ActionButton
from windows.sidebar_window import Sidebar
from profile_handler import ProfileHandler
from logging_handler import generate_log_file
from start_bot import MainWindow
from console_handler import set_console_instance, send_messages
from stop_bot import stop_bot

class MissionChiefBotApp(QMainWindow):
    generate_log_file()

    def __init__(self):
        super().__init__()
        self.current_view = "home"
        self.is_running = False
        self.process = None
        self.setWindowTitle("MissionChief Bot")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        screen = self.screen().availableGeometry()
        self.setGeometry(
            screen.width() // 4,
            screen.height() // 4,
            screen.width() // 2,
            screen.height() // 2
        )

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

        self.sidebar = Sidebar(self)
        content_layout.addWidget(self.sidebar)

        self.console_panel = QFrame()
        self.console_panel.setObjectName("main_panel")
        self.console_panel.setStyleSheet("background-color: #101010; border-radius: 14px;")
        main_layout = QVBoxLayout(self.console_panel)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        header = QLabel("MissionChief Bot Console")
        header.setStyleSheet("color: #EAEAEA;")
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        main_layout.addWidget(header)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #DADADA;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
                padding: 8px;
                font-family: Consolas, Courier New, monospace;
                font-size: 11pt;
            }
        """)
        main_layout.addWidget(self.console, 1)
        set_console_instance(self.console)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(8)

        self.start_button = ActionButton("Start Bot")
        self.start_button.clicked.connect(self.toggle_start_stop)
        footer.addWidget(self.start_button)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #141414; color: #9A9A9A; border: none;")
        self.status_bar.showMessage("Ready")

        status_container = QFrame()
        status_container.setStyleSheet("background-color: #101010;")
        status_layout = QVBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(0)
        status_layout.addLayout(footer)
        status_layout.addWidget(self.status_bar)
        main_layout.addWidget(status_container)

        self.profile_handler = ProfileHandler(self)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.console_panel)
        self.stack.addWidget(self.profile_handler)
        content_layout.addWidget(self.stack, 1)

        container_layout.addWidget(content, 1)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(container)
        self.setCentralWidget(root)

        self.main_window_instance = MainWindow()
        self.main_window_instance.worker.started.connect(self._store_process)

    def _store_process(self, proc):
        self.process = proc

    def animate_button(self, btn):
        anim = QPropertyAnimation(btn, b"geometry", self)
        r = btn.geometry()
        anim.setDuration(120)
        anim.setStartValue(QRect(r.x(), r.y(), r.width(), r.height()))
        anim.setEndValue(QRect(r.x(), r.y()+2, r.width(), r.height()))
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.finished.connect(lambda: btn.setGeometry(r))
        anim.start()

    def show_settings(self):
        self.sidebar.settings_btn.setText("Home")
        self.sidebar.settings_btn.setIcon(QIcon("icons/home.png"))
        self.stack.setCurrentIndex(1)
        self.current_view = "settings"
        self.sidebar.settings_btn.clicked.disconnect()
        self.sidebar.settings_btn.clicked.connect(self.show_home)

    def show_home(self):
        self.sidebar.settings_btn.setText("Settings")
        self.sidebar.settings_btn.setIcon(QIcon("icons/settings.png"))
        self.stack.setCurrentIndex(0)
        self.current_view = "home"
        self.sidebar.settings_btn.clicked.disconnect()
        self.sidebar.settings_btn.clicked.connect(self.show_settings)

    def toggle_start_stop(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_button.setText("Stop Bot")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #E05454;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                    font-weight: 600;
                    padding: 10px 16px;
                }
                QPushButton:hover { background-color: #EB6666; }
                QPushButton:pressed { background-color: #C94949; }
            """)
            self.status_bar.showMessage("Bot Running")
            self.process = self.main_window_instance.start_bot()
        else:
            self.start_button.setText("Start Bot")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #2E7CF6;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                    font-weight: 600;
                    padding: 10px 16px;
                }
                QPushButton:hover { background-color: #3B86F7; }
                QPushButton:pressed { background-color: #266BE3; }
            """)
            self.status_bar.showMessage("Bot Stopped")
            if self.process is not None:
                self.process = stop_bot(self.process)
            else:
                send_messages("No bot process is currently running.")
            send_messages("Stop command issued from UI.")
        self.animate_button(self.start_button)
