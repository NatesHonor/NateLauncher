import os
import sys
import shutil

import zipfile
import requests
import subprocess
import configparser
from PyQt6.QtWidgets import QMessageBox
from handlers.console import send_messages

API_URL = "https://api.natemarcellus.com/updates/missionlauncher"
INI_FILE = "launcher_settings.ini"

def check_updates(parent):
    try:
        if getattr(parent, "update_declined_this_session", False):
            return

        config = configparser.ConfigParser()
        config.read(INI_FILE)
        local_version = config.get("Launcher", "version")

        resp = requests.get(API_URL, timeout=5)
        data = resp.json()

        remote_version = data.get("version")
        mandatory = data.get("mandatory", False)
        notes_list = data.get("notes", [])
        changelog = "\n".join(f"- {n}" for n in notes_list)

        if not remote_version or remote_version == local_version:
            return

        if mandatory:
            QMessageBox.information(
                parent,
                "Mandatory Update",
                f"A mandatory update ({remote_version}) is available.\n\n"
                f"Changelog:\n{changelog}\n\nUpdating..."
            )
            run_updater(data["url"])
            return

        msg = QMessageBox(parent)
        msg.setWindowTitle("Update Available")
        msg.setText(f"A new version ({remote_version}) is available!")
        msg.setInformativeText("Click 'Show Details' to view the changelog.")
        msg.setDetailedText(changelog)
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        result = msg.exec()

        if result == QMessageBox.StandardButton.Ok:
            run_updater(data["url"])
        else:
            parent.update_declined_this_session = True

    except Exception as e:
        print("Update check failed:", e)

def run_updater(download_url):
    main_dir = os.path.dirname(sys.executable)
    updater_path = os.path.join(main_dir, "MissionUpdater.exe")
    launcher_pid = os.getpid()
    subprocess.Popen([updater_path, download_url, sys.executable, str(launcher_pid)])
    sys.exit(0)


def run_update_check(version, config_file, status_bar):
    try:
        response = requests.get("https://api.natemarcellus.com/updates/missionhelper", params={"current_version": version}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("version")
            update_url = data.get("url")
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
                temp_extract = os.path.join(os.getcwd(), "temp_update")
                if os.path.exists(temp_extract):
                    shutil.rmtree(temp_extract)
                os.makedirs(temp_extract, exist_ok=True)
                with zipfile.ZipFile("update.zip", "r") as z:
                    z.extractall(temp_extract)
                bot_folder = os.path.join(os.getcwd(), "bot")
                if os.path.exists(bot_folder):
                    shutil.rmtree(bot_folder)
                extracted_items = os.listdir(temp_extract)
                if extracted_items:
                    new_folder = os.path.join(temp_extract, extracted_items[0])
                    shutil.move(new_folder, bot_folder)

                shutil.rmtree(temp_extract)
                os.remove("update.zip")

                if os.path.exists(config_file):
                    with open(config_file, "r") as f:
                        old_settings = f.read()
                    with open(config_file, "w") as f:
                        f.write(old_settings)

                send_messages("Update applied successfully.")
                status_bar.showMessage("Update applied successfully.")
    except Exception as e:
        send_messages(f"Update check failed: {e}")
        status_bar.showMessage("Update check failed")


