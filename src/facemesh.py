import cv2 
import mediapipe as mp

class FaceMesh:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh 

        self.detector = self.mp_face_mesh.FaceMesh(
            max_num_faces = 1,
            refine_landmarks = True,
            min_detection_confidence = 0.5,
            min_tracking_confidence = 0.5
        )

        print("facemesh detector ready")

    def process(self,frame):

        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        rgb_frame.flags.writeable = False 

        results = self.detector.process(rgb_frame)

        rgb_frame.flags.writeable = True

        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
        else:
            return None
        
    def close(self):
        self.detector.close()
        print("facemesh detector closed")