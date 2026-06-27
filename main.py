import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QObject, pyqtSignal

from src.gaze_engine import GazeEngine
from src.dashboard import GazeTrackerUI
from src.mini_dashboard import MiniDashboard

# `keyboard` gives us a true OS-level global hotkey (works even with no
# app window focused/visible). It's optional at import time so the app
# doesn't crash on machines where it hasn't been installed yet --
# `pip install keyboard`.
try:
    import keyboard
    _KEYBOARD_AVAILABLE = True
except ImportError:
    _KEYBOARD_AVAILABLE = False

# NOTE: "Fn" has no keycode and can't be detected by any software --
# it's swallowed by the keyboard's own firmware before the OS sees it.
# What actually gets registered here is the Escape key itself, which is
# what your keyboard sends regardless of whether Fn is held. This is the
# real binding behind the "Fn+Esc" shortcut shown to the user.
EXIT_HOTKEY = "esc"


class _ExitHotkeyBridge(QObject):
    """keyboard's global hook fires from its own background thread, but
    Qt widgets/quit logic must only be touched from the main thread. The
    hook callback just emits this signal; Qt automatically queues the
    connected slot onto the main thread since the bridge object lives there."""
    triggered = pyqtSignal()


def make_placeholder_icon():
    # simple colored-dot icon — swap for a real .ico/.png later via QIcon("path.ico")
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#22D3EE"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(4, 4, 24, 24)
    painter.end()
    return QIcon(pixmap)


class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # tray keeps running after windows close

        self.engine = GazeEngine()
        # Start paused -- don't take over the cursor the instant the .exe
        # runs. The user turns tracking on explicitly from the mini view
        # or the dashboard (Pause/Resume, Start/Pause Tracking).
        if hasattr(self.engine, "pause"):
            self.engine.pause()

        # dashboard gets a callback so its "Back to Tray" button can hand
        # control back to this app instead of just hiding itself
        self.dashboard = GazeTrackerUI(self.engine, on_minimize_to_tray=self.open_mini)
        self.mini = MiniDashboard(self.engine, self.open_dashboard, self.quit_app)

        self.tray = QSystemTrayIcon(make_placeholder_icon(), parent=self.app)
        self.tray.setToolTip("Gaze CV Kalman")

        menu = QMenu()
        mini_action = QAction("Show Mini View")
        mini_action.triggered.connect(self.open_mini)
        menu.addAction(mini_action)

        full_action = QAction("Open Full Dashboard")
        full_action.triggered.connect(self.open_dashboard)
        menu.addAction(full_action)

        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

        self._exit_hotkey_bridge = _ExitHotkeyBridge()
        self._exit_hotkey_bridge.triggered.connect(self.quit_app)
        self._register_exit_hotkey()

    def _register_exit_hotkey(self):
        if not _KEYBOARD_AVAILABLE:
            print(
                "[gaze-tracker] 'keyboard' package not installed -- "
                "the Fn+Esc exit shortcut is disabled. Run: pip install keyboard"
            )
            return
        try:
            keyboard.add_hotkey(
                EXIT_HOTKEY,
                lambda: self._exit_hotkey_bridge.triggered.emit(),
            )
        except Exception as exc:
            print(f"[gaze-tracker] couldn't register global exit hotkey: {exc}")

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # left-click
            self.open_mini()

    def open_mini(self):
        self.dashboard.hide()
        self.mini.show()
        self.mini.raise_()

    def open_dashboard(self):
        self.mini.hide()
        self.dashboard.show()
        self.dashboard.raise_()

    def quit_app(self):
        self.engine.shutdown()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    tray_app = TrayApp()
    tray_app.run()