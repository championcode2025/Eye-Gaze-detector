from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt


class OverlayWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setFixedSize(420, 260)

        self.setStyleSheet("""
        QWidget{
            background-color:rgba(8,18,38,235);
            border:1px solid #22D3EE;
            border-radius:22px;
        }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18,18,18,18)
        main_layout.setSpacing(10)
    
        # ===== HEADER =====

        header = QHBoxLayout()

        title_layout = QVBoxLayout()

        title = QLabel("GAZE TRACKER")

        title.setStyleSheet("""
        color:white;
        font-size:25px;
        font-weight:700;
        border:none;
        """)

        subtitle = QLabel(
            "Focused. Aware. Empowered."
        )

        subtitle.setStyleSheet("""
        color:#7EA8D8;
        font-size:13px;
        border:none;
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout)

        main_layout.addLayout(header)
                
        # ===== TRACKING CARD =====

        tracking_card = QLabel(
            "🟢 TRACKING ACTIVE"
        )

        tracking_card.setAlignment(
            Qt.AlignCenter
        )

        tracking_card.setStyleSheet("""
        background-color:#0F2448;
        color:#22FF99;
        font-size:15px;
        font-weight:700;
        padding:12px;
        border-radius:14px;
        border:1px solid #163E78;
        """)

        main_layout.addWidget(
            tracking_card
        )

        # ===== STATS ROW =====

        stats_row = QHBoxLayout()

        self.zone = QLabel("ZONE\n-")
        self.click = QLabel("CLICK\nREADY")

        for label in [
            self.zone,
            self.click
        ]:

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setStyleSheet("""
            background-color:#0F2448;
            color:white;
            font-size:13px;
            font-weight:600;
            padding:10px;
            border-radius:12px;
            border:1px solid #163E78;
            """)

            stats_row.addWidget(label)

        main_layout.addLayout(
            stats_row
        )

        # ===== FOOTER =====

        footer = QLabel(
            "System Overlay Active"
        )

        footer.setStyleSheet("""
        color:#22D3EE;
        font-size:14px;
        border:none;
        """)

        main_layout.addWidget(
            footer
        )
        self.setLayout(
            main_layout
        )
        self.move(20,20)