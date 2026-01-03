import configparser
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

from utils.regions import list_regions, select_region


def ensure_region_selected(parent):
    config = configparser.ConfigParser()
    config.read("launcher_settings.ini")

    region = config.get("Launcher", "region", fallback="").strip()
    if region:
        return

    dialog = QDialog(parent)
    dialog.setWindowTitle("Select Region")
    dialog.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
    dialog.setModal(True)

    layout = QVBoxLayout(dialog)
    label = QLabel("You must select a region to continue.")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)

    for region in list_regions():
        btn = QPushButton(region)
        btn.clicked.connect(lambda _, r=region: _select(dialog, r))
        layout.addWidget(btn)

    dialog.exec()


def _select(dialog, region):
    select_region(region)
    dialog.accept()