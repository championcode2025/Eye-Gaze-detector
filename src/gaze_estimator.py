import cv2
import numpy as np


class GazeEstimator:
    """
    Takes raw gaze_ratio [0,1] from EyeExtractor.
    Applies Kalman filtering only (no polynomial calibration).

    INPUT: gaze_ratio_x, gaze_ratio_y ∈ [0, 1]
    OUTPUT: {"gaze_x": float, "gaze_y": float, "confidence": float}
    """

    def __init__(self):
        self.kf_x = self._make_kalman()
        self.kf_y = self._make_kalman()

    def _make_kalman(self):
        kf = cv2.KalmanFilter(2, 1)
        kf.transitionMatrix = np.array([[1, 1],
                                         [0, 1]], np.float32)
        kf.measurementMatrix = np.array([[1, 0]], np.float32)
        kf.processNoiseCov = np.eye(2, dtype=np.float32) * 1e-4
        kf.measurementNoiseCov = np.array([[1e-2]], np.float32)
        kf.statePost = np.array([[0.5], [0]], np.float32)
        return kf

    def estimate(self, gaze_ratio_x, gaze_ratio_y, frame_width, frame_height):
        # Kalman filter for x axis
        self.kf_x.predict()
        corrected_x = self.kf_x.correct(
            np.array([[np.float32(gaze_ratio_x)]])
        )
        gaze_x = float(corrected_x[0])

        # Kalman filter for y axis
        self.kf_y.predict()
        corrected_y = self.kf_y.correct(
            np.array([[np.float32(gaze_ratio_y)]])
        )
        gaze_y = float(corrected_y[0])

        gaze_x = max(0.0, min(1.0, gaze_x))
        gaze_y = max(0.0, min(1.0, gaze_y))

        return {
            "gaze_x": round(gaze_x, 4),
            "gaze_y": round(gaze_y, 4),
            "confidence": 0.95
        }