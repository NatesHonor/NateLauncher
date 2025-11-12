from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox
import os
from utils.integrity import run_integrity_check

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
        self.config_path = os.path.join("bot", "config.ini")
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.text_edit.setText(f.read())
        else:
            self.text_edit.setReadOnly(True)
            self.text_edit.setText("⚠️ Config.ini not available until setup is complete.")
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
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

        repair_btn = QPushButton("🛠 Repair")
        repair_btn.setFixedHeight(44)
        repair_btn.setStyleSheet("""
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
        repair_btn.clicked.connect(run_integrity_check)
        layout.addWidget(repair_btn)

    def save_config(self):
        if not os.path.exists(self.config_path):
            QMessageBox.warning(self, "Unavailable", "Config.ini is missing. Run setup or repair first.")
            return
        try:
            with open(self.config_path, "w") as f:
                f.write(self.text_edit.toPlainText())
            if self.parent and hasattr(self.parent, "status_bar"):
                self.parent.status_bar.showMessage("Settings saved", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")
