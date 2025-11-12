from PyQt6.QtWidgets import QFrame

class GlassFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #181818; border-radius: 16px;")
        self.setMouseTracking(True)

    def mousePressEvent(self, event): event.accept()
    def mouseReleaseEvent(self, event): event.accept()
    def mouseMoveEvent(self, event): event.accept()
