import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QFont, QGuiApplication
from PyQt5.QtCore import Qt

from src import theme

# A bit bigger than the original 260x230 -- gives the thumbnail and
# buttons more breathing room without it taking over the screen.
WINDOW_SIZE = (320, 340)
THUMB_SIZE = (292, 160)
SCREEN_MARGIN = 20  # gap kept from the screen edge / taskbar


class MiniDashboard(QWidget):
    def __init__(self, engine, on_open_full, on_quit):
        super().__init__()
        self.engine = engine

        self.setWindowTitle("Gaze Tracker")
        self.setFixedSize(*WINDOW_SIZE)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.SURFACE};
                color: {theme.TEXT};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(*([theme.SPACE_SM] * 4))
        layout.setSpacing(theme.SPACE_SM)

        self.thumb = QLabel()
        self.thumb.setAlignment(Qt.AlignCenter)
        self.thumb.setFixedSize(*THUMB_SIZE)
        self.thumb.setStyleSheet(f"background: {theme.BG}; border-radius: {theme.RADIUS_MD}px;")
        layout.addWidget(self.thumb)

        self.status = QLabel()
        self.status.setFont(theme.font(12, QFont.DemiBold, tracking=2))
        layout.addWidget(self.status)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(theme.SPACE_XS)
        self.pause_btn = QPushButton()
        self.pause_btn.setStyleSheet(theme.button_qss())
        self.pause_btn.clicked.connect(self.toggle_pause)
        btn_row.addWidget(self.pause_btn)

        open_btn = QPushButton("Full Dashboard")
        open_btn.setStyleSheet(theme.button_qss())
        open_btn.clicked.connect(on_open_full)
        btn_row.addWidget(open_btn)
        layout.addLayout(btn_row)

        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet(theme.button_qss())
        quit_btn.clicked.connect(on_quit)
        layout.addWidget(quit_btn)

        self.shortcut_hint = QLabel("* Fn+Esc - To exit the app !")
        self.shortcut_hint.setAlignment(Qt.AlignCenter)
        self.shortcut_hint.setFont(theme.font(9, QFont.Normal))
        self.shortcut_hint.setStyleSheet(f"color: {theme.TEXT_MUTED};")
        layout.addWidget(self.shortcut_hint)

        self.setLayout(layout)

        # the app now launches paused (see main.py) -- reflect that here
        # instead of assuming "Pause"/"TRACKING" is the true starting state
        self._sync_paused_ui(getattr(self.engine, "paused", False))

        self.engine.frame_ready.connect(self.update_thumb)
        self.engine.data_ready.connect(self.update_status)

    def showEvent(self, event):
        self._position_bottom_right()
        super().showEvent(event)

    def _position_bottom_right(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = screen.x() + screen.width() - self.width() - SCREEN_MARGIN
        y = screen.y() + screen.height() - self.height() - SCREEN_MARGIN
        self.move(x, y)

    def _sync_paused_ui(self, paused):
        self.pause_btn.setText("Resume" if paused else "Pause")
        if paused:
            self.status.setText("● PAUSED")
            self.status.setStyleSheet(f"color: {theme.WARN};")
        else:
            self.status.setText("● TRACKING")
            self.status.setStyleSheet(f"color: {theme.GOOD};")

    def toggle_pause(self):
        if self.engine.paused:
            self.engine.resume()
        else:
            self.engine.pause()
        self._sync_paused_ui(self.engine.paused)

    def update_thumb(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.thumb.setPixmap(
            pixmap.scaled(self.thumb.width(), self.thumb.height(),
                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def update_status(self, data):
        if not data["face_detected"]:
            self.status.setText("● NO FACE")
            self.status.setStyleSheet(f"color: {theme.WARN};")
            return
        self.status.setText(f"● TRACKING · Zone {data['zone']}")
        self.status.setStyleSheet(f"color: {theme.GOOD};")