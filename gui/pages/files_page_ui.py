#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Files Page UI Components
Contains UI setup for the Files Page, focusing on file management.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.styles import GREEK_ICONS # Assuming GREEK_ICONS are used for buttons

def setup_ui(self):
    """Set up the user interface for the Files Page"""
    # Main layout
    self.layout = QVBoxLayout(self)
    self.layout.setContentsMargins(40, 40, 40, 40)
    self.layout.setSpacing(25)
    
    # Page title
    title_label = QLabel("Files Library")
    title_font = QFont()
    title_font.setPointSize(22)
    title_font.setBold(True)
    title_label.setFont(title_font)
    self.layout.addWidget(title_label)
    
    # Description with frosted glass panel
    desc_frame = QFrame()
    desc_frame.setObjectName("frosted_panel")
    desc_layout = QVBoxLayout(desc_frame)
    desc_layout.setContentsMargins(20, 20, 20, 20)
    
    desc_label = QLabel(
        "Manage files to be processed by the LLM. Add research papers, articles, or other "
        "documents you want to analyze. Configure processing settings on the 'Processing Settings' page."
    )
    desc_label.setWordWrap(True)
    desc_label.setStyleSheet("font-size: 14px; line-height: 150%;")
    desc_layout.addWidget(desc_label)
    
    self.layout.addWidget(desc_frame)
    
    # Files list group with frosted glass styling
    self.files_group = QFrame()
    self.files_group.setObjectName("frosted_content")
    files_layout = QVBoxLayout(self.files_group)
    files_layout.setContentsMargins(25, 25, 25, 25)
    files_layout.setSpacing(20)
    
    # Available Files heading
    available_heading = QLabel("Available Files")
    available_font = QFont()
    available_font.setPointSize(16)
    available_font.setBold(True)
    available_heading.setFont(available_font)
    files_layout.addWidget(available_heading)
    
    # Files list widget with frosted styling
    files_list_frame = QFrame()
    files_list_frame.setObjectName("frosted_card")
    files_list_frame.setStyleSheet("#frosted_card { border-radius: 10px; min-height: 300px; }") # Adjusted min-height
    files_list_layout = QVBoxLayout(files_list_frame)
    files_list_layout.setContentsMargins(1, 1, 1, 1)
    
    self.files_list = QListWidget()
    self.files_list.setStyleSheet("""
        QListWidget {
            background-color: rgba(255, 255, 255, 0.6); border: none;
            border-radius: 10px; padding: 10px; font-size: 14px;
        }
        QListWidget::item {
            border-radius: 5px; padding: 12px; margin: 5px 0px; min-height: 40px;
            color: #000000; background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(200, 200, 200, 0.7);
        }
        QListWidget::item:selected {
            background-color: rgba(0, 113, 227, 0.8); color: white;
            border: 1px solid rgba(0, 113, 227, 1.0);
        }
        QListWidget::item:hover:!selected {
            background-color: rgba(240, 240, 240, 0.9);
            border: 1px solid rgba(180, 180, 180, 0.7);
        }
        QScrollBar:vertical {
            border: none; background: rgba(240, 240, 240, 0.8);
            width: 16px; margin: 0px; border-radius: 8px;
        }
        QScrollBar::handle:vertical {
            background: rgba(160, 160, 160, 0.8); min-height: 40px; border-radius: 8px;
        }
        QScrollBar::handle:vertical:hover { background: rgba(120, 120, 120, 0.9); }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
    """)
    self.files_list.setMinimumHeight(400) # Increased min height as it's the main content now
    self.files_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
    self.files_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.files_list.setWordWrap(True)
    self.files_list.setAlternatingRowColors(True)
    files_list_layout.addWidget(self.files_list)
    
    files_layout.addWidget(files_list_frame)
    
    # File management buttons with frosted card style
    file_buttons_layout = QHBoxLayout()
    file_buttons_layout.setSpacing(15)
    
    self.add_file_btn = QPushButton(f"{GREEK_ICONS.get('upload', '⬆️')} Add Files")
    self.add_file_btn.setMinimumHeight(45)
    self.add_file_btn.setObjectName("secondary_button")
    file_buttons_layout.addWidget(self.add_file_btn)
    
    self.remove_file_btn = QPushButton(f"{GREEK_ICONS.get('remove', '🗑️')} Remove Selected")
    self.remove_file_btn.setMinimumHeight(45)
    self.remove_file_btn.setObjectName("secondary_button")
    self.remove_file_btn.setEnabled(False)
    file_buttons_layout.addWidget(self.remove_file_btn)
    
    self.remove_all_btn = QPushButton(f"Remove All Files")
    self.remove_all_btn.setMinimumHeight(45)
    self.remove_all_btn.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 59, 48, 0.8); color: white; border: none;
            border-radius: 6px; padding: 8px 16px; font-weight: bold;
        }
        QPushButton:hover { background-color: rgba(255, 59, 48, 1.0); }
        QPushButton:disabled {
            background-color: rgba(255, 59, 48, 0.4); color: rgba(255, 255, 255, 0.7);
        }
    """)
    file_buttons_layout.addWidget(self.remove_all_btn)
    
    self.refresh_btn = QPushButton(f"{GREEK_ICONS.get('refresh', '🔄')} Refresh List") # Changed icon key
    self.refresh_btn.setMinimumHeight(45)
    self.refresh_btn.setObjectName("secondary_button")
    file_buttons_layout.addWidget(self.refresh_btn)
    
    files_layout.addLayout(file_buttons_layout)
    
    self.layout.addWidget(self.files_group, 1)  # 1 = stretch factor
    # The processing UI (setup_processing_ui) is removed from here.
