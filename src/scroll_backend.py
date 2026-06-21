import pyautogui
import time


class ScrollBackend:
    """
    Scroll is triggered by looking at a virtual scrollbar region on the
    right edge of the frame: top-edge strip = scroll up, bottom-edge
    strip = scroll down. A fixed gaze-lock (dwell) time is required
    inside that narrow region before the first scroll fires, so glancing
    at top/bottom-center (not the edge) never triggers scrolling.
    """

    def __init__(self):
        pyautogui.PAUSE = 0.0
        pyautogui.FAILSAFE = False  # was True — caused cursor to freeze at corners

        self.normal_scroll_amount = 3
        self.fast_scroll_amount = 6

        # Virtual scrollbar region: right edge strip of the frame.
        # Tune these if the trigger area feels too big/small or
        # mismatched with your actual screen aspect ratio.
        self.EDGE_X_THRESHOLD = 0.88     # gaze_x beyond this = near right edge
        self.TOP_Y_THRESHOLD = 0.20      # gaze_y below this (within edge) = scroll up
        self.BOTTOM_Y_THRESHOLD = 0.80   # gaze_y above this (within edge) = scroll down

        # Dwell / lock requirements
        self.LOCK_TIME = 0.6             # seconds of continuous gaze before first trigger
        self.scroll_cooldown = 0.4       # seconds between repeated scroll ticks once locked

        self._current_region = None      # "up" | "down" | None
        self._region_entered_at = None
        self.last_scroll_time = 0

    def _get_region(self, gaze_x, gaze_y):
        if gaze_x is None or gaze_y is None:
            return None
        if gaze_x < self.EDGE_X_THRESHOLD:
            return None
        if gaze_y < self.TOP_Y_THRESHOLD:
            return "up"
        if gaze_y > self.BOTTOM_Y_THRESHOLD:
            return "down"
        return None

    def scroll_up(self, speed="normal"):
        clicks = self.fast_scroll_amount if speed == "fast" else self.normal_scroll_amount
        pyautogui.scroll(clicks)

    def scroll_down(self, speed="normal"):
        clicks = self.fast_scroll_amount if speed == "fast" else self.normal_scroll_amount
        pyautogui.scroll(-clicks)

    def handle_gaze_scrolling(self, gaze_x, gaze_y):
        """
        Call every frame with the raw normalized gaze position
        (gaze_x, gaze_y in [0,1], full-frame ratio — same values
        already used as last_gaze_x/last_gaze_y elsewhere).
        """
        now = time.time()
        region = self._get_region(gaze_x, gaze_y)

        if region != self._current_region:
            # Entered a new region (or left the edge) — reset the lock timer.
            self._current_region = region
            self._region_entered_at = now if region else None
            return

        if region is None or self._region_entered_at is None:
            return

        dwell = now - self._region_entered_at
        if dwell < self.LOCK_TIME:
            return  # still locking — not triggered yet

        if now - self.last_scroll_time < self.scroll_cooldown:
            return

        if region == "up":
            self.scroll_up()
            print("📜 Gaze Scroll UP (edge-lock)")
        else:
            self.scroll_down()
            print("📜 Gaze Scroll DOWN (edge-lock)")

        self.last_scroll_time = now