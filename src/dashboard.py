import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QPushButton,
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt

from src import theme


class ZoneBox(QFrame):
    """One cell of the 3x3 gaze grid. Flat color + fixed radius regardless
    of how big the grid layout stretches the cell -- a radius tuned for a
    150px box looks blobby once it gets stretched to 400px wide, so we
    keep the radius constant and let the box itself grow."""

    def __init__(self, text):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(90, 90)

        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(theme.font(11, QFont.DemiBold, tracking=3))
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self._idle()

    def _idle(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.SURFACE_RAISED};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
            }}
        """)
        self.label.setStyleSheet(f"color: {theme.TEXT_MUTED}; background: transparent;")

    def _active(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.ACCENT};
                border: 1px solid {theme.ACCENT};
                border-radius: {theme.RADIUS_MD}px;
            }}
        """)
        self.label.setStyleSheet(f"color: {theme.BG}; background: transparent;")

    def activate(self):
        self._active()

    def deactivate(self):
        self._idle()


class StatusChip(QLabel):
    """A small pill that can flip between GOOD / WARN without anyone
    needing to rebuild its stylesheet by hand each time."""

    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(theme.font(11, QFont.DemiBold, tracking=2))
        self.set_state(good=True)

    def set_state(self, good: bool, text=None):
        if text is not None:
            self.setText(text)
        fg, bg = (theme.GOOD, theme.GOOD_DIM) if good else (theme.WARN, theme.WARN_DIM)
        self.setStyleSheet(theme.chip_qss(fg, bg))


class GazeTrackerUI(QWidget):
    def __init__(self, engine, on_minimize_to_tray=None):
        super().__init__()
        self.engine = engine
        self.on_minimize_to_tray = on_minimize_to_tray

        self.setWindowTitle("Gaze Controlled Interface")
        self.resize(1500, 880)
        self.setMinimumSize(1100, 700)

        self.setStyleSheet(f"""
            QWidget {{ background-color: {theme.BG}; color: {theme.TEXT}; }}
            QLabel {{ color: {theme.TEXT}; }}
        """)

        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(theme.SPACE_LG)
        self.main_layout.setContentsMargins(*([theme.SPACE_LG] * 4))

        # ---------------- LEFT: camera + primary status ----------------
        self.left_card = QFrame()
        self.left_card.setStyleSheet(theme.card_qss())
        self.left_card_layout = QVBoxLayout()
        self.left_card_layout.setSpacing(theme.SPACE_MD)
        self.left_card_layout.setContentsMargins(*([theme.SPACE_MD] * 4))
        self.left_card.setLayout(self.left_card_layout)

        self.title = QLabel("Gaze Estimation Dashboard")
        self.title.setFont(theme.font(24, QFont.Bold, tracking=2))
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("Real-time eye movement tracking")
        self.subtitle.setFont(theme.font(12, QFont.Normal))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet(f"color: {theme.TEXT_MUTED};")

        self.webcam_label = QLabel()
        self.webcam_label.setAlignment(Qt.AlignCenter)
        self.webcam_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webcam_label.setMinimumSize(480, 320)
        self.webcam_label.setStyleSheet(f"""
            background: {theme.BG};
            border: 1px solid {theme.BORDER};
            border-radius: {theme.RADIUS_LG}px;
        """)

        self.status_label = QLabel("● TRACKING ACTIVE")
        self.status_label.setFont(theme.font(14, QFont.DemiBold, tracking=2))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"""
            background: {theme.SURFACE_RAISED};
            border: 1px solid {theme.BORDER};
            color: {theme.GOOD};
            padding: 14px;
            border-radius: {theme.RADIUS_MD}px;
        """)

        self.live_chip = StatusChip("● LIVE")
        self.live_chip.set_state(good=True)

        self.face_chip = StatusChip("FACE DETECTED")
        self.face_chip.set_state(good=True)

        self.left_card_layout.addWidget(self.title)
        self.left_card_layout.addWidget(self.subtitle)
        self.left_card_layout.addWidget(self.webcam_label, 1)
        self.left_card_layout.addWidget(self.status_label)
        chip_row = QHBoxLayout()
        chip_row.setSpacing(theme.SPACE_SM)
        chip_row.addWidget(self.live_chip)
        chip_row.addWidget(self.face_chip)
        self.left_card_layout.addLayout(chip_row)

        self.tray_btn = QPushButton("Back to Tray")
        self.tray_btn.setStyleSheet(theme.button_qss())
        self.tray_btn.clicked.connect(self._handle_minimize)
        self.left_card_layout.addWidget(self.tray_btn)

        # ---------------- RIGHT: analytics + zone grid ----------------
        self.right_card = QFrame()
        self.right_card.setStyleSheet(theme.card_qss())
        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(theme.SPACE_MD)
        self.right_panel.setContentsMargins(*([theme.SPACE_MD] * 4))
        self.right_card.setLayout(self.right_panel)

        self.analytics_card = QFrame()
        self.analytics_card.setStyleSheet(f"""
            QFrame {{
                background: {theme.SURFACE_RAISED};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
            }}
        """)
        analytics_layout = QVBoxLayout()
        analytics_layout.setSpacing(theme.SPACE_XS)
        analytics_layout.setContentsMargins(*([theme.SPACE_MD] * 4))
        self.analytics_card.setLayout(analytics_layout)

        self.analytics_title = QLabel("Tracking Analytics")
        self.analytics_title.setFont(theme.font(16, QFont.Bold, tracking=1))
        self.analytics_title.setStyleSheet(f"color: {theme.TEXT}; padding-bottom: 6px;")

        self.analytics_status = QLabel("STATUS  ·  TRACKING")
        self.analytics_zone = QLabel("ZONE    ·  —")
        self.analytics_gaze = QLabel("GAZE    ·  0.00, 0.00")
        self.analytics_click = QLabel("CLICK   ·  READY")

        analytics_layout.addWidget(self.analytics_title)
        for label in [self.analytics_status, self.analytics_zone,
                      self.analytics_gaze, self.analytics_click]:
            label.setFont(theme.font(12, QFont.Normal))
            label.setStyleSheet(f"color: {theme.TEXT_MUTED}; padding: 4px 0;")
            analytics_layout.addWidget(label)

        self.grid_title = QLabel("Gaze Zone")
        self.grid_title.setFont(theme.font(16, QFont.Bold, tracking=1))
        self.grid_title.setAlignment(Qt.AlignLeft)
        self.grid_title.setStyleSheet(f"color: {theme.TEXT}; padding-top: {theme.SPACE_XS}px;")

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(theme.SPACE_SM)
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

        self.right_panel.addWidget(self.analytics_card)
        self.right_panel.addWidget(self.grid_title)
        self.right_panel.addLayout(self.grid_layout, 1)

        self.main_layout.addWidget(self.left_card, 7)
        self.main_layout.addWidget(self.right_card, 5)
        self.setLayout(self.main_layout)

        self.engine.frame_ready.connect(self.display_frame)
        self.engine.data_ready.connect(self.update_ui)

    def _handle_minimize(self):
        if self.on_minimize_to_tray:
            self.on_minimize_to_tray()
        else:
            self.hide()

    def update_ui(self, data):
        if not data["face_detected"]:
            self.status_label.setText("● NO FACE DETECTED")
            self.status_label.setStyleSheet(f"""
                background: {theme.SURFACE_RAISED};
                border: 1px solid {theme.BORDER};
                color: {theme.WARN};
                padding: 14px;
                border-radius: {theme.RADIUS_MD}px;
            """)
            self.face_chip.set_state(good=False, text="NO FACE")
            self.analytics_status.setText("STATUS  ·  NO FACE")
            self.update_zone_ui(0)
            return

        self.face_chip.set_state(good=True, text="FACE DETECTED")
        self.status_label.setText("● TRACKING ACTIVE")
        self.status_label.setStyleSheet(f"""
            background: {theme.SURFACE_RAISED};
            border: 1px solid {theme.BORDER};
            color: {theme.GOOD};
            padding: 14px;
            border-radius: {theme.RADIUS_MD}px;
        """)

        self.analytics_click.setText(
            "CLICK   ·  BLINK DETECTED" if data["clicked"] else "CLICK   ·  READY"
        )
        self.analytics_gaze.setText(f"GAZE    ·  {data['gaze_x']:.2f}, {data['gaze_y']:.2f}")
        self.analytics_zone.setText(f"ZONE    ·  {data['zone']}")
        self.analytics_status.setText("STATUS  ·  ACTIVE")
        self.update_zone_ui(data["zone"])

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
            pixmap.scaled(self.webcam_label.width(), self.webcam_label.height(),
                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def closeEvent(self, event):
        event.ignore()
        self.hide()