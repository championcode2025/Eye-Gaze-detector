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

        #extract eye data
        if landmarks:
            gaze_data = extractor.extract(landmarks, frame.shape)
            
            # 1. Grab the clean decimal ratios [0.0 to 1.0] from your updated eyeextractor
            raw_ratio_x = gaze_data.get('gaze_ratio_x', 0.5)
            raw_ratio_y = gaze_data.get('gaze_ratio_y', 0.5)
            
            # 2. Pass those decimal ratios directly into your ML estimator
            gaze_estimate = estimator.estimate(
                raw_ratio_x,
                raw_ratio_y,
                frame.shape[1],
                frame.shape[0]
            )
            
            # 3. Print the ratios so you can see them dynamically shifting as you look around
            print(f"Zone:{gaze_data['zone']} | "
                  f"Raw Ratio: ({raw_ratio_x:.3f}, {raw_ratio_y:.3f}) | "
                  f"Screen Prediction: ({gaze_estimate['gaze_x']:.2f}, {gaze_estimate['gaze_y']:.2f})")
            
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