import pyautogui

class ScrollBackend:
    def __init__(self):
        # Force strict processing delays to 0 for instant interface response
        pyautogui.PAUSE = 0.0
        pyautogui.FAILSAFE = True
        
        # Scroll strength configuration (Adjust these values to change scroll speed)
        self.normal_scroll_amount = 150
        self.fast_scroll_amount = 300

    def scroll_up(self, speed="normal"):
        """Scrolls the active window upwards."""
        clicks = self.fast_scroll_amount if speed == "fast" else self.normal_scroll_amount
        # Positive values scroll UP in PyAutoGUI
        pyautogui.scroll(clicks)

    def scroll_down(self, speed="normal"):
        """Scrolls the active window downwards."""
        clicks = self.fast_scroll_amount if speed == "fast" else self.normal_scroll_amount
        # Negative values scroll DOWN in PyAutoGUI
        pyautogui.scroll(-clicks)

    def handle_gaze_scrolling(self, zone_id):
        """
        Integrates with Person 4's 3x3 dashboard zones.
        If looking at the top row (zones 1, 2, 3) -> scroll up.
        If looking at the bottom row (zones 7, 8, 9) -> scroll down.
        """
        if zone_id in [1, 2, 3]:
            self.scroll_up(speed="normal")
            print("📜 Action: Gaze Scroll UP")
        elif zone_id in [7, 8, 9]:
            self.scroll_down(speed="normal")
            print("📜 Action: Gaze Scroll DOWN")