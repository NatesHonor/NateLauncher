from typing import Optional
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QTimer

_console_instance: Optional[QTextEdit] = None

def set_console_instance(console: QTextEdit):
    global _console_instance
    _console_instance = console

def insert_message(message: str):
    if _console_instance is not None:
        QTimer.singleShot(0, lambda: _console_instance.append(message))
    else:
        raise RuntimeError("Console instance not set.")

def send_messages(message: str):
    insert_message(message)
    from logging_handler import log_to_latest_file
    log_to_latest_file(message)
