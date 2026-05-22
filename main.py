import cv2 
from camera import Camera
from facemesh import FaceMesh
from eyeextractor import EyeExtractor 
from visualiser import Visualiser
from gaze_estimator import GazeEstimator
from gaze_backend import GazeBackend     
from click_backend import ClickBackend   
from scroll_backend import ScrollBackend 

def main():
    cam = Camera(device_index=0)
    face_mesh = FaceMesh()
    extractor = EyeExtractor()
    visualiser = Visualiser()
    estimator = GazeEstimator()
    movement_engine = GazeBackend()
    click_engine = ClickBackend()
    scroll_engine = ScrollBackend()      

    print("SYSTEM RUNNING: Press 'q' to quit.")

    while True:
        frame = cam.read()
        if frame is None:
            break
        
        landmarks = face_mesh.process(frame)

        if landmarks:
            gaze_data = extractor.extract(landmarks, frame.shape)

            raw_ratio_x = gaze_data.get("gaze_ratio_x", 0.5)
            raw_ratio_y = gaze_data.get("gaze_ratio_y", 0.5)
            
            gaze_estimate = estimator.estimate(
                raw_ratio_x,
                raw_ratio_y,
                frame.shape[1],
                frame.shape[0]
            )
            
            ml_x_pct = gaze_estimate.get('gaze_x', 0.5)
            ml_y_pct = gaze_estimate.get('gaze_y', 0.5)
            
            if ml_x_pct is not None and ml_y_pct is not None:
                try:
                    movement_engine.update_mouse_position(ml_x_pct, ml_y_pct)
                except Exception as e:
                    print(f"CURSOR ERROR: {e}")  
                current_zone = movement_engine.calculate_current_zone()   
                scroll_engine.handle_gaze_scrolling(current_zone)        
                print(f"Zone: {current_zone} | X: {ml_x_pct:.3f} | Y: {ml_y_pct:.3f}")

            click_engine.process_blink_click(landmarks)
            frame = visualiser.draw(frame, landmarks, gaze_data)

        cv2.imshow("Gaze Tracker", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    print("Program shut down cleanly.")

if __name__ == "__main__":
    main()