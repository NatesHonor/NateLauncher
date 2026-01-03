import os
import subprocess
import threading
import time
from handlers.console import send_messages
from PyQt6.QtWidgets import QStatusBar
from utils import state

def run_bot(venv_name: str = None, status_bar: QStatusBar = None):
    bot_folder = os.path.join(os.getcwd(), "bot")
    if not os.path.exists(bot_folder):
        send_messages("Bot folder not found. Cannot start bot.")
        if status_bar:
            status_bar.showMessage("Bot folder not found")
        return
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
    def worker():
        try:
            process = subprocess.Popen(
                [python_executable, main_py],
                cwd=bot_folder,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            state.add_process("bot_runtime", process)
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    send_messages(line.strip())
                time.sleep(0.1)
            process.wait()
            if process.returncode == 0:
                send_messages("Bot runtime finished successfully.")
                if status_bar:
                    status_bar.showMessage("Bot runtime finished successfully")
            else:
                send_messages(f"Bot runtime exited with code {process.returncode}")
                if status_bar:
                    status_bar.showMessage(f"Bot runtime exited with code {process.returncode}")
        except Exception as e:
            send_messages(f"Failed to run bot: {e}")
            if status_bar:
                status_bar.showMessage("Failed to run bot")
    threading.Thread(target=worker, daemon=True).start()
