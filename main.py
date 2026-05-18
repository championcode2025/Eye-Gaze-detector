import cv2 
from camera import Camera
from facemesh import FaceMesh
from eyeextractor import EyeExtractor 
from visualiser import Visualiser
from gaze_estimator import GazeEstimator

def main():
    # camera setup
    cam = Camera(device_index=0)
    
    # mediapipe facemesh
    face_mesh = FaceMesh()

    # computes iris centers + gaze zone
    extractor = EyeExtractor()
    
    # YOUR CODE: Gaze estimator for calibration + smoothing
    estimator = GazeEstimator()
    
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
            
            # YOUR CODE: Pass raw gaze through estimator
            gaze_estimate = estimator.estimate(
                gaze_data.get('gaze_ratio_x', 0.5),
                gaze_data.get('gaze_ratio_y', 0.5),
                frame.shape[1],
                frame.shape[0]
            )
            
            print(f"Zone:{gaze_data['zone']} | "
                  f"Raw gaze: ({gaze_data.get('gaze_ratio_x', 0.5):.2f}, {gaze_data.get('gaze_ratio_y', 0.5):.2f}) | "
                  f"Estimated: ({gaze_estimate['gaze_x']:.2f}, {gaze_estimate['gaze_y']:.2f})")
            
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