import pyautogui
import time

class ScrollBackend:
    def __init__(self):
        pyautogui.PAUSE = 0.0
        pyautogui.FAILSAFE = False  # prevents cursor from freezing at corners
        
        self.normal_scroll_amount = 3
        self.fast_scroll_amount = 6

        # cooldown prevents scroll firing 30x per second
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.4  # seconds between each scroll action

    def scroll_up(self, speed="normal"):
        clicks = self.fast_scroll_amount if speed == "fast" else self.normal_scroll_amount
        pyautogui.scroll(clicks)

    def scroll_down(self, speed="normal"):
        clicks = self.fast_scroll_amount if speed == "fast" else self.normal_scroll_amount
        pyautogui.scroll(-clicks)

    def handle_gaze_scrolling(self, zone_id):
        # check cooldown before scrolling
        now = time.time()
        if now - self.last_scroll_time < self.scroll_cooldown:
            return  # too soon, skip this frame

        if zone_id in [1, 2, 3]:
            self.scroll_up(speed="normal")
            self.last_scroll_time = now
            print("Gaze Scroll UP")
        elif zone_id in [7, 8, 9]:
            self.scroll_down(speed="normal")
            self.last_scroll_time = now
            print("Gaze Scroll DOWN")
