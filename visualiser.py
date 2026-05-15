'''
for visual output of the processes taking place in
eyeextractor.py and facemesh.py
'''

import cv2

GREEN = (0,255,0) #  iris center dots
YELLOW = (0,255,255) # gaze point
WHITE = (255,255,255) # text labels
RED = (0,0,255) # eye corner dots
GRAY= (180,180,180) # zone grid lines


# points that outline the eyes based on mediapipe facemesh
LEFT_EYE_OUTLINE = [33, 7, 163, 144, 145, 153,
                     154, 155, 133, 173, 157, 158,
                     159, 160, 161, 246]
RIGHT_EYE_OUTLINE = [362, 382, 381, 380, 374, 373,
                      390, 249, 263, 466, 388, 387,
                      386, 385, 384, 398]

class Visualiser:
    def draw(self, frame, landmarks, gaze_data):
        frame = self._draw_zone_grid(frame)
        frame = self._draw_eye_outlines(frame, landmarks)
        frame = self._draw_iris_centers(frame, gaze_data)
        frame = self._draw_gaze_point(frame, gaze_data)
        frame = self._draw_zone_label(frame, gaze_data)
        # layering the drawings on top of each other 
        # og frame - grid - eye outlines - iris centers - gaze point - labels
        return frame 
    
    def _draw_zone_grid(self, frame):
        h, w = frame.shape[:2]

        cv2.line(frame, (w//3, 0), (w//3,h), GRAY, 1)
        cv2.line(frame, (w*2//3,0), (w*2//3,h), GRAY, 1)
        cv2.line(frame, (0,h//3), (w,h//3), GRAY, 1)
        cv2.line(frame, (0,h*2//3), (w,h*2//3), GRAY, 1)

        return frame 
    
    def _draw_eye_outlines(self, frame, landmarks):
        h, w = frame.shape[:2]

        for indices in [LEFT_EYE_OUTLINE, RIGHT_EYE_OUTLINE]:
            for idx in indices:
                lm = landmarks[idx]
                x = int(lm.x*w)
                y = int(lm.y*h)
                cv2.circle(frame, (x,y), 1, RED, -1)
        return frame 
    
    def _draw_iris_centers(Self, frame, gaze_data):
        
        left = gaze_data["left_iris"]
        right = gaze_data["right_iris"]

        cv2.circle(frame, left, 5, GREEN, -1)
        cv2.circle(frame, right, 5, GREEN, -1)

        # white ring for contrast so we can see the green dots better
        cv2.circle(frame, left, 6, WHITE, 1)
        cv2.circle(frame, right, 6, WHITE, 1)

        return frame 
    
    def _draw_gaze_point(self, frame, gaze_data):
        # draws a yellow crosshair at the gaze point
        gx, gy = gaze_data["gaze_point"]
        size = 10

        cv2.line(frame, (gx-size, gy), (gx+size, gy), YELLOW, 2)
        cv2.line(frame, (gx, gy-size), (gx, gy+size), YELLOW, 2)
        
        return frame
    
    def _draw_zone_label(self, frame, gaze_data):
        # highlights the active zone cell
        h, w = frame.shape[:2]
        zone = gaze_data["zone"]

        # zone number text
        cv2.putText(
            frame,
            f"Zone: {zone}",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            WHITE,
            2,
            cv2.LINE_AA
        )

        row = zone//3
        col = zone%3

        x1 = col * (w//3)
        x2 = (col+1)*(w//3)
        y1 = row*(h//3)
        y2 = (row+1)*(h//3)

        cv2.rectangle(frame, (x1,y1), (x2,y2), YELLOW, 2)
        return frame 
    



