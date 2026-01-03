import os
import threading
import subprocess
from handlers.console import send_messages
from PyQt6.QtWidgets import QInputDialog, QApplication, QStatusBar
from utils.install import run_install
from utils.integrity import run_integrity_check
from utils import state
from handlers.updates import run_update_check

def update_start_button_state(button, running: bool):
    if running:
        button.setText("Stop Bot")
        button.setStyleSheet("""
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
    else:
        button.setText("Start Bot")
        button.setStyleSheet("""
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

def run_start_logic(status_bar: QStatusBar):
    settings_file = "launcher_settings.ini"
    venv_name = None
    version = None
    if not os.path.exists(settings_file):
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        venv_name, ok = QInputDialog.getText(None, "Set Venv Name", "Enter venv name:")
        if not ok or not venv_name:
            send_messages("No venv name entered, aborting")
            status_bar.showMessage("No venv name entered")
            return
        with open(settings_file, "w") as f:
            f.write(f"[Launcher]\nvenv={venv_name}\n")
        send_messages(f"venv set as {venv_name} and saved to settings")
        status_bar.showMessage(f"venv set as {venv_name}")
    else:
        try:
            with open(settings_file, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
            for line in lines:
                if line.startswith("venv="):
                    venv_name = line.split("=", 1)[1].strip()
        except Exception as e:
            send_messages(f"Failed to read launcher_settings: {e}")
            status_bar.showMessage("Failed to read launcher_settings")
            return
        if not venv_name:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            venv_name, ok = QInputDialog.getText(None, "Set Venv Name", "Enter venv name:")
            if not ok or not venv_name:
                send_messages("No venv name entered, aborting")
                status_bar.showMessage("No venv name entered")
                return
            with open(settings_file, "w") as f:
                f.write(f"[Launcher]\nvenv={venv_name}\n")
            send_messages(f"venv set as {venv_name} and saved to settings")
            status_bar.showMessage(f"venv set to {venv_name}")
    config_file = os.path.join("bot", "config.ini")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
            for line in lines:
                if line.startswith("version="):
                    version = line.split("=", 1)[1].strip()
                    break
        except Exception as e:
            send_messages(f"Failed to read bot/config.ini: {e}")
            status_bar.showMessage("Failed to read bot/config.ini")
    else:
        send_messages("No bot/config.ini found, treating as out of date")
        status_bar.showMessage("Bot is out of date")
    run_update_check(version, config_file, status_bar)
    thread = threading.Thread(target=_start_worker, args=(status_bar, venv_name), daemon=True)
    thread.start()

def _start_worker(status_bar: QStatusBar, venv_name: str):
    send_messages("Checking Launcher Settings")
    status_bar.showMessage("Checking Launcher Settings...")
    created_new = False
    if not os.path.isdir(venv_name):
        send_messages(f"venv directory '{venv_name}' not found, creating...")
        status_bar.showMessage("Installing venv...")
        try:
            process = subprocess.Popen(
                ["python", "-m", "venv", venv_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            state.add_process("venv_setup", process)
            for line in process.stdout:
                send_messages(line.strip())
            process.wait()
            if process.returncode == 0:
                send_messages(f"venv '{venv_name}' created successfully")
                status_bar.showMessage(f"venv '{venv_name}' created successfully")
                created_new = True
            else:
                send_messages(f"venv creation failed with code {process.returncode}")
                status_bar.showMessage("Failed to create venv")
                return
        except Exception as e:
            send_messages(f"Failed to create venv '{venv_name}': {e}")
            status_bar.showMessage("Failed to create venv")
            return
    else:
        send_messages(f"venv '{venv_name}' already exists")
        status_bar.showMessage("venv already exists")
    if created_new:
        run_install(venv_name, status_bar)
    else:
        run_integrity_check(venv_name, status_bar)
