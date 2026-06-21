import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

from src.gaze_engine import GazeEngine
from src.dashboard import GazeTrackerUI
from src.mini_dashboard import MiniDashboard


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
        self.dashboard = GazeTrackerUI(self.engine)
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

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # left-click
            self.open_mini()

    def open_mini(self):
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