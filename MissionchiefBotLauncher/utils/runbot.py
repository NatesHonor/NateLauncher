import os
import subprocess
from handlers.console import send_messages
from PyQt6.QtWidgets import QStatusBar
from utils import state

def run_bot(venv_name: str = None, status_bar: QStatusBar = None):
    send_messages("Starting bot runtime...")
    if status_bar:
        status_bar.showMessage("Starting bot runtime...")

    bot_folder = os.path.join(os.getcwd(), "bot")
    if not os.path.exists(bot_folder):
        send_messages("Bot folder not found. Cannot start bot.")
        if status_bar:
            status_bar.showMessage("Bot folder not found")
        return

    send_messages(f"Bot folder located at {bot_folder}")
    if status_bar:
        status_bar.showMessage("Bot folder verified")

    main_py = os.path.join(bot_folder, "main.py")
    if not os.path.exists(main_py):
        send_messages("main.py not found in bot folder.")
        if status_bar:
            status_bar.showMessage("main.py not found")
        return

    if os.name == "nt":
        python_executable = os.path.join(venv_name, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(venv_name, "bin", "python")

    if not os.path.exists(python_executable):
        send_messages("Python executable not found in venv.")
        if status_bar:
            status_bar.showMessage("Python executable not found")
        return

    send_messages("Launching bot process...")
    if status_bar:
        status_bar.showMessage("Launching bot process...")

    try:
        process = subprocess.Popen(
            [python_executable, main_py],
            cwd=bot_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        state.current_process = process
        for line in process.stdout:
            send_messages(line.strip())
        process.wait()
        state.current_process = None
        if process.returncode == 0:
            send_messages("Bot runtime finished successfully.")
            if status_bar:
                status_bar.showMessage("Bot runtime finished successfully")
        else:
            send_messages(f"Bot runtime exited with code {process.returncode}")
            if status_bar:
                status_bar.showMessage(f"Bot runtime exited with code {process.returncode}")
    except Exception as e:
        state.current_process = None
        send_messages(f"Failed to run bot: {e}")
        if status_bar:
            status_bar.showMessage("Failed to run bot")
