"""
Shared design tokens for the gaze tracker UI.

Goal: one place that defines color / radius / type so the main dashboard,
mini dashboard, and the OpenCV video overlay (visualiser.py) all agree on
what the app looks like. Edit a value here, it changes everywhere.

Color roles (use the ROLE, not the hex, when styling something new):
    BG          app background, the darkest layer
    SURFACE     card background (one level up from BG)
    SURFACE_RAISED  nested/inset panels sitting on top of a card
    BORDER      the one border color used everywhere (no more, no less)
    TEXT        primary readable text
    TEXT_MUTED  secondary / idle / caption text -- NOT the accent color
    ACCENT      reserved for "this is live / active / focused" only.
                Do not use it for headings, labels, or decoration -- if
                everything is the accent color, nothing reads as active.
    GOOD        face detected / tracking nominal
    WARN        no face / paused / attention needed
"""

from PyQt5.QtGui import QFont, QColor

# ---- Color tokens ---------------------------------------------------------

BG = "#0A0F1C"
SURFACE = "#111A2B"
SURFACE_RAISED = "#18233A"
BORDER = "#26334A"
TEXT = "#EAF1FB"
TEXT_MUTED = "#7E8CA3"
ACCENT = "#22D3EE"
ACCENT_DIM = "#0E2A33"   # accent's own "chip background" tint
GOOD = "#34D399"
GOOD_DIM = "#0F2A22"
WARN = "#F59E0B"
WARN_DIM = "#2C2110"

# ---- Radius scale (pick from this, don't invent new numbers) --------------

RADIUS_SM = 10   # chips, small buttons
RADIUS_MD = 16   # nested panels, zone boxes
RADIUS_LG = 22   # top-level cards

# ---- Spacing scale ----------------------------------------------------

SPACE_XS = 6
SPACE_SM = 12
SPACE_MD = 18
SPACE_LG = 26

# ---- Typography -------------------------------------------------------
# One family, used everywhere, with Qt's automatic cross-platform fallback
# if "Segoe UI" isn't present (e.g. on macOS/Linux). Hierarchy comes from
# size + weight + (real, code-applied) letter spacing -- not from
# QSS letter-spacing, which Qt's stylesheet engine silently ignores.

FONT_FAMILY = "Segoe UI"


def font(size, weight=QFont.Normal, tracking=0.0):
    """
    Build a QFont with *working* letter spacing.

    tracking: percentage spacing, e.g. 4 == 104% of normal advance width.
    Use small values (2-6) for header tracking, 0 for body text.
    """
    f = QFont(FONT_FAMILY, size, weight)
    if tracking:
        f.setLetterSpacing(QFont.PercentageSpacing, 100 + tracking)
    return f


# ---- Reusable QSS fragments ------------------------------------------------

def card_qss(radius=RADIUS_LG):
    """Flat, single-tone card -- no diagonal gradient. Contrast against BG
    does the work instead of a gradient pretending to be depth."""
    return f"""
        QFrame {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: {radius}px;
        }}
    """


def chip_qss(fg, bg):
    return f"""
        QLabel {{
            background: {bg};
            color: {fg};
            border: 1px solid {fg};
            border-radius: {RADIUS_SM}px;
            padding: 8px 14px;
            font-weight: 600;
        }}
    """


def button_qss():
    return f"""
        QPushButton {{
            background: {SURFACE_RAISED};
            color: {ACCENT};
            border: 1px solid {BORDER};
            border-radius: {RADIUS_SM}px;
            padding: 7px;
            font-size: 12px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {BORDER};
        }}
        QPushButton:pressed {{
            background: {ACCENT_DIM};
        }}
    """


def to_bgr(hex_color):
    """Convert a '#RRGGBB' token to an (B, G, R) tuple for cv2 drawing,
    so the video overlay can use the exact same palette as the Qt chrome."""
    c = QColor(hex_color)
    return (c.blue(), c.green(), c.red())