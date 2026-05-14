from pathlib import Path
import time

import cv2
import mediapipe as mp


MODEL_PATH = Path("face_landmarker.task")


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def main() -> None:
    if not MODEL_PATH.exists():
        print(f"Error: Model file not found: {MODEL_PATH}")
        print("Download 'face_landmarker.task' and place it in this project folder.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    RunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=RunningMode.VIDEO,
        num_faces=1,
    )

    # Iris center landmarks when present.
    # 468 = right iris center, 473 = left iris center.
    right_pupil_idx = 468
    left_pupil_idx = 473
    right_eye_outer_idx = 33
    right_eye_inner_idx = 133
    right_eye_top_idx = 159
    right_eye_bottom_idx = 145
    left_eye_inner_idx = 362
    left_eye_outer_idx = 263
    left_eye_top_idx = 386
    left_eye_bottom_idx = 374

    print("Camera opened. Press 'q' to quit.")

    with FaceLandmarker.create_from_options(options) as face_landmarker:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame from camera.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(time.time() * 1000)

            result = face_landmarker.detect_for_video(mp_image, timestamp_ms)

            if result.face_landmarks:
                face_landmarks = result.face_landmarks[0]
                frame_h, frame_w = frame.shape[:2]

                for idx, color, label in (
                    (right_pupil_idx, (0, 255, 0), "R"),
                    (left_pupil_idx, (0, 255, 255), "L"),
                ):
                    if idx >= len(face_landmarks):
                        continue

                    landmark = face_landmarks[idx]
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)

                    cv2.circle(frame, (x, y), 4, color, -1)
                    cv2.putText(
                        frame,
                        label,
                        (x + 6, y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1,
                        cv2.LINE_AA,
                    )

                right_iris = face_landmarks[right_pupil_idx]
                left_iris = face_landmarks[left_pupil_idx]

                right_outer = face_landmarks[right_eye_outer_idx]
                right_inner = face_landmarks[right_eye_inner_idx]
                right_top = face_landmarks[right_eye_top_idx]
                right_bottom = face_landmarks[right_eye_bottom_idx]
                left_inner = face_landmarks[left_eye_inner_idx]
                left_outer = face_landmarks[left_eye_outer_idx]
                left_top = face_landmarks[left_eye_top_idx]
                left_bottom = face_landmarks[left_eye_bottom_idx]

                right_w = max(abs(right_inner.x - right_outer.x), 1e-6)
                left_w = max(abs(left_outer.x - left_inner.x), 1e-6)
                right_h = max(abs(right_bottom.y - right_top.y), 1e-6)
                left_h = max(abs(left_bottom.y - left_top.y), 1e-6)

                right_x = (right_iris.x - right_outer.x) / right_w
                left_x = (left_iris.x - left_inner.x) / left_w
                right_y = (right_iris.y - right_top.y) / right_h
                left_y = (left_iris.y - left_top.y) / left_h

                gaze_x = clamp01((right_x + left_x) / 2.0)
                gaze_y = clamp01((right_y + left_y) / 2.0)
                gaze = {"gaze_x": float(gaze_x), "gaze_y": float(gaze_y)}
                print(gaze)

                cv2.putText(
                    frame,
                    f"gaze_x: {gaze_x:.3f} gaze_y: {gaze_y:.3f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow("OpenCV + MediaPipe Tasks Pupil Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
