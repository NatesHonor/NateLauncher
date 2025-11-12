from typing import Optional
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG

_console_instance: Optional[QTextEdit] = None

def set_console_instance(console: QTextEdit):
    global _console_instance
    _console_instance = console

def insert_message(message: str):
    if _console_instance is not None:
        QMetaObject.invokeMethod(
            _console_instance,
            "append",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, message)
        )
    else:
        raise RuntimeError("Console instance not set.")

def send_messages(message: str):
    insert_message(message)
    from handlers.logging import log_to_latest_file
    log_to_latest_file(message)

