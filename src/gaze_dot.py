from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor


class GazeDot(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        

        self.resize(40, 40)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setPen(Qt.NoPen)

        # Outer glow
        painter.setBrush(
            QColor(34, 211, 238, 60)
        )

        painter.drawEllipse(
            0,
            0,
            35,
            35
        )

        # Middle glow
        painter.setBrush(
            QColor(34, 211, 238, 140)
        )

        painter.drawEllipse(
            6,
            6,
            26,
            26
        )

        # Core
        painter.setBrush(
            QColor(255, 255, 255)
        )

        painter.drawEllipse(
            14,
            14,
            10,
            10
        )