import pyautogui

class GazeBackend:
    def __init__(self):
        #fetches physical monitor's height and width
        self.screen_w = int(pyautogui.size()[0])
        self.screen_h = int(pyautogui.size()[1])
        
        pyautogui.PAUSE = 0.0  #removes built in delay between commands
        pyautogui.FAILSAFE = True 
        
        self.smoothing_factor = 0.45 #smooths out eye jitters
        self.current_smoothed_x = float(self.screen_w / 2)
        self.current_smoothed_y = float(self.screen_h / 2)

    def process_raw_landmarks(self, landmarks):
        pass

    def update_mouse_position(self, ml_screen_x_pct, ml_screen_y_pct):
        if ml_screen_x_pct is None or ml_screen_y_pct is None:
            return

        raw_ml_x = float(ml_screen_x_pct)
        raw_ml_y = float(ml_screen_y_pct)
        #calibration formula - to span the entire screen 
        amplified_x = (raw_ml_x - 0.40) / (0.70 - 0.40)
        amplified_y = (raw_ml_y - 0.15) / (0.45 - 0.15)

        amplified_x = max(0.0, min(1.0, amplified_x))
        amplified_y = max(0.0, min(1.0, amplified_y))
        # converts into exact, real-world pixel target coordinates
        target_pixel_x = amplified_x * self.screen_w
        target_pixel_y = amplified_y * self.screen_h
        #LERP - calculates where the cursor is right now and where the
        #eye wants to go and moves it 45% of the way there
        self.current_smoothed_x += (target_pixel_x - self.current_smoothed_x) * self.smoothing_factor
        self.current_smoothed_y += (target_pixel_y - self.current_smoothed_y) * self.smoothing_factor

        final_x = int(round(self.current_smoothed_x))
        final_y = int(round(self.current_smoothed_y))
        #sets 40 pixel padding boundary around the edges
        final_x = max(40, min(self.screen_w - 40, final_x))
        final_y = max(40, min(self.screen_h - 40, final_y))
        #calls PyAutoGUI to command mouse to computed coordinates
        pyautogui.moveTo(final_x, final_y)

    def calculate_current_zone(self):
        try:
            current_x, current_y = pyautogui.position()
        except Exception:
            current_x, current_y = int(self.screen_w / 2), int(self.screen_h / 2)
        # forms 3x3 grid on screen 
        col = int((current_x / self.screen_w) * 3)
        col = max(0, min(2, col))

        row = int((current_y / self.screen_h) * 3)
        row = max(0, min(2, row))

        zone_id = (row * 3) + col + 1
        return zone_id