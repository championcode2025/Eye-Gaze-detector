# Gaze CV Kalman

A real-time, gaze-controlled interface that runs as a lightweight Windows system-tray application. It estimates eye gaze from a webcam and maps it to OS-level cursor movement, blink-clicks, and edge-triggered scrolling — built on MediaPipe FaceMesh, OpenCV, a Kalman filter for smoothing, and PyQt5 for the UI.

## Features

- **Real-time gaze tracking** using MediaPipe FaceMesh landmark detection
- **Kalman-filtered gaze estimation** to reduce frame-to-frame jitter without adding excessive lag
- **Cursor control** — gaze position is mapped to OS cursor movement via PyAutoGUI
- **Blink-to-click** — detects blinks and triggers a mouse click
- **Edge-lock scrolling** — looking at a narrow strip near the top or bottom of the right screen edge for a fixed dwell time triggers scroll up/down, similar to a virtual scrollbar. This avoids false triggers from glancing at the top/bottom-center or corner zones.
- **System tray application** — runs as a minimal background app:
  - A tray icon sits in the Windows "show hidden icons" area
  - **Left-click** the tray icon to open a small **mini dashboard** (live webcam thumbnail, tracking status, Pause/Resume, and quick access to the full dashboard)
  - **Right-click** for a context menu (Show Mini View / Open Full Dashboard / Quit)
  - A **full dashboard** is available for detailed monitoring: live webcam feed, tracking analytics (zone, gaze coordinates, click state), and a 3×3 interactive gaze-zone grid
  - The app launches **paused** by default — tracking/cursor control only activates once the user explicitly resumes it
  - A global **Esc hotkey** (labeled "Fn+Esc" in the UI, since Fn itself can't be detected in software) quits the app, via the optional `keyboard` package
- **Packaged as a standalone Windows `.exe`** using PyInstaller — no Python installation required to run it

## Project Structure

```
gaze cv kalman/
├── main.py                  — Tray app entry point (QSystemTrayIcon, hotkey, window wiring)
├── Gaze.spec                — PyInstaller build spec (MediaPipe bundling, UPX exclusions)
├── requirements.txt
├── src/
│   ├── gaze_engine.py        — Shared backend: owns camera + full pipeline, emits Qt signals
│   ├── dashboard.py           — Full PyQt5 dashboard UI (webcam feed, analytics, zone grid)
│   ├── mini_dashboard.py      — Minimal tray-popup UI (thumbnail, status, controls)
│   ├── theme.py               — Centralized design tokens (color, radius, spacing, typography)
│   ├── camera.py               — Webcam wrapper (OpenCV VideoCapture)
│   ├── facemesh.py             — MediaPipe FaceMesh wrapper
│   ├── eyeextractor.py         — Iris center extraction and raw gaze ratio calculation
│   ├── gaze_estimator.py       — Kalman-filtered gaze smoothing
│   ├── gaze_backend.py         — Maps gaze ratio to OS cursor position; 3×3 zone calculation
│   ├── click_backend.py        — Blink detection mapped to mouse click
│   ├── scroll_backend.py       — Edge-lock dwell-based scroll triggering
│   ├── visualiser.py           — OpenCV overlay drawing utilities
│   └── data_collector.py       — Offline calibration-dataset collection helper (currently unused/orphaned — collects a 25-point gaze dataset to CSV, but nothing in the app consumes it yet)
```

## How It Works (High-Level)

1. `GazeEngine` owns the camera, MediaPipe FaceMesh, and the full backend pipeline, running on a `QTimer` loop (~30ms interval).
2. Each frame: `FaceMesh` detects facial landmarks → `EyeExtractor` computes raw iris-based gaze ratios → `GazeEstimator` applies Kalman filtering to smooth the signal.
3. `GazeBackend` maps the smoothed gaze ratio to OS cursor position (with an amplification/clamping transform) and computes the current 3×3 gaze zone.
4. `ClickBackend` watches for blinks and triggers OS-level clicks.
5. `ScrollBackend` checks whether gaze is dwelling in a narrow region near the top or bottom of the right screen edge; after a fixed lock duration, it triggers scroll up/down.
6. `GazeEngine` emits two Qt signals every frame — `frame_ready` (the annotated video frame) and `data_ready` (zone, gaze coordinates, click/face-detection state) — which both `GazeTrackerUI` (full dashboard) and `MiniDashboard` (tray popup) subscribe to, so there's only ever one camera and one processing loop regardless of which window is open.

## Quickstart (Running from Source)

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

The tray icon should appear in the system tray. Left-click it to open the mini dashboard; the app launches paused, so click "Resume" to begin tracking.

## Building a Standalone Executable

The project includes a pre-configured `Gaze.spec` file that handles MediaPipe's data-file bundling and excludes specific files from UPX compression (to avoid a known `pyexpat` DLL corruption issue on Windows).

```powershell
.venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller --clean Gaze.spec
```

The resulting executable will be in the `dist/` folder. Always build from `Gaze.spec` rather than a raw `pyinstaller main.py` command — rebuilding from scratch without the spec will regenerate a default spec and silently lose the MediaPipe bundling and UPX-exclusion fixes.

**Notes specific to Windows builds:**
- Build using a clean, standalone CPython install (e.g. from python.org). Conda/Spyder-based interpreters split native DLLs (like `libexpat.dll`) into a separate `Library\bin` folder, a layout PyInstaller's dependency analyzer doesn't expect — this caused a `pyexpat` DLL crash in earlier builds.
- The Microsoft Visual C++ Redistributable (x64) should be installed on the target machine.
- Expect a build size in the hundreds of MB given the TensorFlow/MediaPipe/OpenCV dependencies — this is normal.

## Tuning Parameters

- **Kalman filter** (`gaze_estimator.py`): `processNoiseCov` and `measurementNoiseCov` control the responsiveness-vs-jitter tradeoff for gaze smoothing.
- **Cursor mapping** (`gaze_backend.py`): the amplification range (currently hardcoded, e.g. `0.40–0.70` for x, `0.15–0.45` for y) maps the *usable* raw gaze range to the full screen — this needs to be tuned per-user/per-camera-setup, and is one of the main targets for the calibration work described below.
- **Scroll edge-lock** (`scroll_backend.py`): `EDGE_X_THRESHOLD`, `TOP_Y_THRESHOLD`, `BOTTOM_Y_THRESHOLD` define the virtual scrollbar region; `LOCK_TIME` controls how long gaze must dwell there before the first scroll fires.
- **Blink detection** (`click_backend.py`): threshold and frame-count parameters control sensitivity to blinks.

## Troubleshooting

- **"Could not open camera"**: another application may be holding the webcam, or Windows camera privacy permissions may be blocking access (Settings → Privacy & security → Camera). The engine is designed to degrade gracefully — if the camera can't be opened, the app still launches and shows a "NO CAMERA DETECTED" placeholder instead of crashing, which is useful for testing the UI on a machine without a working camera.
- **DLL load errors on the built `.exe`**: typically caused by building inside a conda/Spyder environment, or running just `Gaze.exe` without its `_internal` folder alongside it (when built without `--onefile`-style spec configuration). Make sure the full `dist/Gaze` output is kept together if copying the build elsewhere.
- **Cursor jumps or feels unresponsive**: check the amplification/clamping values in `gaze_backend.py`, and the Kalman filter's process/measurement noise covariances in `gaze_estimator.py`.

## Future Scope

- **Better UI** — the current dashboard and mini-view use a shared design-token system (`theme.py`), but there's room to push further: smoother transitions/animations between tray and dashboard states, richer visual feedback for blink-clicks and scroll triggers, and a true custom app icon (currently a placeholder dot drawn in code).
- **Better gaze control** — the cursor-mapping amplification range is currently hardcoded per a rough estimate of "usable" eye movement, rather than being derived from actual measured per-user range. Planned improvements include adaptive Kalman tuning (responsive during saccades, smooth during fixation) and refining the scroll edge-zone thresholds based on real usage data rather than assumed gaze ranges.
- **Calibration logic for different screen dimensions** — the project has a 9-point calibration flow (`GazeEstimator`) and a more granular 25-point offline data collector (`data_collector.py`), but neither is currently wired into the live app, and the cursor-mapping logic assumes a fixed screen resolution. Future work should connect a calibration flow to `GazeBackend`'s amplification mapping so the gaze-to-cursor transform adapts automatically to the user's actual screen size and resolution, rather than relying on a fixed amplification range tuned for one setup.

## Notes

This project directly moves the system cursor and performs clicks — be mindful when testing, and consider pausing tracking (via the mini dashboard) before debugging other parts of the app.
