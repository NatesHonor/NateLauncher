from PyQt6.QtWidgets import QFrame

class GlassFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #181818; border-radius: 16px;")
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if self.parent():
            self.parent().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.parent():
            self.parent().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.parent():
            self.parent().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)
