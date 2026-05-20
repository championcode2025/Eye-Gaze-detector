import numpy as np

LEFT_IRIS  = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

LEFT_EYE_INNER   = 133
LEFT_EYE_OUTER   = 33
LEFT_EYE_TOP     = 159
LEFT_EYE_BOTTOM = 145

RIGHT_EYE_INNER  = 362
RIGHT_EYE_OUTER  = 263
RIGHT_EYE_TOP    = 386
RIGHT_EYE_BOTTOM = 374

class EyeExtractor:
    def extract(self, landmarks, frame_shape):
        h, w = frame_shape[:2]

        left_iris  = self._get_iris_center(landmarks, LEFT_IRIS,  w, h)
        right_iris = self._get_iris_center(landmarks, RIGHT_IRIS, w, h)

        # Relative ratio instead of raw pixel zone
        # FIXED: Match left_iris with left eye landmarks (263, 362...) 
        # and right_iris with right eye landmarks (33, 133...)
        left_ratio  = self._get_iris_ratio(landmarks, left_iris,
                                           263, 362, 386, 374, w, h)
        right_ratio = self._get_iris_ratio(landmarks, right_iris,
                                           33,  133, 159, 145, w, h)

        gaze_ratio_x = (left_ratio[0] + right_ratio[0]) / 2
        gaze_ratio_y = (left_ratio[1] + right_ratio[1]) / 2

        zone       = self._get_zone(gaze_ratio_x, gaze_ratio_y)
        gaze_point = (int(gaze_ratio_x * w), int(gaze_ratio_y * h))

        return {
            "left_iris":  left_iris,
            "right_iris": right_iris,
            "gaze_ratio_x": gaze_ratio_x,  # Exposes the true decimal X value [0, 1]
            "gaze_ratio_y": gaze_ratio_y,  # Exposes the true decimal Y value [0, 1]
            "gaze_point": gaze_point,
            "zone":       zone,
        }
    
    def _get_iris_center(self, landmarks, indices, w, h):
        '''
        Averages the 4 iris landmark points to get the center
        MEDIAPIPE gives coords as float values between 0.0 and 1.0
        multiplying by w and h gives us pixel coordinates
        '''
        coords = [
            (landmarks[i].x * w, landmarks[i].y * h)
            for i in indices
        ]
        center = np.mean(coords, axis=0)
        return (int(center[0]), int(center[1]))
    
    def _average_point(self, point_a, point_b):
        avg_x = (point_a[0] + point_b[0]) // 2
        avg_y = (point_a[1] + point_b[1]) // 2
        return (avg_x, avg_y)
    
    def _get_iris_ratio(self, landmarks, iris_center,
                        outer_idx, inner_idx,
                        top_idx, bottom_idx,
                        w, h):
        outer_x  = landmarks[outer_idx].x * w
        inner_x  = landmarks[inner_idx].x * w
        top_y    = landmarks[top_idx].y   * h
        bottom_y = landmarks[bottom_idx].y * h

        eye_width  = abs(inner_x - outer_x)
        eye_height = abs(bottom_y - top_y)

        if eye_width < 1 or eye_height < 1:
            return (0.5, 0.5)

        left_x = min(outer_x, inner_x)
        top_y  = min(top_y, bottom_y)

        ratio_x = (iris_center[0] - left_x) / eye_width
        ratio_y = (iris_center[1] - top_y)  / eye_height

        ratio_x = max(0.0, min(1.0, ratio_x))
        ratio_y = max(0.0, min(1.0, ratio_y))

        return (ratio_x, ratio_y)

    def _get_zone(self, ratio_x, ratio_y):
        if ratio_x < 0.40:        
            col = 0
        elif ratio_x < 0.60:      
            col = 1
        else:                     
            col = 2

        if ratio_y < 0.40:        
            row = 0
        elif ratio_y < 0.60:      
            row = 1
        else:                     
            row = 2

        return row * 3 + col