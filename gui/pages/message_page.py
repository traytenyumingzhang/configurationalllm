#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Message Page
Configure user message for LLM interactions
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QGroupBox, QPushButton, QMessageBox,
    QFrame
)
from PySide6.QtCore import Qt, Signal

class MessagePage(QWidget):
    """Message configuration page"""
    
    # Signal emitted when message is updated
    message_updated = Signal()
    
    def __init__(self, config_manager):
        """Initialize message page"""
        super().__init__()
        
        self.config_manager = config_manager
        self.message_config = config_manager.get_message()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Page title
        title_label = QLabel("Message Configuration")
        title_font = title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Configure the message that will be sent to the LLM with each file. "
            "This message instructs the LLM on what to do with the file content."
        )
        desc_label.setWordWrap(True)
        self.layout.addWidget(desc_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)
        
        # User Message group
        self.message_group = QGroupBox("User Message")
        message_layout = QVBoxLayout(self.message_group)
        
        # Message editing field
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Enter the message to send to the LLM...")
        self.message_edit.setText(self.message_config.get("user_message", ""))
        
        message_layout.addWidget(self.message_edit)
        
        self.layout.addWidget(self.message_group, 1)  # 1 = stretch factor
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Save button
        self.save_btn = QPushButton("Save Message")
        self.save_btn.setMinimumHeight(40)
        button_layout.addWidget(self.save_btn)
        
        # Reset button
        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.setMinimumHeight(40)
        button_layout.addWidget(self.reset_btn)
        
        self.layout.addLayout(button_layout)
        
        # Default message for reset
        self.default_message = "Analyze the following literature and provide insights."
        
        # Connect signals
        self.save_btn.clicked.connect(self._save_message)
        self.reset_btn.clicked.connect(self._reset_message)
        
        # Add usage tips
        self._add_usage_tips()
    
    def _add_usage_tips(self):
        """Add usage tips section"""
        tips_group = QGroupBox("Usage Tips")
        tips_layout = QVBoxLayout(tips_group)
        
        tips_text = (
            "<b>Tips for effective messages:</b><br><br>"
            "• Be specific about what you want the LLM to analyze or extract<br>"
            "• Consider asking for structured outputs (like tables or lists)<br>"
            "• You can request specific formats like CSV for data extraction<br>"
            "• Include any special instructions about notation or terminology<br>"
            "• The filename will be automatically included with your message"
        )
        
        tips_label = QLabel(tips_text)
        tips_label.setTextFormat(Qt.RichText)
        tips_label.setWordWrap(True)
        tips_layout.addWidget(tips_label)
        
        # Example message
        example_title = QLabel("<b>Example Message:</b>")
        example_title.setTextFormat(Qt.RichText)
        tips_layout.addWidget(example_title)
        
        example_text = (
            "Analyze this scientific paper and extract:\n"
            "1. The key research question\n"
            "2. The methodology used\n"
            "3. The main findings\n"
            "4. Limitations mentioned\n\n"
            "If the paper contains experimental data, summarize it in a CSV table format."
        )
        
        example_edit = QTextEdit()
        example_edit.setPlainText(example_text)
        example_edit.setReadOnly(True)
        example_edit.setMaximumHeight(150)
        tips_layout.addWidget(example_edit)
        
        self.layout.addWidget(tips_group)
    
    def _save_message(self):
        """Save message to configuration"""
        try:
            message_text = self.message_edit.toPlainText().strip()
            
            # Validate
            if not message_text:
                QMessageBox.warning(self, "Empty Message", 
                                   "User message cannot be empty. Please enter a valid message.")
                return
            
            # Create new message dict
            new_message = {
                "user_message": message_text
            }
            
            # Save to config
            success = self.config_manager.set_message(new_message)
            
            if success:
                QMessageBox.information(self, "Message Saved", 
                                       "User message has been saved successfully.")
                self.message_updated.emit()
            else:
                QMessageBox.critical(self, "Error", 
                                    "Failed to save message. Please try again.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def _reset_message(self):
        """Reset message to default"""
        result = QMessageBox.question(self, "Reset Message", 
                                     "Are you sure you want to reset to the default message?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if result == QMessageBox.Yes:
            self.message_edit.setText(self.default_message)
            
            # Save the default
            new_message = {
                "user_message": self.default_message
            }
            
            success = self.config_manager.set_message(new_message)
            
            if success:
                QMessageBox.information(self, "Message Reset", 
                                      "User message has been reset to default.")
                self.message_updated.emit()
            else:
                QMessageBox.critical(self, "Error", 
                                   "Failed to reset message. Please try again.")
