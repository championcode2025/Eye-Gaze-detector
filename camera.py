# handles webcam access using opencv

import cv2

class Camera:
    def __init__(self, device_index=0):
        # index=0 is inn-built camera, 1 = external camera
        self.cap = cv2.VideoCapture(device_index)

        if not self.cap.isOpened():
            raise RuntimeError(
                "could not open camera"
            )
        
        # setting resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("camera opened")

    def read(self):
        # frame is a numpy array of shape(h,w,3)
        # 3 = blue,green,red channels (BGR)
        ret,frame = self.cap.read()
        if not ret:
            return None 
        
        frame = cv2.flip(frame,1) # inverts the movement of the user to the camera 
        # basically done to move right when user moves to the right 
        return frame 
    
def get_dimensions(self):
    # used to calculate the gaze zones 
    width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return width, height

def release(self):
    # frees the webcam so other apps can use it
    self.cap.release()
    print("camera released")
    
           