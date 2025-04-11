#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application Styles
Defines the Apple-inspired visual styling for the application
"""

from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt

# Application color palette with purple theme (#8a3681)
COLORS = {
    # Main colors
    "background": "#F5F7FA",  # Lighter background to enhance frosted effect
    "sidebar": "#F0EDF2",     # Light purple-tinged sidebar
    "accent": "#8a3681",      # Main purple accent color
    "accent_darker": "#6A2963",  # Darker purple for pressed states
    "accent_highlight": "#9B4D92",  # Lighter purple for hover states
    "success": "#34C759",     # Apple green
    "warning": "#FF9500",     # Apple orange
    "error": "#FF3B30",       # Apple red
    "text_primary": "#1D1D1F",
    "text_secondary": "#86868B",
    "text_tertiary": "#AEAEB2",
    "border": "#D2D2D7",
    "divider": "#E5E5E5",
    
    # UI Element colors
    "button_background": "#8a3681",  # Purple buttons
    "button_text": "#FFFFFF",
    "input_background": "rgba(255, 255, 255, 0.8)",
    "input_border": "rgba(210, 210, 215, 0.8)",
    "slider_track": "#E5E5E5",
    "slider_handle": "#8a3681",  # Purple slider handle
    
    # Frosted glass effect colors
    "frosted_bg": "rgba(255, 255, 255, 0.7)",
    "frosted_border": "rgba(138, 54, 129, 0.3)",  # Purple-tinted border
    "frosted_card_bg": "rgba(255, 255, 255, 0.5)",
    "frosted_card_border": "rgba(138, 54, 129, 0.2)",  # Purple-tinted card border
}

# Greek letters for icons (with descriptive names)
GREEK_ICONS = {
    "home": "Ω",            # Omega: home/main
    "settings": "Σ",        # Sigma: settings/system
    "prompts": "Π",         # Pi: prompts
    "message": "Μ",         # Mu: message
    "files": "Φ",           # Phi: files
    "output": "Δ",          # Delta: output/data
    "about": "Ψ",           # Psi: about/info
    "save": "Γ",            # Gamma: save
    "upload": "Θ",          # Theta: upload
    "download": "Λ",        # Lambda: download
    "start": "α",           # Alpha: start/activate
    "stop": "β",            # Beta: stop
    "add": "Ξ",             # Xi: add
    "remove": "Ζ",          # Zeta: remove
    "search": "ε",          # Epsilon: search
    "config": "Ρ",          # Rho: configuration
}

def get_application_stylesheet():
    """Returns the main application stylesheet"""
    return f"""
    /* Global */
    QMainWindow, QDialog {{
        background-color: {COLORS["background"]};
    }}
    
    QWidget {{
        font-family: ".AppleSystemUIFont", "Helvetica Neue", "Lucida Grande";
        color: {COLORS["text_primary"]};
    }}
    
    /* Sidebar with frosted glass effect */
    #sidebar {{
        background-color: {COLORS["frosted_bg"]};
        border-right: 1px solid {COLORS["frosted_border"]};
        border-top-left-radius: 10px;
        border-bottom-left-radius: 10px;
        min-width: 250px;
    }}
    
    QListWidget {{
        background-color: transparent;
        border: none;
        font-size: 14px;
        outline: 0;
    }}
    
    QListWidget::item {{
        height: 50px;  /* Significantly increased height to avoid text cutting */
        padding-left: 15px;
        border-radius: 8px;
        margin: 3px 8px;  /* Slightly increased margin for better spacing */
        color: {COLORS["text_primary"]};  /* Explicitly set unselected text to black */
        font-weight: normal;  /* Normal weight for unselected items */
    }}
    
    QListWidget::item:selected {{
        background-color: {COLORS["accent"]};
        color: white;  /* White text when selected */
        font-weight: bold;  /* Bold text when selected */
    }}
    
    QListWidget::item:hover:!selected {{
        background-color: rgba(233, 233, 235, 0.7);
    }}
    
    /* Content Area */
    #content_area {{
        background-color: {COLORS["background"]};
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }}
    
    /* Frosted Glass Panels */
    #frosted_panel, #frosted_content, #frosted_card {{
        border-radius: 15px;
    }}
    
    #frosted_panel {{
        background-color: {COLORS["frosted_bg"]};
        border: 1px solid {COLORS["frosted_border"]};
    }}
    
    #frosted_content {{
        background-color: {COLORS["frosted_bg"]};
        border: 1px solid {COLORS["frosted_border"]};
    }}
    
    #frosted_card {{
        background-color: {COLORS["frosted_card_bg"]};
        border: 1px solid {COLORS["frosted_card_border"]};
        border-radius: 10px;
    }}
    
    /* Specific styling for logo containers */
    #logo_container {{
        background-color: white;
        border-radius: 8px; 
        border: 1px solid {COLORS["border"]};
        padding: 10px;
    }}
    
    /* Forms and Inputs */
    QLineEdit, QTextEdit, QComboBox, QSpinBox {{
        background-color: {COLORS["input_background"]};
        border: 1px solid {COLORS["input_border"]};
        border-radius: 6px;
        padding: 8px 12px;
        selection-background-color: {COLORS["accent"]};
        selection-color: white;
        font-size: 14px;
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 2px solid {COLORS["accent"]};
    }}
    
    QComboBox {{
        min-height: 20px;
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 20px;
        border-left-width: 0px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        width: 10px;
        height: 10px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS["frosted_bg"]};
        border: 1px solid {COLORS["frosted_border"]};
        border-radius: 6px;
        selection-background-color: {COLORS["accent"]};
        selection-color: white;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS["button_background"]};
        color: {COLORS["button_text"]};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 14px;
        min-height: 36px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS["accent_highlight"]};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS["accent_darker"]};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS["text_tertiary"]};
        color: {COLORS["text_secondary"]};
    }}
    
    QPushButton#secondary_button {{
        background-color: {COLORS["frosted_card_bg"]};
        color: {COLORS["accent"]};
        border: 1px solid {COLORS["frosted_border"]};
    }}
    
    QPushButton#secondary_button:hover {{
        background-color: rgba(233, 233, 235, 0.7);
    }}
    
    /* Sliders */
    QSlider::groove:horizontal {{
        height: 4px;
        background: {COLORS["slider_track"]};
        border-radius: 2px;
    }}
    
    QSlider::handle:horizontal {{
        background: {COLORS["slider_handle"]};
        width: 18px;
        height: 18px;
        margin: -7px 0;
        border-radius: 9px;
    }}
    
    QSlider::sub-page:horizontal {{
        background: {COLORS["accent"]};
        border-radius: 2px;
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {COLORS["text_tertiary"]};
        border-radius: 5px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {COLORS["text_secondary"]};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        border: none;
        background: none;
    }}
    
    /* Group Boxes */
    QGroupBox {{
        background-color: {COLORS["frosted_bg"]};
        border: 1px solid {COLORS["frosted_border"]};
        border-radius: 8px;
        margin-top: 12px;
        font-weight: bold;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 10px;
        color: {COLORS["text_primary"]};
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS["text_primary"]};
    }}
    
    QLabel#subtitle {{
        color: {COLORS["text_secondary"]};
        font-size: 13px;
    }}
    
    QLabel#header {{
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    
    /* Separators */
    QFrame[frameShape="4"], QFrame[frameShape="HLine"] {{
        background-color: {COLORS["divider"]};
        border: none;
        max-height: 1px;
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {COLORS["frosted_border"]};
        border-radius: 8px;
        top: -1px;
        background-color: {COLORS["frosted_bg"]};
    }}
    
    QTabBar::tab {{
        padding: 8px 16px;
        background-color: {COLORS["frosted_card_bg"]};
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 2px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS["frosted_bg"]};
        border: 1px solid {COLORS["frosted_border"]};
        border-bottom-color: {COLORS["frosted_bg"]};
    }}
    
    /* Progress Bar */
    QProgressBar {{
        border: none;
        border-radius: 3px;
        background-color: {COLORS["slider_track"]};
        text-align: center;
        color: white;
        height: 6px;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS["accent"]};
        border-radius: 3px;
    }}
"""

def apply_dark_mode_palette(app):
    """
    Apply a dark mode color palette to the application
    (This is just prepared but not used by default)
    """
    dark_palette = QPalette()
    
    # Dark mode colors
    dark_color = QColor(30, 30, 30)
    dark_gray = QColor(53, 53, 53)
    light_gray = QColor(100, 100, 100)
    text_color = QColor(255, 255, 255)
    accent_color = QColor(138, 54, 129)  # Purple accent
    
    # Set color roles
    dark_palette.setColor(QPalette.Window, dark_color)
    dark_palette.setColor(QPalette.WindowText, text_color)
    dark_palette.setColor(QPalette.Base, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.AlternateBase, dark_color)
    dark_palette.setColor(QPalette.ToolTipBase, accent_color)
    dark_palette.setColor(QPalette.ToolTipText, text_color)
    dark_palette.setColor(QPalette.Text, text_color)
    dark_palette.setColor(QPalette.Button, dark_gray)
    dark_palette.setColor(QPalette.ButtonText, text_color)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, accent_color)
    dark_palette.setColor(QPalette.Highlight, accent_color)
    dark_palette.setColor(QPalette.HighlightedText, text_color)
    
    # Set disabled colors
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, light_gray)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, light_gray)
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, light_gray)
    
    # Apply the palette
    app.setPalette(dark_palette)
