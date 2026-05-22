import cv2 
import mediapipe as mp

class FaceMesh:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.detector = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        print("Native MediaPipe FaceMesh detector online and ready.")

    def process(self, frame):
        if frame is None:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False 
        results = self.detector.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark 
        return None

    def close(self):
        self.detector.close()
        print("MediaPipe face mesh tracking closed.")