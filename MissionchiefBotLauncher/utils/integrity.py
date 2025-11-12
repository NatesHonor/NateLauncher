import os
import shutil
import subprocess
from handlers.console import send_messages
from utils.install import run_install
from utils.runbot import run_bot
from PyQt6.QtWidgets import QStatusBar

def run_integrity_check(venv_name: str, status_bar: QStatusBar):
    send_messages("Integrity check started.")
    status_bar.showMessage("Integrity check started...")

    bot_folder = os.path.join(os.getcwd(), "bot")
    cache_folder = os.path.join(os.getcwd(), "cache", "bot")

    if not os.path.exists(cache_folder):
        send_messages("Cache folder not found. Running install process...")
        status_bar.showMessage("Cache folder not found. Running install...")
        run_install(venv_name, status_bar)
        return

    if not os.path.exists(bot_folder):
        if os.path.exists(cache_folder):
            send_messages("Bot folder missing. Copying cache to bot...")
            status_bar.showMessage("Copying cache to bot...")
            shutil.copytree(cache_folder, bot_folder)
            send_messages("Bot folder created from cache.")
            status_bar.showMessage("Bot folder created from cache.")
        else:
            send_messages("Bot and cache folders missing. Running install process...")
            status_bar.showMessage("Bot and cache folders missing. Running install...")
            run_install(venv_name, status_bar)
            return

    cache_files = []
    for root, _, files in os.walk(cache_folder):
        for file in files:
            rel_path = os.path.relpath(root, cache_folder)
            cache_files.append((os.path.join(root, file), os.path.join(bot_folder, rel_path, file)))

    total_files = len(cache_files)
    verified_count = 0
    missing_files = []

    for i, (cache_file, target_file) in enumerate(cache_files, start=1):
        if os.path.exists(target_file):
            verified_count += 1
        else:
            missing_files.append((cache_file, target_file))
        percent = int((i / total_files) * 100)
        if percent % 10 == 0:
            send_messages(f"{percent}% integrity verified...")
            status_bar.showMessage(f"{percent}% integrity verified...")

    if missing_files:
        send_messages(f"{len(missing_files)} file(s) missing or corrupted. Restoring...")
        status_bar.showMessage(f"{len(missing_files)} file(s) missing or corrupted. Restoring...")
        for cache_file, target_file in missing_files:
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            shutil.copy2(cache_file, target_file)
            send_messages(f"Restored {os.path.basename(target_file)}")
    else:
        send_messages("Integrity verified. No missing files.")
        status_bar.showMessage("Integrity verified. No missing files.")

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

    run_bot(venv_name, status_bar)
