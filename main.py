import cv2 
from src.camera import Camera
from src.facemesh import FaceMesh
from src.eyeextractor import EyeExtractor 
from src.visualiser import Visualiser 

def main():
    # camera setup
    cam = Camera(device_index=0)
    
    # mediapipe facemesh
    face_mesh = FaceMesh()

    # computes iris centers + gaze zone
    extractor = EyeExtractor()
    
    # draws landmarks on screen
    visualiser = Visualiser()

    print("gaze tracker running, press q to quit")

    while True:
        # grab frame
        frame = cam.read()
        if frame is None:
            print("no frame received. check webcam")
            break
        
        # detect face landmarks
        landmarks = face_mesh.process(frame)

        # extract eye data
        if landmarks:
            gaze_data = extractor.extract(landmarks, frame.shape)
            print(f"Zone:{gaze_data['zone']} | "
                  f"Left: {gaze_data['left_iris']} | "
                  f"Right: {gaze_data['right_iris']}")
            
            # draw on frame
            frame = visualiser.draw(frame, landmarks, gaze_data)

        cv2.imshow("Gaze Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    print("gaze tracker stopped")

if __name__ == "__main__":
    main()

            