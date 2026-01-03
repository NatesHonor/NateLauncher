import os
import shutil
import subprocess
import zipfile
import requests
from io import BytesIO
from handlers.console import send_messages
from PyQt6.QtWidgets import QStatusBar
from utils import state
from utils.runbot import run_bot

def run_install(venv_name: str, status_bar: QStatusBar):
    send_messages(f"Starting install process for venv '{venv_name}'")
    status_bar.showMessage("Running install process...")

    url = "https://github.com/NatesHonor/MissionchiefBot-X/archive/refs/tags/latest.zip"
    bot_folder = os.path.join(os.getcwd(), "bot")
    cache_folder = os.path.join(os.getcwd(), "cache", "bot")

    try:
        send_messages("Downloading latest bot release zip...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        send_messages("Download complete. Extracting zip...")

        with zipfile.ZipFile(BytesIO(response.content)) as z:
            root_folder = z.namelist()[0].split("/")[0]
            temp_extract = os.path.join(os.getcwd(), "temp_extract")
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract)
            os.makedirs(temp_extract, exist_ok=True)
            z.extractall(temp_extract)

        source_dir = os.path.join(temp_extract, root_folder)
        if os.path.exists(bot_folder):
            shutil.rmtree(bot_folder)
        if os.path.exists(cache_folder):
            shutil.rmtree(cache_folder)

        send_messages("Copying files to bot folder...")
        shutil.copytree(source_dir, bot_folder)
        send_messages("Copy complete to bot folder.")

        os.makedirs(os.path.dirname(cache_folder), exist_ok=True)
        send_messages("Copying files to cache folder...")
        shutil.copytree(source_dir, cache_folder)
        send_messages("Copy complete to cache folder.")

        shutil.rmtree(temp_extract)
        send_messages("Temporary extraction cleaned up.")

        send_messages("Install process complete")
        status_bar.showMessage("Install process complete")

        requirements_file = os.path.join(bot_folder, "requirements.txt")
        if os.path.exists(requirements_file):
            send_messages("Installing requirements into venv...")
            status_bar.showMessage("Installing requirements...")
            pip_executable = os.path.join(venv_name, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(venv_name, "bin", "pip")
            try:
                process = subprocess.Popen(
                    [pip_executable, "install", "-r", requirements_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                state.add_process("pip_install", process)
                for line in process.stdout:
                    send_messages(line.strip())
                process.wait()
                if process.returncode == 0:
                    send_messages("Requirements installed successfully.")
                    status_bar.showMessage("Requirements installed successfully.")
                else:
                    send_messages(f"Requirements installation failed with code {process.returncode}")
                    status_bar.showMessage("Requirements installation failed.")
                    return
            except Exception as e:
                send_messages(f"Failed to install requirements: {e}")
                status_bar.showMessage("Failed to install requirements.")
                return
        else:
            send_messages("No requirements.txt found in bot folder.")
            status_bar.showMessage("No requirements.txt found.")

    except Exception as e:
        send_messages(f"Install process failed: {e}")
        status_bar.showMessage("Install process failed")

    run_bot(venv_name, status_bar)
