import os
import shutil
import requests
import zipfile

from PyQt6.QtCore import QThread, pyqtSignal, QProcess

from console_handler import send_messages

class Worker(QThread):
    output = pyqtSignal(str)
    started = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.process = None
        self.venv_created = False
        self.requirements_installed = False
        self.bot_downloaded = False

    def run(self):
        if not os.path.exists("launcher_settings.ini"):
            with open("launcher_settings.ini", "w") as f:
                f.write("")
            self.output.emit("launcher_settings.ini created, requesting venv preference")
        else:
            self.start_bot_after_wait()

    def _read_venv_name(self, file):
        for line in file:
            if line.startswith("venv="):
                return line.strip().split("=")[1]
        return ""

    def install_bot(self):
        try:
            bot_folder = os.path.join(os.getcwd(), "bot")
            os.makedirs(bot_folder, exist_ok=True)
            zip_url = "https://github.com/NatesHonor/MissionchiefBot-X/archive/refs/tags/latest.zip"
            zip_path = os.path.join(bot_folder, "latest.zip")
            response = requests.get(zip_url, stream=True)
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(bot_folder)
            extracted_folder_name = None
            for name in os.listdir(bot_folder):
                full_path = os.path.join(bot_folder, name)
                if os.path.isdir(full_path) and name.startswith("MissionchiefBot-X"):
                    extracted_folder_name = full_path
                    break
            if extracted_folder_name:
                for item in os.listdir(extracted_folder_name):
                    s = os.path.join(extracted_folder_name, item)
                    d = os.path.join(bot_folder, item)
                    if os.path.exists(d):
                        if os.path.isdir(d):
                            shutil.rmtree(d)
                        else:
                            os.remove(d)
                    shutil.move(s, d)
                shutil.rmtree(extracted_folder_name)
            os.remove(zip_path)
            cache_folder = os.path.join(os.getcwd(), "cache")
            os.makedirs(cache_folder, exist_ok=True)
            cache_bot_folder = os.path.join(cache_folder, "bot")
            if os.path.exists(cache_bot_folder):
                shutil.rmtree(cache_bot_folder)
            shutil.copytree(bot_folder, cache_bot_folder)
            self.output.emit("Bot setup completed successfully and cached!")
        except Exception as e:
            self.output.emit(f"Error during bot setup: {e}")

    def install_requirements(self, venv_name):
        req_file = os.path.join(os.getcwd(), "bot", "requirements.txt")
        requirements_command = f"{os.path.join(venv_name, 'Scripts', 'pip')} install -r \"{req_file}\"" if venv_name else f"pip install -r \"{req_file}\""
        self.start_process(requirements_command)

    def start_process(self, command):
        self.process = QProcess()
        self.process.setProgram(command.split()[0])
        self.process.setArguments(command.split()[1:])
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.command_finished)
        self.process.start()

    def handle_stdout(self):
        output = bytes(self.process.readAllStandardOutput()).decode(errors="ignore")
        if output:
            self.output.emit(output)

    def handle_stderr(self):
        error = bytes(self.process.readAllStandardError()).decode(errors="ignore")
        if error:
            self.output.emit(error)

    def command_finished(self, exit_code):
        if exit_code == 0 and not self.requirements_installed:
            self.requirements_installed = True
            self.start_bot_after_wait()

    def start_bot_after_wait(self):
        with open("launcher_settings.ini", "r") as f:
            venv_name = self._read_venv_name(f)
        bot_main = os.path.join(os.getcwd(), "bot", "main.py")
        python_exe = os.path.join(venv_name, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_name, 'bin', 'python')
        command = python_exe if venv_name else "python"
        args = ["-u", bot_main]

        self.process = QProcess()
        self.process.setProgram(command)
        self.process.setArguments(args)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.start()

        pid = self.process.processId()
        self.output.emit(f"Bot started with process ID {pid}")
        self.started.emit(self.process)
        return self.process

class MainWindow:
    def __init__(self):
        self.worker = Worker()
        self.worker.output.connect(send_messages)

    def start_bot(self):
        if self.worker.isRunning():
            send_messages("Bot launch already in progress.")
            return self.worker.process
        self.worker.start()
        return self.worker.process
