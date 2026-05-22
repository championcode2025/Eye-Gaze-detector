import cv2 
from camera import Camera
from facemesh import FaceMesh
from eyeextractor import EyeExtractor 
from visualiser import Visualiser
from gaze_estimator import GazeEstimator
from gaze_backend import GazeBackend     
from click_backend import ClickBackend   

def main():
    cam = Camera(device_index=0)
    face_mesh = FaceMesh()
    extractor = EyeExtractor()
    visualiser = Visualiser()
    estimator = GazeEstimator()
    movement_engine = GazeBackend()
    click_engine = ClickBackend()

    print("SYSTEM RUNNING: Press 'q' to quit.")

    while True:
        frame = cam.read() #pulls newest video matrix array frame
        if frame is None:
            break
        
        landmarks = face_mesh.process(frame)# passes videoframe to Facemesh that returns a data object of structural face map coordinate

        if landmarks:#human face detected
            gaze_data = extractor.extract(landmarks, frame.shape)#passes mesh landmarks to EyeExtractor
            left_ratio_tuple = gaze_data.get('left_ratio', (0.5, 0.5))
            
            raw_ratio_x = left_ratio_tuple[0]
            raw_ratio_y = left_ratio_tuple[1]
            
            gaze_estimate = estimator.estimate(
                raw_ratio_x,
                raw_ratio_y,
                frame.shape[1],
                frame.shape[0]
            )#runs raw values through model to understand where we are looking
            
            ml_x_pct = gaze_estimate.get('gaze_x', 0.5)
            ml_y_pct = gaze_estimate.get('gaze_y', 0.5)#0.5 is default value
            
            if ml_x_pct is not None and ml_y_pct is not None:
                #movement_engine.update_mouse_position(ml_x_pct, ml_y_pct)
                current_zone = movement_engine.calculate_current_zone()
                print(f"LIVE ML PREDICTION -> X: {ml_x_pct:.3f} | Y: {ml_y_pct:.3f}")
            click_engine.process_blink_click(landmarks)
            frame = visualiser.draw(frame, landmarks, gaze_data)

        cv2.imshow("Gaze Tracker Layout Diagnostic", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    print("Program shut down cleanly.")

if __name__ == "__main__":
    main()