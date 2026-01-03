from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QTextEdit,
    QHBoxLayout, QStatusBar
)

from widgets.action_button import ActionButton
from handlers.console import set_console_instance
from utils.start import update_start_button_state, run_start_logic
from utils.stop_bot import stop_bot


class ConsolePanel(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.setStyleSheet("background-color: #101010; border-radius: 14px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Mission Helper Console")
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #EAEAEA;")
        layout.addWidget(header)

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
        layout.addWidget(self.console, 1)
        set_console_instance(self.console)

        footer = QHBoxLayout()

        self.start_button = ActionButton("Start Bot")
        self.start_button.clicked.connect(self.toggle_start_stop)
        footer.addWidget(self.start_button)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        layout.addLayout(footer)
        layout.addWidget(self.status_bar)

    def toggle_start_stop(self):
        self.parent.is_running = not self.parent.is_running
        update_start_button_state(self.start_button, self.parent.is_running)

        if self.parent.is_running:
            run_start_logic(self.status_bar)
        else:
            stop_bot()
            self.status_bar.showMessage("Bot Stopped")