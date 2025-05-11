#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processing Settings Page
Handles UI and logic for configuring processing parameters.
"""

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Signal

from .processing_settings_page_ui import setup_processing_settings_ui

class ProcessingSettingsPage(QWidget):
    """
    Manages the UI and logic for the Processing Settings page.
    Allows users to configure iterations and delay for file processing.
    """
    settings_updated = Signal() # Emitted when settings are saved

    def __init__(self, config_manager, main_window=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.main_window = main_window # For potential future use (e.g., status bar messages)

        # Load initial values from config_manager or use defaults
        self.num_iterations = self.config_manager.get_setting('num_iterations', 1)
        self.rate_limit_delay = self.config_manager.get_setting('rate_limit_delay', 5) # Default 5 seconds

        # Setup UI using the imported function
        # This will create UI elements as attributes of `self`
        setup_processing_settings_ui(self) 
        
        # Connect signals from UI elements to handler methods
        self._connect_signals()

    def _connect_signals(self):
        """Connects all UI element signals to their respective slots."""
        # Iteration controls
        self.iterations_spinner.valueChanged.connect(self._sync_iterations_from_spinner)
        self.iterations_slider.valueChanged.connect(self._sync_iterations_from_slider)
        
        # Delay controls
        self.delay_spinner.valueChanged.connect(self._sync_delay_from_spinner)
        self.delay_slider.valueChanged.connect(self._sync_delay_from_slider)
        
        # Save button
        self.save_settings_btn.clicked.connect(self.save_settings_action)

    def _sync_iterations_from_spinner(self, value):
        """Updates the iteration slider when the spinner changes."""
        self.num_iterations = value
        self.iterations_slider.setValue(value)
        # Settings are saved explicitly via the save button

    def _sync_iterations_from_slider(self, value):
        """Updates the iteration spinner when the slider changes."""
        self.num_iterations = value
        self.iterations_spinner.setValue(value)
        # Settings are saved explicitly via the save button

    def _sync_delay_from_spinner(self, value):
        """Updates the delay slider when the spinner changes."""
        self.rate_limit_delay = value
        self.delay_slider.setValue(value)
        # Settings are saved explicitly via the save button

    def _sync_delay_from_slider(self, value):
        """Updates the delay spinner when the slider changes."""
        self.rate_limit_delay = value
        self.delay_spinner.setValue(value)
        # Settings are saved explicitly via the save button

    def save_settings_action(self):
        """Saves the current iteration and delay settings to the config file."""
        self.config_manager.save_setting('num_iterations', self.num_iterations)
        self.config_manager.save_setting('rate_limit_delay', self.rate_limit_delay)
        
        QMessageBox.information(self, "Settings Saved", 
                                "Processing settings have been saved successfully.")
        self.settings_updated.emit()

    def load_settings(self):
        """Loads settings from config_manager and updates UI elements."""
        self.num_iterations = self.config_manager.get_setting('num_iterations', 1)
        self.rate_limit_delay = self.config_manager.get_setting('rate_limit_delay', 5)
        
        self.iterations_spinner.setValue(self.num_iterations)
        self.iterations_slider.setValue(self.num_iterations) # Slider will sync via spinner's signal
        self.delay_spinner.setValue(self.rate_limit_delay)
        self.delay_slider.setValue(self.rate_limit_delay) # Slider will sync via spinner's signal

    def enter_page(self):
        """Called when the page is navigated to. Ensures settings are fresh."""
        self.load_settings()

    def leave_page(self):
        """Called when the page is navigated away from."""
        # Optionally, prompt to save if changes are unsaved, or auto-save.
        # For now, saving is explicit via the button.
        pass
