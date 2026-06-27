import cv2
import numpy as np
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from src.camera import Camera
from src.facemesh import FaceMesh
from src.eyeextractor import EyeExtractor
from src.visualiser import Visualiser
from src.gaze_estimator import GazeEstimator
from src.gaze_backend import GazeBackend
from src.click_backend import ClickBackend
from src.scroll_backend import ScrollBackend


class GazeEngine(QObject):
    """
    Owns the camera + full backend pipeline and runs the per-frame
    processing loop. Emits signals so any number of UI widgets
    (full dashboard, mini tray view) can display the same live data
    without each owning their own camera/timer.

    If the camera fails to open, the engine still runs and emits a
    placeholder frame instead of crashing — useful for UI testing
    on a machine without a working webcam.
    """

    frame_ready = pyqtSignal(object)   # raw BGR np.ndarray frame (post-visualiser draw)
    data_ready = pyqtSignal(dict)      # {zone, gaze_x, gaze_y, clicked, face_detected}

    def __init__(self, interval_ms=30):
        super().__init__()

        self.camera_available = True
        try:
            self.cam = Camera(device_index=0)
        except Exception as e:
            print(f"⚠ Camera unavailable, running in UI-preview mode: {e}")
            self.cam = None
            self.camera_available = False

        self.face_mesh = FaceMesh()
        self.extractor = EyeExtractor()
        self.visualiser = Visualiser()
        self.gaze_estimator = GazeEstimator()
        self.gaze_backend = GazeBackend()
        self.click_backend = ClickBackend()
        self.scroll_backend = ScrollBackend()

        self.paused = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(interval_ms)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def process_frame(self):
        if self.paused:
            return

        if not self.camera_available:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                blank, "NO CAMERA DETECTED", (90, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 255), 2
            )
            self.frame_ready.emit(blank)
            self.data_ready.emit({
                "zone": None,
                "gaze_x": None,
                "gaze_y": None,
                "clicked": False,
                "face_detected": False,
            })
            return

        frame = self.cam.read()
        if frame is None:
            return

        landmarks = self.face_mesh.process(frame)

        if not landmarks:
            self.frame_ready.emit(frame)
            self.data_ready.emit({
                "zone": None,
                "gaze_x": None,
                "gaze_y": None,
                "clicked": False,
                "face_detected": False,
            })
            return

        gaze_data = self.extractor.extract(landmarks, frame.shape)
        frame = self.visualiser.draw(frame, landmarks, gaze_data)

        self.click_backend.process_blink_click(landmarks)

        h, w = frame.shape[:2]
        raw_x = gaze_data["gaze_point"][0] / w
        raw_y = gaze_data["gaze_point"][1] / h

        estimate = self.gaze_estimator.estimate(raw_x, raw_y, w, h)

        self.gaze_backend.update_mouse_position(
            estimate["gaze_x"], estimate["gaze_y"]
        )

        self.gaze_backend.last_gaze_x = raw_x
        self.gaze_backend.last_gaze_y = raw_y

        zone = self.gaze_backend.calculate_current_zone()
        self.scroll_backend.handle_gaze_scrolling(raw_x, raw_y)

        self.frame_ready.emit(frame)
        self.data_ready.emit({
            "zone": zone,
            "gaze_x": estimate["gaze_x"],
            "gaze_y": estimate["gaze_y"],
            "clicked": self.click_backend.has_clicked,
            "face_detected": True,
        })

    def shutdown(self):
        self.timer.stop()
        if self.cam is not None:
            self.cam.release()
        self.face_mesh.close()