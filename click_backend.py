import pyautogui
import numpy as np

class ClickBackend:
    def __init__(self):
        #targetted mathematical cutoff for blink
        self.blink_threshold = 0.16
        self.consecutive_frames_required = 3 #eyes should stay closed for atleast 3 frames
        self.frame_counter = 0 #counts number of frames for which eye remained closed
        self.has_clicked = False #prevents spamming continuous clicks
        pyautogui.PAUSE = 0.0 #click happens as soon as blink is detected

    def calculate_ear(self, landmarks, eye_indices, w, h):
        #extract coordinate positions of six points that form eye shape
        p2_x, p2_y = landmarks[eye_indices[0]].x * w, landmarks[eye_indices[0]].y * h
        p6_x, p6_y = landmarks[eye_indices[1]].x * w, landmarks[eye_indices[1]].y * h
        p3_x, p3_y = landmarks[eye_indices[2]].x * w, landmarks[eye_indices[2]].y * h
        p5_x, p5_y = landmarks[eye_indices[3]].x * w, landmarks[eye_indices[3]].y * h
        p1_x, p1_y = landmarks[eye_indices[4]].x * w, landmarks[eye_indices[4]].y * h
        p4_x, p4_y = landmarks[eye_indices[5]].x * w, landmarks[eye_indices[5]].y * h
        #distance formula to calculate vertical heights
        v1 = np.sqrt((p2_x - p6_x)**2 + (p2_y - p6_y)**2)
        v2 = np.sqrt((p3_x - p5_x)**2 + (p3_y - p5_y)**2)
        horizontal = np.sqrt((p1_x - p4_x)**2 + (p1_y - p4_y)**2)

        if horizontal == 0:#safety
            return 0.5

        return (v1 + v2) / (2.0 * horizontal)#standard EAR equation

    def process_blink_click(self, landmarks):
        if not landmarks:#face out of frame
            return

        w, h = 640, 480
        left_eye_indices = [159, 145, 158, 153, 33, 133]
        #finds out how happe left eye is
        left_ear = self.calculate_ear(landmarks, left_eye_indices, w, h)

        if left_ear < self.blink_threshold:
            self.frame_counter += 1
            if self.frame_counter >= self.consecutive_frames_required and not self.has_clicked:
                pyautogui.click()
                print("Blinking Detected - Left-Click Executed")
                self.has_clicked = True
        else:
            self.frame_counter = 0
            self.has_clicked = False