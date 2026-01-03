import sys, os, shutil, requests, psutil, subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, url, target_exe):
        super().__init__()
        self.url = url
        self.target_exe = target_exe

    def run(self):
        resp = requests.get(self.url, stream=True)
        total = int(resp.headers.get("content-length", 0))
        tmp_file = self.target_exe + ".new"
        downloaded = 0
        with open(tmp_file, "wb") as f:
            for chunk in resp.iter_content(8192):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    percent = int(downloaded * 100 / total)
                    self.progress.emit(percent)
        shutil.move(tmp_file, self.target_exe)
        self.finished.emit()

class UpdaterWindow(QWidget):
    def __init__(self, download_url, target_exe, target_pid):
        super().__init__()
        self.download_url = download_url
        self.target_exe = target_exe
        self.target_pid = target_pid
        self.setWindowTitle("Mission Helper Updater")
        self.setFixedSize(500, 160)
        layout = QVBoxLayout(self)
        self.status = QLabel("Preparing update...", self)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("font-size: 12pt; color: #EAEAEA;")
        layout.addWidget(self.status)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setFixedHeight(30)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 10px;
                text-align: center;
                font-size: 10pt;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress)
        QTimer.singleShot(100, self.run_update)

    def run_update(self):
        if self.is_pid_running(self.target_pid):
            self.status.setText("Waiting for Mission Helper to close...")
            QTimer.singleShot(15000, self.force_close)
        else:
            self.status.setText("Downloading update...")
            self.start_download()

    def is_pid_running(self, pid):
        try:
            proc = psutil.Process(pid)
            return proc.is_running()
        except Exception:
            return False

    def force_close(self):
        try:
            proc = psutil.Process(self.target_pid)
            if proc.is_running():
                proc.kill()
        except Exception:
            pass
        self.status.setText("Downloading update...")
        self.start_download()

    def start_download(self):
        self.thread = DownloadThread(self.download_url, self.target_exe)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.restart_app)
        self.thread.start()

    def restart_app(self):
        self.status.setText("Restarting Mission Helper...")
        subprocess.Popen([self.target_exe])
        QApplication.quit()

def main():
    if len(sys.argv) < 4:
        sys.exit(1)
    app = QApplication(sys.argv)
    win = UpdaterWindow(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
