import sys
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QFrame, QStatusBar, QStackedWidget
)
from widgets.glass_frame import GlassFrame
from widgets.title_bar import TitleBar
from widgets.action_button import ActionButton
from windows.sidebar import Sidebar
from windows.settings import ProfileHandler
from handlers.logging import generate_log_file
from handlers.console import set_console_instance
from utils.start import update_start_button_state, run_start_logic

class MissionChiefBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        generate_log_file()
        self.is_running = False
        self.drag_offset = None
        self.setWindowTitle("MissionChief Bot")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        screen = self.screen().availableGeometry()
        self.setGeometry(screen.width() // 4, screen.height() // 4, screen.width() // 2, screen.height() // 2)

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

        self.console_panel = QFrame()
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
                font-size: 8pt;
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

        self.sidebar = Sidebar(self, self.stack)
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack, 1)

        container_layout.addWidget(content, 1)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(container)
        self.setCentralWidget(root)

    def toggle_start_stop(self):
        self.is_running = not self.is_running
        update_start_button_state(self.start_button, self.is_running)

        if self.is_running:
            run_start_logic(self.status_bar)

    def animate_button(self, btn):
        anim = QPropertyAnimation(btn, b"geometry", self)
        r = btn.geometry()
        anim.setDuration(120)
        anim.setStartValue(QRect(r.x(), r.y(), r.width(), r.height()))
        anim.setEndValue(QRect(r.x(), r.y() + 2, r.width(), r.height()))
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.finished.connect(lambda: btn.setGeometry(r))
        anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            gp = event.globalPosition().toPoint()
            self.move(gp - self.drag_offset)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { background-color: #101010; }")
    window = MissionChiefBotApp()
    window.show()
    sys.exit(app.exec())
