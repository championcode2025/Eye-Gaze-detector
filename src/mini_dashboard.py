import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt


class MiniDashboard(QWidget):
    def __init__(self, engine, on_open_full, on_quit):
        super().__init__()
        self.engine = engine

        self.setWindowTitle("Gaze Tracker")
        self.setFixedSize(260, 230)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget { background-color:#0D172B; color:#F8FAFC; font-family: Segoe UI; border-radius:16px; }
            QPushButton {
                background:#16233D; color:#7DD3FC; border:1px solid #28476F;
                border-radius:8px; padding:6px; font-size:12px; font-weight:600;
            }
            QPushButton:hover { background:#1D2F52; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.thumb = QLabel()
        self.thumb.setFixedSize(236, 120)
        self.thumb.setStyleSheet("background:#030712; border-radius:10px;")
        layout.addWidget(self.thumb)

        self.status = QLabel("● TRACKING | Zone: -")
        self.status.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.status.setStyleSheet("color:#7DD3FC;")
        layout.addWidget(self.status)

        btn_row = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_pause)
        btn_row.addWidget(self.pause_btn)

        open_btn = QPushButton("Full Dashboard")
        open_btn.clicked.connect(on_open_full)
        btn_row.addWidget(open_btn)
        layout.addLayout(btn_row)

        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(on_quit)
        layout.addWidget(quit_btn)

        self.setLayout(layout)

        self.engine.frame_ready.connect(self.update_thumb)
        self.engine.data_ready.connect(self.update_status)

    def toggle_pause(self):
        if self.engine.paused:
            self.engine.resume()
            self.pause_btn.setText("Pause")
        else:
            self.engine.pause()
            self.pause_btn.setText("Resume")

    def update_thumb(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.thumb.setPixmap(pixmap.scaled(self.thumb.width(), self.thumb.height(), Qt.KeepAspectRatio))

    def update_status(self, data):
        if not data["face_detected"]:
            self.status.setText("● NO FACE DETECTED")
            return
        self.status.setText(f"● TRACKING | Zone: {data['zone']}")