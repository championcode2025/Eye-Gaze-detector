import cv2 
import mediapipe as mp

class FaceMesh:
    def __init__(self):
        # not created inside loop because expensive 
        self.mp_face_mesh = mp.solutions.face_mesh 
        self.detector = self.mp_face_mesh.FaceMesh(
            max_num_faces = 1, # 1 user's face
            refine_landmarks = True, # gives iris points
            min_detection_confidence = 0.6, # confidence score for face detection
            min_tracking_confidence = 0.6 # confidence score for continous tracking
        )
        print("facemesh detector ready")

    def process(self,frame):
        '''
        face detection on a single frame
        frame is the BGR numpy array from camera.py
        returns a list of landmark objects (478 points) if face is found
        '''
        # convert bgr to rgb otherwise colours will be wrong
        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        # make the frame non writable so mediapipe cannot change it back to array 
        rgb_frame.flags.writeable = False 

        results = self.detector.process(rgb_frame)

        # make frame writable again so visualiser can draw on it 
        rgb_frame.flags.writeable = True


        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark # return the first face's landmarks
        else:
            return None
        
    def close(self):
        self.detector.close()
        print("facemesh detector closed")


