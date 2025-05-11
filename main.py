#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configurational LLM
Main application entry point
Author: Trayten Yuming Zhang
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale

from gui.main_window import MainWindow
from utils.config_manager import ConfigManager
from gui.styles import get_application_stylesheet, apply_dark_mode_palette

def main():
    # Initialize application
    app = QApplication(sys.argv)
    
    # Apply application stylesheet
    app.setStyleSheet(get_application_stylesheet())
    
    # Setup font
    app.setFont(app.font())
    
    # Setup translation
    translator = QTranslator()
    config = ConfigManager()
    locale = config.get_language() or QLocale.system().name()
    translator.load(f"resources/translations/{locale}")
    app.installTranslator(translator)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
