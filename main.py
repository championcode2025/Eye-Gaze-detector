from pathlib import Path
import time

import cv2
import mediapipe as mp


MODEL_PATH = Path("face_landmarker.task")


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
                    (right_pupil_idx, (0, 255, 0), "L"),
                    (left_pupil_idx, (0, 255, 255), "R"),
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

            cv2.imshow("OpenCV + MediaPipe Tasks Pupil Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
