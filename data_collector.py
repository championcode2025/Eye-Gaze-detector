import cv2
import csv
import time
import numpy as np
from camera import Camera
from facemesh import FaceMesh
from eyeextractor import EyeExtractor

def run_data_collection(filename="gaze_dataset.csv"):
    cam = Camera(device_index=0)
    face_mesh = FaceMesh()
    extractor = EyeExtractor()
    
    window_name = "Data Collection"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Standard screen boundaries (Adjust if your primary monitor layout differs)
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    
    # 5x5 grid of target points
    points = []
    for x in np.linspace(100, SCREEN_WIDTH - 100, 5):
        for y in np.linspace(100, SCREEN_HEIGHT - 100, 5):
            points.append((int(x), int(y)))
            
    # ==========================================
    # STEP 1: FACE ALIGNMENT PHASE
    # ==========================================
    print("\n=== STEP 1: ALIGN YOUR FACE ===")
    print("Look at the screen. Make sure you are clearly visible in the preview box.")
    print("Press [SPACEBAR] to start calibration when ready.")
    
    while True:
        frame = cam.read()
        if frame is None:
            continue
            
        screen = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
        
        # Display instructions on screen
        cv2.putText(screen, "Center your face in the preview box", (50, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(screen, "Press SPACEBAR to begin", (50, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # Put camera preview in bottom right corner
        preview = cv2.resize(frame, (400, 300))
        screen[SCREEN_HEIGHT-300:, SCREEN_WIDTH-400:] = preview
        
        cv2.imshow(window_name, screen)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '): 
            break
        elif key == 27: # ESC key to abort
            cam.release()
            cv2.destroyAllWindows()
            return

    print("\n=== STEP 2: STARTING DATA COLLECTION ===")
    
    # ==========================================
    # STEP 2: RE-RUN POINT TRACKING WITH PREVIEWS
    # ==========================================
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'raw_gaze_x', 'raw_gaze_y', 'screen_target_x', 'screen_target_y'])
        
        for i, (target_x, target_y) in enumerate(points):
            # 1-second warning state (Dot is RED: move eyes here)
            start_prep = time.time()
            while time.time() - start_prep < 1.0:
                frame = cam.read()
                screen = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
                cv2.circle(screen, (target_x, target_y), 15, (0, 0, 255), -1) 
                
                if frame is not None:
                    preview = cv2.resize(frame, (200, 150))
                    screen[SCREEN_HEIGHT-150:, SCREEN_WIDTH-200:] = preview
                cv2.imshow(window_name, screen)
                cv2.waitKey(1)

            # 2-second recording state (Dot is GREEN: tracking frames)
            start_time = time.time()
            face_detected_for_point = False
            
            while time.time() - start_time < 2.0:
                frame = cam.read()
                if frame is None:
                    continue
                
                screen = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
                cv2.circle(screen, (target_x, target_y), 15, (0, 255, 0), -1)
                
                # Render continuous live PiP window
                preview = cv2.resize(frame, (200, 150))
                screen[SCREEN_HEIGHT-150:, SCREEN_WIDTH-200:] = preview
                cv2.imshow(window_name, screen)
                
                landmarks = face_mesh.process(frame)
                if landmarks:
                    face_detected_for_point = True
                    gaze_data = extractor.extract(landmarks, frame.shape)
                    
                    gaze_point = gaze_data.get('gaze_point')
                    if gaze_point and len(gaze_point) >= 2:
                        raw_x = gaze_data.get('gaze_ratio_x')
                        raw_y = gaze_data.get('gaze_ratio_y')
                    else:
                        raw_x, raw_y = None, None
                    
                    if raw_x is not None and raw_y is not None:
                        writer.writerow([time.time(), round(raw_x, 5), round(raw_y, 5), target_x, target_y])
                    else:
                        # Safety check if key names are different
                         print(f"⚠ Key name mismatch! Available keys in your extractor: {list(gaze_data.keys())}")
                
                if cv2.waitKey(1) & 0xFF == 27:
                    print("Data collection stopped early.")
                    cam.release()
                    cv2.destroyAllWindows()
                    return
            
            if not face_detected_for_point:
                print(f"❌ Point {i+1}: MediaPipe completely lost your face! Stay centered.")
            else:
                print(f"✓ Point {i+1}/{len(points)} recorded.")

    cam.release()
    cv2.destroyAllWindows()
    print(f"\nSuccess! Your dataset has been saved to '{filename}' with actual data coordinates.")

if __name__ == "__main__":
    run_data_collection()