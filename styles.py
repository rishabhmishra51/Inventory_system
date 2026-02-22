"""
styles.py - Centralized stylesheet and color constants for the application.
"""

# Color palette
PRIMARY = "#1a73e8"
PRIMARY_DARK = "#1557b0"
SUCCESS = "#0f9d58"
WARNING = "#f4b400"
DANGER = "#db4437"
LIGHT_BG = "#f8f9fa"
WHITE = "#ffffff"
DARK_TEXT = "#202124"
SECONDARY_TEXT = "#5f6368"
BORDER = "#dadce0"

GLOBAL_STYLE = """
QMainWindow {
    background-color: #f8f9fa;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #202124;
}

/* ---- Side Navigation ---- */
#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #dadce0;
}
#sidebar QPushButton {
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 0px;
    font-size: 13px;
    color: #5f6368;
    background: transparent;
}
#sidebar QPushButton:hover {
    background-color: #e8f0fe;
    color: #1a73e8;
}
#sidebar QPushButton:checked, #sidebar QPushButton[active="true"] {
    background-color: #e8f0fe;
    color: #1a73e8;
    font-weight: bold;
    border-left: 3px solid #1a73e8;
}
#appTitle {
    font-size: 18px;
    font-weight: bold;
    color: #1a73e8;
    padding: 20px 20px 10px 20px;
}

/* ---- Cards / Panels ---- */
.card {
    background-color: #ffffff;
    border: 1px solid #dadce0;
    border-radius: 8px;
    padding: 16px;
}

/* ---- Tables ---- */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dadce0;
    border-radius: 4px;
    gridline-color: #eeeeee;
    selection-background-color: #e8f0fe;
    selection-color: #202124;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #f1f3f4;
    color: #202124;
    font-weight: 600;
    padding: 8px 6px;
    border: none;
    border-bottom: 2px solid #dadce0;
}

/* ---- Buttons ---- */
QPushButton {
    padding: 8px 20px;
    border-radius: 4px;
    font-weight: 500;
}
QPushButton#primaryBtn {
    background-color: #1a73e8;
    color: white;
    border: none;
}
QPushButton#primaryBtn:hover {
    background-color: #1557b0;
}
QPushButton#successBtn {
    background-color: #0f9d58;
    color: white;
    border: none;
}
QPushButton#successBtn:hover {
    background-color: #0b8043;
}
QPushButton#dangerBtn {
    background-color: #db4437;
    color: white;
    border: none;
}
QPushButton#dangerBtn:hover {
    background-color: #c5221f;
}
QPushButton#outlineBtn {
    background-color: transparent;
    color: #1a73e8;
    border: 1px solid #1a73e8;
}
QPushButton#outlineBtn:hover {
    background-color: #e8f0fe;
}

/* ---- Inputs ---- */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    padding: 8px 12px;
    border: 1px solid #dadce0;
    border-radius: 4px;
    background-color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #1a73e8;
}

/* ---- Tab Widget ---- */
QTabWidget::pane {
    border: 1px solid #dadce0;
    border-radius: 4px;
    background: #ffffff;
}
QTabBar::tab {
    padding: 10px 24px;
    border: none;
    color: #5f6368;
}
QTabBar::tab:selected {
    color: #1a73e8;
    font-weight: bold;
    border-bottom: 2px solid #1a73e8;
}
QTabBar::tab:hover {
    color: #1a73e8;
    background-color: #e8f0fe;
}

/* ---- Labels ---- */
QLabel#sectionTitle {
    font-size: 20px;
    font-weight: bold;
    color: #202124;
}
QLabel#statValue {
    font-size: 28px;
    font-weight: bold;
    color: #1a73e8;
}
QLabel#statLabel {
    font-size: 12px;
    color: #5f6368;
}
QLabel#warningLabel {
    color: #db4437;
    font-weight: bold;
}

/* ---- ScrollBar ---- */
QScrollBar:vertical {
    width: 8px;
    background: transparent;
}
QScrollBar::handle:vertical {
    background-color: #bdc1c6;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background-color: #9aa0a6;
}

/* ---- Group Box ---- */
QGroupBox {
    font-weight: bold;
    border: 1px solid #dadce0;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
"""
