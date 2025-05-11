#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processing Settings Page UI Components
Contains UI setup for configuring processing parameters.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSlider, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.styles import GREEK_ICONS # Assuming GREEK_ICONS for save button

def setup_processing_settings_ui(self):
    """Set up the user interface for the Processing Settings Page"""
    # Main layout
    self.layout = QVBoxLayout(self)
    self.layout.setContentsMargins(40, 40, 40, 40)
    self.layout.setSpacing(25)
    self.layout.setAlignment(Qt.AlignTop) # Align content to the top

    # Page title
    title_label = QLabel("Processing Settings")
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
        "Configure parameters for file processing, such as the number of analysis "
        "iterations per file and the delay between processing individual files or iterations."
    )
    desc_label.setWordWrap(True)
    desc_label.setStyleSheet("font-size: 14px; line-height: 150%;")
    desc_layout.addWidget(desc_label)
    self.layout.addWidget(desc_frame)

    # Settings group with frosted glass styling
    settings_group = QFrame()
    settings_group.setObjectName("frosted_content")
    settings_layout = QVBoxLayout(settings_group)
    settings_layout.setContentsMargins(25, 25, 25, 25)
    settings_layout.setSpacing(20)

    # Iterations setting with frosted card style
    iterations_frame = QFrame()
    iterations_frame.setObjectName("frosted_card")
    iterations_card_layout = QVBoxLayout(iterations_frame)

    iterations_title = QLabel("Analysis Iterations")
    iterations_title.setStyleSheet("font-weight: bold; font-size: 14px;")
    iterations_card_layout.addWidget(iterations_title)

    iterations_control_layout = QHBoxLayout()
    iterations_label = QLabel("Number of iterations per file:")
    iterations_control_layout.addWidget(iterations_label)

    self.iterations_spinner = QSpinBox()
    self.iterations_spinner.setMinimum(1)
    self.iterations_spinner.setMaximum(10) 
    self.iterations_spinner.setValue(self.num_iterations) # Initialized by parent class
    self.iterations_spinner.setMinimumWidth(80)
    self.iterations_spinner.setMinimumHeight(40)
    self.iterations_spinner.setStyleSheet("""
        QSpinBox {
            background-color: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(210, 210, 215, 0.8);
            border-radius: 6px;
            padding: 5px;
            font-size: 14px;
        }
    """)
    iterations_control_layout.addWidget(self.iterations_spinner)

    self.iterations_slider = QSlider(Qt.Horizontal)
    self.iterations_slider.setMinimum(1)
    self.iterations_slider.setMaximum(10)
    self.iterations_slider.setValue(self.num_iterations) # Initialized by parent class
    self.iterations_slider.setMinimumHeight(45)
    self.iterations_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 16px; background: rgba(229, 229, 229, 0.7);
            border-radius: 8px; border: 1px solid rgba(210, 210, 215, 0.5);
        }
        QSlider::handle:horizontal {
            background: #8a3681; width: 30px; height: 30px;
            margin: -7px 0; border-radius: 15px; border: 2px solid rgba(138, 54, 129, 0.8);
        }
        QSlider::sub-page:horizontal { background: #8a3681; border-radius: 8px; }
    """)
    iterations_control_layout.addWidget(self.iterations_slider, 1)
    
    iterations_card_layout.addLayout(iterations_control_layout)
    settings_layout.addWidget(iterations_frame)
    
    # Delay setting with frosted card style
    delay_frame = QFrame()
    delay_frame.setObjectName("frosted_card")
    delay_card_layout = QVBoxLayout(delay_frame)
    
    delay_title = QLabel("Processing Delay")
    delay_title.setStyleSheet("font-weight: bold; font-size: 14px;")
    delay_card_layout.addWidget(delay_title)
    
    delay_control_layout = QHBoxLayout()
    delay_label = QLabel("Delay between processing steps (seconds):")
    delay_control_layout.addWidget(delay_label)
    
    self.delay_spinner = QSpinBox()
    self.delay_spinner.setMinimum(0) # Allow 0 delay
    self.delay_spinner.setMaximum(60)
    self.delay_spinner.setValue(self.rate_limit_delay) # Initialized by parent class
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
    self.delay_slider.setMinimum(0) # Allow 0 delay
    self.delay_slider.setMaximum(60)
    self.delay_slider.setValue(self.rate_limit_delay) # Initialized by parent class
    self.delay_slider.setMinimumHeight(45)
    self.delay_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 16px; background: rgba(229, 229, 229, 0.7);
            border-radius: 8px; border: 1px solid rgba(210, 210, 215, 0.5);
        }
        QSlider::handle:horizontal {
            background: #8a3681; width: 30px; height: 30px;
            margin: -7px 0; border-radius: 15px; border: 2px solid rgba(138, 54, 129, 0.8);
        }
        QSlider::sub-page:horizontal { background: #8a3681; border-radius: 8px; }
    """)
    delay_control_layout.addWidget(self.delay_slider, 1)
    
    delay_card_layout.addLayout(delay_control_layout)
    settings_layout.addWidget(delay_frame)

    # Save button
    self.save_settings_btn = QPushButton(f"{GREEK_ICONS.get('save', '💾')} Save Settings") # Use a default if save icon missing
    self.save_settings_btn.setMinimumHeight(50)
    self.save_settings_btn.setObjectName("primary_button") # Assuming a primary button style
    self.save_settings_btn.setStyleSheet("""
        QPushButton { font-size: 16px; font-weight: bold; }
    """) # Basic styling, can be enhanced
    settings_layout.addWidget(self.save_settings_btn)
    
    settings_layout.addStretch(1) # Add stretch to push settings to the top
    self.layout.addWidget(settings_group)
    self.layout.addStretch(1) # Add stretch to main layout
