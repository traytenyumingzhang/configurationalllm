#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Settings Page
Configure API settings for LLM interaction
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QSlider, QGroupBox,
    QPushButton, QFormLayout, QMessageBox, QFrame,
    QCheckBox
)
from PySide6.QtCore import Qt, Signal

class APISettingsPage(QWidget):
    """API Settings configuration page"""
    
    # Signal emitted when settings are updated
    settings_updated = Signal()
    
    def __init__(self, config_manager, main_window=None): # Added main_window parameter
        """Initialize API settings page"""
        super().__init__()
        
        self.config_manager = config_manager
        self.main_window = main_window # Store main_window reference if needed later
        self.api_settings = config_manager.get_api_settings()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Page title
        title_label = QLabel("API Settings")
        title_font = title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Configure your API settings for interacting with Large Language Models. "
            "You'll need an API key from Anthropic (Claude), OpenAI, Google (Gemini), or an OpenAI-compatible service."
        )
        desc_label.setWordWrap(True)
        self.layout.addWidget(desc_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)
        
        # Settings form
        form_group = QGroupBox("API Configuration")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # API Type selection
        self.api_type_combo = QComboBox()
        self.api_type_combo.addItem("Claude (Anthropic)", "claude")
        self.api_type_combo.addItem("OpenAI (GPT)", "openai")
        self.api_type_combo.addItem("Gemini (Google)", "gemini") # Added Gemini
        self.api_type_combo.addItem("OpenAI-compatible (DeepSeek, etc.)", "openai_compatible")
        
        current_api = self.api_settings.get("type", "claude")
        if current_api == "claude":
            self.api_type_combo.setCurrentIndex(0)
        elif current_api == "openai":
            self.api_type_combo.setCurrentIndex(1)
        elif current_api == "gemini": # Handle Gemini index
            self.api_type_combo.setCurrentIndex(2)
        else: # openai_compatible
            self.api_type_combo.setCurrentIndex(3)
        
        form_layout.addRow("API Type:", self.api_type_combo)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.api_settings.get("api_key", ""))
        self.api_key_input.setPlaceholderText("Enter your API key")
        form_layout.addRow("API Key:", self.api_key_input)
        
        # API Base URL (for ALL API types now)
        self.api_base_input = QLineEdit()
        api_base = self.api_settings.get("api_base", "")
        # Set default based on current API type if not defined
        if not api_base:
            if current_api == "claude":
                api_base = "https://api.anthropic.com"
            elif current_api == "openai":
                api_base = "https://api.openai.com/v1"
            elif current_api == "gemini": # Default for Gemini
                api_base = "https://generativelanguage.googleapis.com/v1beta"
            elif current_api == "openai_compatible":
                api_base = "https://api.deepseek.com/v1"
            
        self.api_base_input.setText(api_base)
        self.api_base_input.setPlaceholderText("Enter API base URL (optional for standard endpoints)")
        self.api_base_label = QLabel("API Base URL:")
        form_layout.addRow(self.api_base_label, self.api_base_input)
        
        # Model selection
        model_layout = QVBoxLayout()
        
        # Model dropdown with predefined options
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        model_layout.addWidget(self.model_combo)
        
        # Custom model name input (for all API types)
        model_input_layout = QHBoxLayout()
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Enter exact model ID (e.g., gemini-1.5-pro-latest)")
        self.use_custom_model_checkbox = QCheckBox("Edit model ID")
        
        # Connect checkbox to enable/disable the input field
        self.use_custom_model_checkbox.stateChanged.connect(self._toggle_model_input)
        
        model_input_layout.addWidget(self.model_input)
        model_input_layout.addWidget(self.use_custom_model_checkbox)
        model_layout.addLayout(model_input_layout)
        
        form_layout.addRow("Model:", model_layout)
        
        # Update models based on current API selection
        self._update_model_options()
        
        # Temperature slider
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(0)
        self.temp_slider.setMaximum(100) # Gemini temp range is 0.0-1.0
        self.temp_slider.setValue(int(float(self.api_settings.get("temperature", 0.7)) * 100))
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temp_slider)
        
        self.temp_label = QLabel(f"{self.temp_slider.value() / 100:.2f}")
        temp_layout.addWidget(self.temp_label)
        
        form_layout.addRow("Temperature:", temp_layout)
        
        # Enable reasoning checkbox
        self.enable_reasoning_checkbox = QCheckBox("Enable step-by-step reasoning")
        reasoning_enabled = self.api_settings.get("reasoning_enabled", True)
        self.enable_reasoning_checkbox.setChecked(reasoning_enabled)
        form_layout.addRow("", self.enable_reasoning_checkbox)
        
        # Reasoning level
        reasoning_level_layout = QHBoxLayout()
        self.reasoning_combo = QComboBox()
        self.reasoning_combo.addItem("Low", "low")
        self.reasoning_combo.addItem("Medium", "medium")
        self.reasoning_combo.addItem("High", "high")
        
        current_reasoning = self.api_settings.get("reasoning_level", "medium")
        if current_reasoning == "low":
            self.reasoning_combo.setCurrentIndex(0)
        elif current_reasoning == "medium":
            self.reasoning_combo.setCurrentIndex(1)
        else:
            self.reasoning_combo.setCurrentIndex(2)
        
        reasoning_level_layout.addWidget(self.reasoning_combo)
        
        self.reasoning_label = QLabel("Reasoning Level:")
        
        # Set the initial state
        self.reasoning_combo.setEnabled(reasoning_enabled)
        
        form_layout.addRow(self.reasoning_label, reasoning_level_layout)
        
        reasoning_desc = QLabel(
            "Reasoning enables step-by-step thinking:\n"
            "• Low: Basic step-by-step thinking\n"
            "• Medium: Detailed reasoning with explanations\n"
            "• High: Comprehensive reasoning with evidence evaluation\n"
            "Disable reasoning for more direct responses without explicit thought process."
        )
        reasoning_desc.setWordWrap(True)
        form_layout.addRow("", reasoning_desc)
        
        self.layout.addWidget(form_group)
        
        # Save button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setMinimumHeight(40)
        self.layout.addWidget(self.save_btn)
        
        # Add stretch to push content to the top
        self.layout.addStretch()
        
        # Connect signals
        self.api_type_combo.currentIndexChanged.connect(self._update_model_options)
        self.api_type_combo.currentIndexChanged.connect(self._update_api_base_visibility)
        self.model_combo.currentIndexChanged.connect(self._update_model_input)
        self.temp_slider.valueChanged.connect(self._update_temp_label)
        self.enable_reasoning_checkbox.stateChanged.connect(self._toggle_reasoning)
        self.save_btn.clicked.connect(self._save_settings)
        
        # Initial UI updates
        self._update_api_base_visibility()
        self._update_model_input()
        self._toggle_reasoning(self.enable_reasoning_checkbox.isChecked())
        
        # Set initial model input state
        current_model = self.api_settings.get("model", "")
        use_custom = self.api_settings.get("use_custom_model", False)
        
        # If there's a saved model and it's not in our predefined lists,
        # assume it's custom and populate the model input
        if current_model:
            self.model_input.setText(current_model)
            
            # Check if we should use custom model input
            if use_custom:
                self.use_custom_model_checkbox.setChecked(True)
                self._toggle_model_input(True)
    
    def _toggle_model_input(self, enabled):
        """Enable or disable model ID input field"""
        is_enabled = bool(enabled)
        self.model_input.setEnabled(is_enabled)
        self.model_combo.setEnabled(not is_enabled)
        
        # Update the input field text if checkbox is checked
        if is_enabled:
            # Use the selected model ID if the input is empty
            if not self.model_input.text() and self.model_combo.currentData():
                self.model_input.setText(self.model_combo.currentData())
    
    def _toggle_reasoning(self, enabled):
        """Enable or disable reasoning controls based on checkbox"""
        is_enabled = bool(enabled)
        self.reasoning_combo.setEnabled(is_enabled)
        self.reasoning_label.setEnabled(is_enabled)
    
    def _update_api_base_visibility(self):
        """Show or hide API base URL field based on API type and set defaults"""
        # Always show base URL for all API types
        self.api_base_label.setVisible(True)
        self.api_base_input.setVisible(True)
        
        # Set appropriate default URL based on API type
        api_type = self.api_type_combo.currentData()
        
        # Only set default if the field is empty or matches a known default
        current_url = self.api_base_input.text()
        default_urls = {
            "claude": "https://api.anthropic.com",
            "openai": "https://api.openai.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta", # Gemini default
            "openai_compatible": "https://api.deepseek.com/v1"
        }
        
        # If empty or matches one of the defaults, update it
        if not current_url or current_url in default_urls.values():
            self.api_base_input.setText(default_urls.get(api_type, ""))
    
    def _update_model_input(self):
        """Update model input text based on selection"""
        # Only update if the custom model checkbox is unchecked
        if not self.use_custom_model_checkbox.isChecked():
            api_type = self.api_type_combo.currentData()
            model_data = self.model_combo.currentData()
            if model_data:
                self.model_input.setText(model_data)
    
    def _update_model_options(self):
        """Update model options based on selected API type"""
        # Save current selection if any
        current_model = self.model_combo.currentData()
        
        # Clear the model combo
        self.model_combo.clear()
        self.model_combo.blockSignals(True)  # Prevent triggering visibility updates
        
        api_type = self.api_type_combo.currentData()
        
        if api_type == "claude":
            # Make sure we're using the correct model ID format
            self.model_combo.addItem("Claude 3.7 Sonnet (Latest)", "claude-3-7-sonnet-20250219")
            self.model_combo.addItem("Claude 3 Opus", "claude-3-opus-20240229")
            self.model_combo.addItem("Claude 3 Sonnet", "claude-3-sonnet-20240229")
            self.model_combo.addItem("Claude 3 Haiku", "claude-3-haiku-20240307")
            self.model_combo.addItem("Claude 2.1", "claude-2.1")
            self.model_combo.addItem("Claude 2.0", "claude-2.0")
        elif api_type == "openai":
            self.model_combo.addItem("GPT-4 Turbo", "gpt-4-turbo-preview")
            self.model_combo.addItem("GPT-4", "gpt-4")
            self.model_combo.addItem("GPT-3.5 Turbo", "gpt-3.5-turbo")
        elif api_type == "gemini": # Add Gemini models
            self.model_combo.addItem("Gemini 1.5 Pro (Latest)", "gemini-1.5-pro-latest")
            self.model_combo.addItem("Gemini 1.5 Flash (Latest)", "gemini-1.5-flash-latest")
            self.model_combo.addItem("Gemini 1.0 Pro", "gemini-1.0-pro") # Older model
        else:  # OpenAI-compatible
            self.model_combo.addItem("DeepSeek Coder", "deepseek-coder")
            self.model_combo.addItem("DeepSeek R1", "deepseek-r1")
            self.model_combo.addItem("DeepSeek LLM", "deepseek-llm")
        
        self.model_combo.blockSignals(False)
        
        # Try to restore previous selection
        found = False
        if current_model:
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i) == current_model:
                    self.model_combo.setCurrentIndex(i)
                    found = True
                    break
        
        # Update model input field with the current selection
        self._update_model_input()
    
    def _update_temp_label(self, value):
        """Update temperature label when slider changes"""
        self.temp_label.setText(f"{value / 100:.2f}")
    
    def _save_settings(self):
        """Save API settings"""
        try:
            new_settings = {
                "type": self.api_type_combo.currentData(),
                "api_key": self.api_key_input.text(),
                "temperature": self.temp_slider.value() / 100,
                "reasoning_enabled": self.enable_reasoning_checkbox.isChecked(),
                "reasoning_level": self.reasoning_combo.currentData(),
                "use_custom_model": self.use_custom_model_checkbox.isChecked()
            }
            
            # Always save the API base URL for all API types
            api_base = self.api_base_input.text().strip()
            # Only save if non-empty, otherwise let the processor use defaults
            if api_base:
                new_settings["api_base"] = api_base
            
            # Get model based on mode
            if self.use_custom_model_checkbox.isChecked():
                # Use custom model input
                custom_model = self.model_input.text().strip()
                if custom_model:
                    new_settings["model"] = custom_model
                else:
                    QMessageBox.warning(self, "Missing Model ID", 
                                       "Please enter a custom model ID.")
                    return
            else:
                # Use selected model from dropdown
                model_data = self.model_combo.currentData()
                if model_data:
                    new_settings["model"] = model_data
                else:
                    QMessageBox.warning(self, "Missing Model", 
                                       "Please select a model.")
                    return
            
            # Validate settings
            if not new_settings["api_key"]:
                QMessageBox.warning(self, "Missing API Key", 
                                   "Please enter your API key before saving.")
                return
            
            # API Base URL is now optional for standard endpoints, no need to validate presence
            
            # Save settings
            success = self.config_manager.set_api_settings(new_settings)
            
            if success:
                QMessageBox.information(self, "Settings Saved", 
                                       "API settings have been saved successfully.")
                self.settings_updated.emit()
            else:
                QMessageBox.critical(self, "Error", 
                                    "Failed to save settings. Please try again.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def enter_page(self):
        """Called when page is navigated to."""
        # Reload settings from config manager when page is entered
        self.api_settings = self.config_manager.get_api_settings()
        
        # Update UI elements with loaded settings
        current_api = self.api_settings.get("type", "claude")
        api_type_map = {"claude": 0, "openai": 1, "gemini": 2, "openai_compatible": 3}
        self.api_type_combo.setCurrentIndex(api_type_map.get(current_api, 0))
        
        self.api_key_input.setText(self.api_settings.get("api_key", ""))
        
        api_base = self.api_settings.get("api_base", "")
        if not api_base: # Set default if empty, based on current_api
            default_bases = {"claude": "https://api.anthropic.com", "openai": "https://api.openai.com/v1", "gemini": "https://generativelanguage.googleapis.com/v1beta", "openai_compatible": "https://api.deepseek.com/v1"}
            api_base = default_bases.get(current_api, "")
        self.api_base_input.setText(api_base)

        self._update_model_options() # This will also try to set the current model

        # Set model from settings after options are populated
        saved_model = self.api_settings.get("model", "")
        if saved_model:
            # Try to find in combo
            idx = self.model_combo.findData(saved_model)
            if idx != -1:
                self.model_combo.setCurrentIndex(idx)
            # Always set the text input for custom model scenario
            self.model_input.setText(saved_model)

        self.use_custom_model_checkbox.setChecked(self.api_settings.get("use_custom_model", False))
        self._toggle_model_input(self.use_custom_model_checkbox.isChecked()) # Ensure correct state

        self.temp_slider.setValue(int(float(self.api_settings.get("temperature", 0.7)) * 100))
        self._update_temp_label(self.temp_slider.value()) # Update label too

        reasoning_enabled = self.api_settings.get("reasoning_enabled", True)
        self.enable_reasoning_checkbox.setChecked(reasoning_enabled)
        self._toggle_reasoning(reasoning_enabled) # Update dependent controls

        current_reasoning = self.api_settings.get("reasoning_level", "medium")
        reasoning_map = {"low":0, "medium":1, "high":2}
        self.reasoning_combo.setCurrentIndex(reasoning_map.get(current_reasoning,1))

    def leave_page(self):
        """Called when page is navigated away from."""
        pass # No specific action needed on leave, settings are saved via button
