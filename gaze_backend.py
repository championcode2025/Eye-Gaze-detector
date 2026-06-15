import pyautogui

class GazeBackend:
    def __init__(self):
        self.screen_w = int(pyautogui.size()[0])
        self.screen_h = int(pyautogui.size()[1])
        
        pyautogui.PAUSE = 0.0
        pyautogui.FAILSAFE = False # prevents crash and freeze when cursor hits corner

        self.smoothing_factor = 0.25
         # Initializes the starting coordinates of your cursor tracking variables
        self.current_smoothed_x = float(self.screen_w / 2)
        self.current_smoothed_y = float(self.screen_h / 2)

        # store gaze position for zone calculation
        self.last_gaze_x = 0.5
        self.last_gaze_y = 0.5
        # sets initial active screen zone to zone 5
        self.current_zone = 5
        self.zone_change_threshold = 0.04

    def process_raw_landmarks(self, landmarks):
        pass

    def update_mouse_position(self, ml_screen_x_pct, ml_screen_y_pct):
        if ml_screen_x_pct is None or ml_screen_y_pct is None:
            return

        raw_ml_x = float(ml_screen_x_pct)
        raw_ml_y = float(ml_screen_y_pct)

        # save raw gaze for zone calculation
        self.last_gaze_x = raw_ml_x
        self.last_gaze_y = raw_ml_y

        # calibration formula - map usable gaze range to full screen
        # takes a tiny eye-movement range and stretches it out so that it expands to full 0.0 to 1.0 scale
        amplified_x = (raw_ml_x - 0.40) / (0.70 - 0.40)
        amplified_y = (raw_ml_y - 0.15) / (0.45 - 0.15)

        amplified_x = max(0.0, min(1.0, amplified_x))
        amplified_y = max(0.0, min(1.0, amplified_y))
        # converts decimal percentages into real-world monitor pixels
        target_pixel_x = amplified_x * self.screen_w
        target_pixel_y = amplified_y * self.screen_h

        # LERP smoothing
        # mouse does not move directly to where our eye points
        # calculates the distance between where the cursor is and where it wants to go
        # and multiplies it by smoothing_factor - gives cursor smooth feel
        self.current_smoothed_x += (target_pixel_x - self.current_smoothed_x) * self.smoothing_factor
        self.current_smoothed_y += (target_pixel_y - self.current_smoothed_y) * self.smoothing_factor

        final_x = int(round(self.current_smoothed_x))
        final_y = int(round(self.current_smoothed_y))

        # padding so cursor stays away from edges
        final_x = max(40, min(self.screen_w - 40, final_x))
        final_y = max(40, min(self.screen_h - 40, final_y))

        # wrap in try/except so one bad frame doesn't freeze everything
        try:
            pyautogui.moveTo(final_x, final_y)
        except Exception as e:
            print(f"Mouse move failed: {e}")

    def calculate_current_zone(self):
        # use gaze position directly, not cursor position
        col = int(self.last_gaze_x * 3)
        col = max(0, min(2, col))

        row = int(self.last_gaze_y * 3)
        row = max(0, min(2, row))

        new_zone = (row * 3) + col + 1

        # hysteresis: only change zone if gaze clearly moved
        if new_zone != self.current_zone:
            zone_width = 1.0 / 3
            gaze_center_x = (col + 0.5) * zone_width
            gaze_center_y = (row + 0.5) * zone_width

            prev_col = (self.current_zone - 1) % 3
            prev_row = (self.current_zone - 1) // 3
            prev_center_x = (prev_col + 0.5) * zone_width
            prev_center_y = (prev_row + 0.5) * zone_width

            movement = ((gaze_center_x - prev_center_x) ** 2 +
                        (gaze_center_y - prev_center_y) ** 2) ** 0.5

            if movement > self.zone_change_threshold:
                self.current_zone = new_zone

        return self.current_zone
