import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QFrame,
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt


class ZoneBox(QFrame):
    def __init__(self, text):
        super().__init__()
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            color: white; font-size:11px; letter-spacing:0.5px; font-weight: 700;
        """)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setMinimumSize(150, 150)
        self.setStyleSheet("""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #111D33, stop:1 #182845);
            border:1px solid #31547E; border-radius:30px;
        """)

    def activate(self):
        self.setStyleSheet("""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #22D3EE, stop:0.5 #14B8A6, stop:1 #0EA5E9);
            border:3px solid #E0FBFC; border-radius:30px;
        """)
        self.label.setStyleSheet("color:#07111F; font-size:13px; font-weight:650; letter-spacing:1px;")

    def deactivate(self):
        self.setStyleSheet("""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #111D33, stop:1 #182845);
            border:1px solid #31547E; border-radius:30px;
        """)
        self.label.setStyleSheet("color:white; font-size:13px; font-weight:650; letter-spacing:1px;")


class GazeTrackerUI(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        self.setWindowTitle("Gaze Controlled Interface")
        self.resize(1700, 950)
        self.setMinimumSize(1500, 850)

        self.setStyleSheet("""
            QWidget{ background-color:#070B14; color:#F8FAFC; font-family: Segoe UI; }
            QLabel{ color:#E6EDF7; }
            QFrame{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0E1628, stop:1 #121D33);
                border-radius:26px; border:1px solid rgba(255,255,255,0.06);
            }
        """)

        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(34)
        self.main_layout.setContentsMargins(34, 30, 34, 30)

        # LEFT PANEL
        self.left_card = QFrame()
        self.left_card.setStyleSheet("""
            QFrame{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0D172B, stop:1 #16233D);
            border-radius:34px; border:1px solid #28476F; padding:18px; }
        """)
        self.left_card_layout = QVBoxLayout()
        self.left_card_layout.setSpacing(24)
        self.left_card_layout.setContentsMargins(26, 24, 26, 24)
        self.left_card.setLayout(self.left_card_layout)

        self.title = QLabel("AI Gaze Estimation Dashboard")
        self.subtitle = QLabel("Real-time eye movement visualization dashboard")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color:#7DD3FC; font-size:15px; font-weight:500; padding-bottom:18px; letter-spacing:1px;")
        self.title.setFont(QFont("Bahnschrift SemiBold", 35, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color:#F8FAFC; padding-top:12px; padding-bottom:12px; letter-spacing:1px;")

        self.webcam_label = QLabel()
        self.webcam_label.setFixedSize(1030, 700)
        self.webcam_label.setStyleSheet("""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #030712, stop:1 #08172C);
            border:1px solid #355E8C; border-radius:42px; padding:24px; margin-top:10px; margin-bottom:14px;
        """)

        self.status_label = QLabel("● TRACKING ACTIVE | Zone : None")
        self.status_label.setFont(QFont("Bahnschrift SemiBold", 17, QFont.Medium))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #081225, stop:1 #0E203A);
            border:1px solid #1E3A5F; padding:20px; border-radius:24px; font-size:19px; font-weight:600; color:#7DD3FC;
        """)

        self.live_chip = QLabel("● LIVE")
        self.live_chip.setAlignment(Qt.AlignCenter)
        self.live_chip.setStyleSheet("""
            background:#0E2A20; color:#6EE7B7; border:1px solid #34D399;
            padding:10px; border-radius:18px; font-size:15px; font-weight:700;
        """)
        self.face_chip = QLabel("FACE DETECTED")
        self.face_chip.setAlignment(Qt.AlignCenter)
        self.face_chip.setStyleSheet("""
            background:#0D203A; color:#7DD3FC; border:1px solid #38BDF8;
            padding:10px; border-radius:18px; font-size:15px; font-weight:700;
        """)

        self.left_card_layout.addWidget(self.title)
        self.left_card_layout.addWidget(self.subtitle)
        self.left_card_layout.addWidget(self.webcam_label)
        self.left_card_layout.addWidget(self.status_label)
        chip_row = QHBoxLayout()
        chip_row.setSpacing(16)
        chip_row.addWidget(self.live_chip)
        chip_row.addWidget(self.face_chip)
        self.left_card_layout.addLayout(chip_row)

        # RIGHT PANEL
        self.right_card = QFrame()
        self.right_card.setStyleSheet("""
            QFrame{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0D172B, stop:1 #16233D);
            border-radius:34px; border:1px solid #28476F; padding:18px; }
        """)
        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(22)
        self.right_panel.setContentsMargins(24, 24, 24, 24)
        self.right_card.setLayout(self.right_panel)

        self.grid_title = QLabel("Interactive Gaze Grid")
        self.grid_title.setFont(QFont("Bahnschrift SemiBold", 30, QFont.Bold))
        self.grid_title.setAlignment(Qt.AlignCenter)
        self.grid_title.setStyleSheet("color:#93C5FD; padding-top:12px; padding-bottom:14px; letter-spacing:1px;")

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(22)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.zone_boxes = []
        zone_names = ["TOP LEFT", "TOP CENTER", "TOP RIGHT", "MID LEFT", "CENTER",
                      "MID RIGHT", "BOT LEFT", "BOT CENTER", "BOT RIGHT"]
        index = 0
        for row in range(3):
            for col in range(3):
                box = ZoneBox(zone_names[index])
                self.grid_layout.addWidget(box, row, col)
                self.zone_boxes.append(box)
                index += 1

        self.analytics_card = QFrame()
        self.analytics_card.setStyleSheet("""
            QFrame{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0C162B, stop:1 #182946);
            border-radius:30px; border:1px solid #315A8A; padding:18px; }
        """)
        analytics_layout = QVBoxLayout()
        analytics_layout.setSpacing(18)
        analytics_layout.setContentsMargins(24, 24, 24, 24)
        self.analytics_card.setLayout(analytics_layout)

        self.analytics_title = QLabel("Tracking Analytics")
        self.analytics_title.setStyleSheet("font-size:24px; font-weight:700; color:#7DD3FC; padding-bottom:8px;")
        self.analytics_title.setFont(QFont("Bahnschrift SemiBold", 18, QFont.Bold))
        self.analytics_status = QLabel("STATUS : TRACKING")
        self.analytics_zone = QLabel("ZONE : NONE")
        self.analytics_conf = QLabel("CONFIDENCE : LIVE")
        self.analytics_gaze = QLabel("GAZE : 0.00 , 0.00")
        self.analytics_click = QLabel("CLICK : READY")

        for label in [self.analytics_title, self.analytics_status, self.analytics_zone,
                      self.analytics_conf, self.analytics_gaze, self.analytics_click]:
            label.setStyleSheet("color:#E6EDF7; padding:8px; font-size:13px; font-weight:600;")
            analytics_layout.addWidget(label)

        self.right_panel.addWidget(self.analytics_card)
        self.right_panel.addWidget(self.grid_title)
        self.right_panel.addLayout(self.grid_layout)

        self.main_layout.addWidget(self.left_card, 7)
        self.main_layout.addWidget(self.right_card, 5)
        self.setLayout(self.main_layout)

        # listen to shared engine instead of owning backend/timer
        self.engine.frame_ready.connect(self.display_frame)
        self.engine.data_ready.connect(self.update_ui)

    def update_ui(self, data):
        if not data["face_detected"]:
            self.analytics_status.setText("STATUS : NO FACE")
            return

        self.analytics_click.setText(
            "CLICK : BLINK DETECTED" if data["clicked"] else "CLICK : READY"
        )
        self.analytics_gaze.setText(f"GAZE : {data['gaze_x']:.2f} , {data['gaze_y']:.2f}")
        self.update_zone_ui(data["zone"])
        self.status_label.setText(f"● TRACKING ACTIVE | Zone : {data['zone']}")
        self.analytics_zone.setText(f"ZONE : {data['zone']}")
        self.analytics_status.setText("STATUS : ACTIVE")

    def update_zone_ui(self, active_zone):
        active_index = active_zone - 1
        for i, box in enumerate(self.zone_boxes):
            box.activate() if i == active_index else box.deactivate()

    def display_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.webcam_label.setPixmap(
            pixmap.scaled(self.webcam_label.width(), self.webcam_label.height(), Qt.KeepAspectRatio)
        )

    def closeEvent(self, event):
        # don't kill the engine/camera — just hide the window, tray app stays alive
        event.ignore()
        self.hide()