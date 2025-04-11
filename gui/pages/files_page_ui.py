#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Files Page UI Components
Contains UI setup for the Files Page
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QPushButton, QFrame,
    QProgressBar, QSlider, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.styles import COLORS, GREEK_ICONS

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
        "documents you want to analyze. Each file will be processed individually."
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
    files_list_frame.setStyleSheet("#frosted_card { border-radius: 10px; min-height: 300px; }")
    files_list_layout = QVBoxLayout(files_list_frame)
    files_list_layout.setContentsMargins(1, 1, 1, 1)
    
    self.files_list = QListWidget()
    self.files_list.setStyleSheet("""
        QListWidget {
            background-color: rgba(255, 255, 255, 0.6);
            border: none;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        }
        QListWidget::item {
            border-radius: 5px;
            padding: 12px;
            margin: 5px 0px;
            min-height: 40px;
            color: #000000;
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(200, 200, 200, 0.7);
        }
        QListWidget::item:selected {
            background-color: rgba(0, 113, 227, 0.8);
            color: white;
            border: 1px solid rgba(0, 113, 227, 1.0);
        }
        QListWidget::item:hover:!selected {
            background-color: rgba(240, 240, 240, 0.9);
            border: 1px solid rgba(180, 180, 180, 0.7);
        }
        QScrollBar:vertical {
            border: none;
            background: rgba(240, 240, 240, 0.8);
            width: 16px;
            margin: 0px;
            border-radius: 8px;
        }
        QScrollBar::handle:vertical {
            background: rgba(160, 160, 160, 0.8);
            min-height: 40px;
            border-radius: 8px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(120, 120, 120, 0.9);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """)
    self.files_list.setMinimumHeight(300)
    self.files_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
    self.files_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.files_list.setWordWrap(True)
    self.files_list.setAlternatingRowColors(True)
    files_list_layout.addWidget(self.files_list)
    
    files_layout.addWidget(files_list_frame)
    
    # File management buttons with frosted card style
    file_buttons_layout = QHBoxLayout()
    file_buttons_layout.setSpacing(15)
    
    # Add file button with Greek icon
    self.add_file_btn = QPushButton(f"{GREEK_ICONS['upload']} Add Files")
    self.add_file_btn.setMinimumHeight(45)
    self.add_file_btn.setObjectName("secondary_button")
    file_buttons_layout.addWidget(self.add_file_btn)
    
    # Remove file button with Greek icon
    self.remove_file_btn = QPushButton(f"{GREEK_ICONS['remove']} Remove Selected")
    self.remove_file_btn.setMinimumHeight(45)
    self.remove_file_btn.setObjectName("secondary_button")
    self.remove_file_btn.setEnabled(False)  # Disabled until selection
    file_buttons_layout.addWidget(self.remove_file_btn)
    
    # Remove all files button with warning style
    self.remove_all_btn = QPushButton(f"Remove All Files")
    self.remove_all_btn.setMinimumHeight(45)
    self.remove_all_btn.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 59, 48, 0.8);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: rgba(255, 59, 48, 1.0);
        }
        QPushButton:disabled {
            background-color: rgba(255, 59, 48, 0.4);
            color: rgba(255, 255, 255, 0.7);
        }
    """)
    file_buttons_layout.addWidget(self.remove_all_btn)
    
    # Refresh list button
    self.refresh_btn = QPushButton(f"{GREEK_ICONS['config']} Refresh List")
    self.refresh_btn.setMinimumHeight(45)
    self.refresh_btn.setObjectName("secondary_button")
    file_buttons_layout.addWidget(self.refresh_btn)
    
    files_layout.addLayout(file_buttons_layout)
    
    self.layout.addWidget(self.files_group, 1)  # 1 = stretch factor
    
    # Add processing section
    setup_processing_ui(self)

def setup_processing_ui(self):
    """Set up the processing section UI"""
    # Processing section with frosted glass
    processing_frame = QFrame()
    processing_frame.setObjectName("frosted_content")
    processing_layout = QVBoxLayout(processing_frame)
    processing_layout.setContentsMargins(25, 25, 25, 25)
    processing_layout.setSpacing(20)
    
    # Processing title
    process_title = QLabel("Process Files")
    title_font = QFont()
    title_font.setPointSize(16)
    title_font.setBold(True)
    process_title.setFont(title_font)
    processing_layout.addWidget(process_title)
    
    # Rate limit warning with frosted glass card
    warning_frame = QFrame()
    warning_frame.setObjectName("frosted_card")
    warning_frame.setStyleSheet("""
        #frosted_card {
            background-color: rgba(255, 149, 0, 0.15);
            border: 1px solid rgba(255, 149, 0, 0.3);
        }
    """)
    warning_layout = QVBoxLayout(warning_frame)
    
    # Rate limit warning
    rate_limit_label = QLabel(
        "⚠️ API Rate Limiting: A delay is added between files to avoid "
        "hitting API rate limits. This ensures all files are processed properly."
    )
    rate_limit_label.setWordWrap(True)
    rate_limit_label.setStyleSheet("color: #D67D00; font-style: italic;")
    warning_layout.addWidget(rate_limit_label)
    
    processing_layout.addWidget(warning_frame)
    
    # Delay setting with frosted card style
    delay_frame = QFrame()
    delay_frame.setObjectName("frosted_card")
    delay_layout = QVBoxLayout(delay_frame)
    
    delay_title = QLabel("Processing Delay")
    delay_title.setStyleSheet("font-weight: bold; font-size: 14px;")
    delay_layout.addWidget(delay_title)
    
    delay_control_layout = QHBoxLayout()
    delay_label = QLabel("Delay between files (seconds):")
    delay_control_layout.addWidget(delay_label)
    
    self.delay_spinner = QSpinBox()
    self.delay_spinner.setMinimum(1)
    self.delay_spinner.setMaximum(60)
    self.delay_spinner.setValue(self.rate_limit_delay)
    self.delay_spinner.setMinimumWidth(80)
    self.delay_spinner.setMinimumHeight(40)
    self.delay_spinner.setStyleSheet("""
        QSpinBox {
            background-color: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(210, 210, 215, 0.8);
            border-radius: 6px;
            padding: 5px;
            font-size: 14px;
        }
    """)
    delay_control_layout.addWidget(self.delay_spinner)
    
    self.delay_slider = QSlider(Qt.Horizontal)
    self.delay_slider.setMinimum(1)
    self.delay_slider.setMaximum(60)
    self.delay_slider.setValue(self.rate_limit_delay)
    self.delay_slider.setMinimumHeight(45)  # Increased height significantly
    self.delay_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 16px;
            background: rgba(229, 229, 229, 0.7);
            border-radius: 8px;
            border: 1px solid rgba(210, 210, 215, 0.5);
        }
        
        QSlider::handle:horizontal {
            background: #8a3681;
            width: 30px;
            height: 30px;
            margin: -7px 0;
            border-radius: 15px;
            border: 2px solid rgba(138, 54, 129, 0.8);
        }
        
        QSlider::sub-page:horizontal {
            background: #8a3681;
            border-radius: 8px;
        }
    """)
    delay_control_layout.addWidget(self.delay_slider, 1)  # 1 = stretch factor
    
    delay_layout.addLayout(delay_control_layout)
    
    processing_layout.addWidget(delay_frame)
    
    # Progress section with frosted glass
    progress_frame = QFrame()
    progress_frame.setObjectName("frosted_card")
    progress_layout = QVBoxLayout(progress_frame)
    
    progress_title = QLabel("Processing Progress")
    progress_title.setStyleSheet("font-weight: bold; font-size: 14px;")
    progress_layout.addWidget(progress_title)
    
    # Progress bar with Apple style
    self.progress_bar = QProgressBar()
    self.progress_bar.setMinimum(0)
    self.progress_bar.setMaximum(100)
    self.progress_bar.setValue(0)
    self.progress_bar.setTextVisible(True)
    self.progress_bar.setFormat("%v% (%v of %m files)")
    self.progress_bar.setMinimumHeight(25)
    self.progress_bar.setStyleSheet("""
        QProgressBar {
            background-color: rgba(229, 229, 229, 0.7);
            border: none;
            border-radius: 8px;
            text-align: center;
            color: rgba(0, 0, 0, 0.7);
            font-weight: bold;
            min-height: 25px;
            font-size: 13px;
            padding: 0px 4px;
        }
        QProgressBar::chunk {
            background-color: #0071E3;
            border-radius: 8px;
        }
    """)
    progress_layout.addWidget(self.progress_bar)
    
    processing_layout.addWidget(progress_frame)
    
    # Process button
    self.process_btn = QPushButton(f"{GREEK_ICONS['start']} Process All Files")
    self.process_btn.setMinimumHeight(50)
    self.process_btn.setStyleSheet("""
        QPushButton {
            font-size: 16px;
            font-weight: bold;
        }
    """)
    processing_layout.addWidget(self.process_btn)
    
    self.layout.addWidget(processing_frame)
