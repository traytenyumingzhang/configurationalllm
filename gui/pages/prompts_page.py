#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prompts Page
Configure system prompts for LLM interactions
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QGroupBox, QPushButton, QMessageBox,
    QDialog, QDialogButtonBox, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette

class BetaWarningDialog(QDialog):
    """Beta feature warning dialog"""
    
    def __init__(self, parent=None):
        """Initialize beta warning dialog"""
        super().__init__(parent)
        
        self.setWindowTitle("Beta Feature Warning")
        self.setMinimumWidth(500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Warning icon and title
        title_layout = QHBoxLayout()
        
        warning_label = QLabel("⚠️")
        warning_font = warning_label.font()
        warning_font.setPointSize(24)
        warning_label.setFont(warning_font)
        
        title_layout.addWidget(warning_label)
        
        title = QLabel("Beta Feature")
        title_font = title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Warning message
        message = QLabel(
            "Custom prompt editing is a beta feature and may affect the performance and "
            "reliability of the LLM. Incorrect prompts may lead to unexpected results or "
            "errors in processing.\n\n"
            "If you proceed, you accept responsibility for any issues that may arise from "
            "using custom prompts."
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Create buttons manually
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("I Understand, Proceed")
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        
        layout.addLayout(buttons_layout)


class PromptsPage(QWidget):
    """Prompts configuration page"""
    
    # Signal emitted when prompts are updated
    prompts_updated = Signal()
    
    def __init__(self, config_manager):
        """Initialize prompts page"""
        super().__init__()
        
        self.config_manager = config_manager
        self.prompts = config_manager.get_prompts()
        self.user_accepted_beta = False
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Page title
        title_label = QLabel("Prompts Configuration")
        title_font = title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.layout.addWidget(title_label)
        
        # Beta warning label
        self.warning_label = QLabel("⚠️ This is a beta feature. Click Edit to proceed.")
        warning_font = self.warning_label.font()
        warning_font.setBold(True)
        self.warning_label.setFont(warning_font)
        
        # Set warning text color to orange
        palette = self.warning_label.palette()
        palette.setColor(QPalette.WindowText, QColor(255, 140, 0))
        self.warning_label.setPalette(palette)
        
        self.layout.addWidget(self.warning_label)
        
        # Description
        desc_label = QLabel(
            "System prompts are instructions given to the LLM that guide its behavior and responses. "
            "These prompts are combined with reasoning instructions based on your reasoning level setting."
        )
        desc_label.setWordWrap(True)
        self.layout.addWidget(desc_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)
        
        # System Prompt group
        self.prompt_group = QGroupBox("System Prompt")
        prompt_layout = QVBoxLayout(self.prompt_group)
        
        # Prompt editing field (read-only initially)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter system prompt instructions...")
        self.prompt_edit.setText(self.prompts.get("system_prompt", ""))
        self.prompt_edit.setReadOnly(True)
        
        prompt_layout.addWidget(self.prompt_edit)
        
        self.layout.addWidget(self.prompt_group, 1)  # 1 = stretch factor
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Edit button
        self.edit_btn = QPushButton("Edit Prompt")
        self.edit_btn.setMinimumHeight(40)
        button_layout.addWidget(self.edit_btn)
        
        # Save button (disabled initially)
        self.save_btn = QPushButton("Save Prompt")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        # Reset button
        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.setMinimumHeight(40)
        button_layout.addWidget(self.reset_btn)
        
        self.layout.addLayout(button_layout)
        
        # Default prompt for reset
        self.default_prompt = """You are a helpful assistant analyzing scientific literature. Your response should contain exactly two lines within a csv code block:
First line: list the variable name
Second line: list the output

The format of the code block:
```csv
```
"""
        
        # Connect signals
        self.edit_btn.clicked.connect(self._show_beta_warning)
        self.save_btn.clicked.connect(self._save_prompts)
        self.reset_btn.clicked.connect(self._reset_prompts)
    
    def _show_beta_warning(self):
        """Show beta warning dialog"""
        if self.user_accepted_beta:
            self._enable_editing()
            return
        
        dialog = BetaWarningDialog(self)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            self.user_accepted_beta = True
            self._enable_editing()
    
    def _enable_editing(self):
        """Enable prompt editing"""
        self.prompt_edit.setReadOnly(False)
        self.save_btn.setEnabled(True)
        
        # Change background color to indicate editing mode
        palette = self.prompt_edit.palette()
        palette.setColor(QPalette.Base, QColor(255, 255, 240))  # Light yellow background
        self.prompt_edit.setPalette(palette)
        
        # Change warning label
        self.warning_label.setText("⚠️ Editing mode enabled. Be careful with your changes.")
    
    def _save_prompts(self):
        """Save prompts to configuration"""
        try:
            prompt_text = self.prompt_edit.toPlainText().strip()
            
            # Validate
            if not prompt_text:
                QMessageBox.warning(self, "Empty Prompt", 
                                   "System prompt cannot be empty. Please enter a valid prompt.")
                return
            
            # Create new prompts dict
            new_prompts = {
                "system_prompt": prompt_text
            }
            
            # Save to config
            success = self.config_manager.set_prompts(new_prompts)
            
            if success:
                # Reset UI state
                self.prompt_edit.setReadOnly(True)
                self.save_btn.setEnabled(False)
                
                # Reset palette
                self.prompt_edit.setPalette(QPalette())
                
                # Reset warning label
                self.warning_label.setText("⚠️ This is a beta feature. Click Edit to proceed.")
                
                QMessageBox.information(self, "Prompts Saved", 
                                       "System prompt has been saved successfully.")
                
                self.prompts_updated.emit()
            else:
                QMessageBox.critical(self, "Error", 
                                    "Failed to save prompts. Please try again.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def _reset_prompts(self):
        """Reset prompts to default"""
        result = QMessageBox.question(self, "Reset Prompts", 
                                     "Are you sure you want to reset to the default prompt?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if result == QMessageBox.Yes:
            self.prompt_edit.setText(self.default_prompt)
            
            # If in editing mode, keep it enabled
            if not self.prompt_edit.isReadOnly():
                return
            
            # Otherwise, save the default
            new_prompts = {
                "system_prompt": self.default_prompt
            }
            
            success = self.config_manager.set_prompts(new_prompts)
            
            if success:
                QMessageBox.information(self, "Prompts Reset", 
                                       "System prompt has been reset to default.")
                self.prompts_updated.emit()
            else:
                QMessageBox.critical(self, "Error", 
                                    "Failed to reset prompts. Please try again.")
