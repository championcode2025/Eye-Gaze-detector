# Gaze CV Kalman

Real-time gaze-controlled interface and PyQt5 dashboard that estimates eye gaze from a webcam and maps it to OS cursor actions (move, blink-click, scroll). Uses MediaPipe FaceMesh for landmark detection, OpenCV for video I/O, and PyAutoGUI for OS interactions.

## Quickstart

1. Create and activate a virtual environment (Windows):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app:

```powershell
python main.py
```

## Project structure

- `main.py` — PyQt5 UI and application entry
- `src/camera.py` — webcam wrapper
- `src/facemesh.py` — MediaPipe FaceMesh wrapper
- `src/eyeextractor.py` — iris center extraction and gaze ratios
- `src/gaze_estimator.py` — smoothing, Kalman filters, calibration save/load
- `src/gaze_backend.py` — mapping gaze ratios to OS cursor, zone logic
- `src/click_backend.py` — blink detection mapped to click
- `src/scroll_backend.py` — gaze-based scrolling
- `src/visualiser.py` — OpenCV overlay drawing utilities
- `src/data_collector.py` — offline dataset collection helper

## How it works (high-level)

1. Capture webcam frames with `Camera`.
2. Detect facial landmarks with `FaceMesh`.
3. Compute iris centers and normalized gaze ratios in `EyeExtractor`.
4. (Optional) Calibrate using `GazeEstimator` 9-point flow to produce a mapping from raw gaze ratios → screen pixels.
5. Smooth and map gaze to OS cursor in `GazeBackend`; blink clicks and scrolling handled by `ClickBackend` and `ScrollBackend`.
6. Visual overlays are drawn via `Visualiser` and shown in the PyQt UI.

## Calibration & Usage

- Calibration flow: press the `Calibrate` control in the UI (if present) to start a 9-point calibration. For each dot, hold gaze on the dot for ~1.5–2s so `GazeEstimator.record_calibration_sample` can capture a sample.
- If you lack an on-screen calibration UI, use `src/data_collector.py` to build a dataset and call `GazeEstimator.finish_calibration()` programmatically.
- Camera resolution in `Camera` is set to 640×480; you can increase it but might affect performance.

## Tuning parameters

- Smoothing (`gaze_estimator.py` and `gaze_backend.py`): `alpha`, Kalman filter noise covariances, and `smoothing_factor` control jitter vs responsiveness.
- Blink detection (`click_backend.py`): `blink_threshold` and `consecutive_frames_required` control sensitivity to blinks.
- Scrolling (`scroll_backend.py`): `normal_scroll_amount`, `fast_scroll_amount`, and `scroll_cooldown` prevent overscrolling.

## Troubleshooting

- Permissions: Windows may require accessibility or input permission for PyAutoGUI to move the cursor. Run the app as a normal desktop app (not sandboxed) and allow input control.
- If MediaPipe fails to detect your face: check lighting, camera framing, and ensure the webcam is not used by another app.
- Cursor jumps or is unresponsive: check `gaze_backend.py` calibrated mapping offsets (lines that amplify and clamp gaze ratios). Use smaller smoothing values to reduce lag.
- If the app freezes on a bad frame, many backends include try/except; inspect logs printed in the console for exceptions.

## Development & Testing

- To collect calibration data, run `python -m src.data_collector` and follow on-screen prompts.
- Unit-testable logic: `eyeextractor` math, `gaze_estimator` calibration mapping, and `gaze_backend` zone calculation.

## LLM context snippet

Use the snippet below when asking an LLM for help improving or debugging the project. It contains the most relevant facts.

```json
{
  "project": "Gaze CV Kalman",
  "entry": "main.py",
  "key_files": ["src/eyeextractor.py","src/gaze_estimator.py","src/gaze_backend.py","src/click_backend.py","src/scroll_backend.py","src/facemesh.py"],
  "data_shapes": {
    "camera_frame": "(480, 640, 3)",
    "gaze_ratio": "float pair in [0,1]",
    "gaze_point": "(x_pixel, y_pixel)",
    "zone": "1-9 int (3x3 grid)"
  },
  "common_issues": [
    "cursor jitter — tune smoothing/Kalman/processNoiseCov",
    "incorrect mapping — recalibrate or change polynomial mapping in GazeEstimator",
    "blink false-positive — raise blink_threshold or require more frames"
  ]
}
```

## Notes

- This project directly moves the system cursor and performs clicks — close the app or disable backends when debugging to avoid unintended input.
