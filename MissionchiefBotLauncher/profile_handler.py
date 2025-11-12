from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox
import os

class ProfileHandler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 8)
        layout.setSpacing(12)

        header = QTextEdit()
        header.setReadOnly(True)
        header.setText("⚙️ Edit Config.ini")
        header.setStyleSheet("color: #EAEAEA; background: transparent; border: none; font-weight: bold; font-size: 12pt;")
        header.setFixedHeight(40)
        layout.addWidget(header)

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #DADADA;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 11pt;
            }
        """)
        config_path = os.path.join("bot", "config.ini")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.text_edit.setText(f.read())
        layout.addWidget(self.text_edit, 1)

        save_btn = QPushButton("💾 Save")
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(lambda: self.save_config(config_path))
        layout.addWidget(save_btn)

    def save_config(self, config_path):
        try:
            with open(config_path, "w") as f:
                f.write(self.text_edit.toPlainText())
            if self.parent and hasattr(self.parent, "status_bar"):
                self.parent.status_bar.showMessage("Settings saved", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")
