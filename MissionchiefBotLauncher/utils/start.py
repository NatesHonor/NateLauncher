import os
import threading
import subprocess
import requests
from handlers.console import send_messages
from PyQt6.QtWidgets import QInputDialog, QApplication, QStatusBar
from utils.install import run_install
from utils.integrity import run_integrity_check
from utils import state

DEFAULT_VERSION = "1.0"

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
    state.stop_requested = False

    settings_file = "launcher_settings.ini"
    venv_name = None
    version = DEFAULT_VERSION

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
            f.write(f"version={DEFAULT_VERSION}\n")
            f.write(f"venv={venv_name}\n")
        send_messages(f"venv set as {venv_name} and saved to settings")
        status_bar.showMessage(f"venv set as {venv_name}")
    else:
        try:
            with open(settings_file, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
            for line in lines:
                if line.startswith("version="):
                    version = line.split("=", 1)[1].strip()
                elif line.startswith("venv="):
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
                f.write(f"version={DEFAULT_VERSION}\n")
                f.write(f"venv={venv_name}\n")
            send_messages(f"venv set as {venv_name} and saved to settings")
            status_bar.showMessage(f"venv set to {venv_name}")

    try:
        response = requests.get("https://api.natemarcellus.com/updates/missionchieflauncher", params={"current_version": version}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("latest_version")
            update_url = data.get("update_url")
            if latest_version and latest_version != version:
                send_messages(f"Update available: {latest_version}. Downloading...")
                status_bar.showMessage(f"Updating to version {latest_version}...")
                update_response = requests.get(update_url, stream=True)
                update_response.raise_for_status()
                with open("update.zip", "wb") as f:
                    for chunk in update_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                send_messages("Update downloaded. Applying update...")
                status_bar.showMessage("Applying update...")
                import zipfile
                import shutil
                temp_extract = os.path.join(os.getcwd(), "temp_update")
                if os.path.exists(temp_extract):
                    shutil.rmtree(temp_extract)
                os.makedirs(temp_extract, exist_ok=True)
                with zipfile.ZipFile("update.zip", "r") as z:
                    z.extractall(temp_extract)
                for item in os.listdir(temp_extract):
                    s = os.path.join(temp_extract, item)
                    d = os.path.join(os.getcwd(), item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                shutil.rmtree(temp_extract)
                os.remove("update.zip")
                with open(settings_file, "r") as f:
                    lines = f.readlines()
                with open(settings_file, "w") as f:
                    f.write(f"version={latest_version}\n")
                    for line in lines:
                        if not line.startswith("version="):
                            f.write(line)
                send_messages("Update applied successfully.")
                status_bar.showMessage("Update applied successfully.")
    except Exception as e:
        send_messages(f"Update check failed: {e}")
        status_bar.showMessage("Update check failed")

    thread = threading.Thread(target=_start_worker, args=(status_bar, venv_name), daemon=True)
    thread.start()

def _start_worker(status_bar: QStatusBar, venv_name: str):
    if state.stop_requested:
        send_messages("Start aborted by user.")
        status_bar.showMessage("Start aborted.")
        return

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
            state.current_process = process
            for line in process.stdout:
                if state.stop_requested:
                    send_messages("Venv creation aborted by user.")
                    status_bar.showMessage("Venv creation aborted.")
                    process.kill()
                    return
                send_messages(line.strip())
            process.wait()
            state.current_process = None
            if process.returncode == 0:
                send_messages(f"venv '{venv_name}' created successfully")
                status_bar.showMessage(f"venv '{venv_name}' created successfully")
                created_new = True
            else:
                send_messages(f"venv creation failed with code {process.returncode}")
                status_bar.showMessage("Failed to create venv")
                return
        except Exception as e:
            state.current_process = None
            send_messages(f"Failed to create venv '{venv_name}': {e}")
            status_bar.showMessage("Failed to create venv")
            return
    else:
        send_messages(f"venv '{venv_name}' already exists")
        status_bar.showMessage("venv already exists")

    if state.stop_requested:
        send_messages("Operation aborted by user.")
        status_bar.showMessage("Operation aborted.")
        return

    if created_new:
        run_install(venv_name, status_bar)
    else:
        run_integrity_check(venv_name, status_bar)
