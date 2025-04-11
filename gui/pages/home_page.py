#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Home Page
The landing page of the Configurational LLM application
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QSizePolicy, QFrame, QGridLayout
)
from PySide6.QtGui import QPixmap, QFont, QColor
from PySide6.QtCore import Qt, QSize
from gui.styles import COLORS

class HomePage(QWidget):
    """Application home page"""
    
    def __init__(self):
        """Initialize home page"""
        super().__init__()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)
        
        # Hero section with frosted glass effect
        hero_frame = QFrame()
        hero_frame.setObjectName("frosted_panel")
        hero_frame.setMaximumHeight(180)  # Limit hero height
        
        hero_layout = QVBoxLayout(hero_frame)
        hero_layout.setContentsMargins(25, 20, 25, 20)
        hero_layout.setSpacing(8)
        
        # App title with large, bold styling
        title_label = QLabel("Configurational LLM")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        hero_layout.addWidget(title_label)
        
        # Tagline with Apple-style secondary text
        tagline = QLabel("Process scientific literature with large language models")
        tagline.setObjectName("subtitle")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 15px;")
        hero_layout.addWidget(tagline)
        
        # Brief intro text
        intro_text = QLabel(
            "Welcome to Configurational LLM, an advanced tool designed for researchers and academics "
            "to analyze scientific literature using large language models. This application helps you extract valuable insights from academic papers "
            "through structured prompting and comprehensive analysis."
        )
        intro_text.setWordWrap(True)
        intro_text.setAlignment(Qt.AlignCenter)
        intro_text.setStyleSheet("line-height: 140%; font-size: 13px;")
        hero_layout.addWidget(intro_text)
        
        self.layout.addWidget(hero_frame)
        
        # University logos in a grid with minimal styling
        logos_layout = QHBoxLayout()
        logos_layout.setContentsMargins(20, 10, 20, 10)
        logos_layout.setSpacing(40)
        logos_layout.setAlignment(Qt.AlignCenter)
        
        # Durham logo and label in container with white background
        durham_container = QFrame()
        durham_container.setObjectName("logo_container")  # Apply white background style
        durham_layout = QVBoxLayout(durham_container)
        durham_layout.setContentsMargins(15, 15, 15, 15)
        durham_layout.setSpacing(5)
        
        durham_logo = QLabel()
        durham_pixmap = QPixmap(os.path.join("logos", "durham.png"))
        # Higher resolution scaling - maintain aspect ratio but allow more detail
        durham_pixmap = durham_pixmap.scaled(150, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        durham_logo.setPixmap(durham_pixmap)
        durham_logo.setAlignment(Qt.AlignCenter)
        durham_layout.addWidget(durham_logo)
        
        durham_label = QLabel("Durham University")
        durham_label.setAlignment(Qt.AlignCenter)
        durham_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        durham_layout.addWidget(durham_label)
        
        logos_layout.addWidget(durham_container)
        
        # Tsinghua logo and label in container with white background
        tsinghua_container = QFrame()
        tsinghua_container.setObjectName("logo_container")  # Apply white background style
        tsinghua_layout = QVBoxLayout(tsinghua_container)
        tsinghua_layout.setContentsMargins(15, 15, 15, 15)
        tsinghua_layout.setSpacing(5)
        
        tsinghua_logo = QLabel()
        tsinghua_pixmap = QPixmap(os.path.join("logos", "tsinghua-LOGO-01.png"))
        # Higher resolution scaling - maintain aspect ratio but allow more detail
        tsinghua_pixmap = tsinghua_pixmap.scaled(150, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        tsinghua_logo.setPixmap(tsinghua_pixmap)
        tsinghua_logo.setAlignment(Qt.AlignCenter)
        tsinghua_layout.addWidget(tsinghua_logo)
        
        tsinghua_label = QLabel("Tsinghua University")
        tsinghua_label.setAlignment(Qt.AlignCenter)
        tsinghua_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        tsinghua_layout.addWidget(tsinghua_label)
        
        logos_layout.addWidget(tsinghua_container)
        
        self.layout.addLayout(logos_layout)
        
        # Steps section with individual step items instead of separate layouts
        steps_frame = QFrame()
        steps_frame.setObjectName("frosted_card")
        steps_frame.setMinimumHeight(180)
        steps_frame.setMaximumHeight(220)
        
        steps_layout = QVBoxLayout(steps_frame)
        steps_layout.setContentsMargins(20, 20, 20, 20)
        steps_layout.setSpacing(15)  # Increased spacing between steps
        
        # Steps with modern styling
        steps = [
            "Configure your API settings with Claude or OpenAI API key",
            "Review and customize prompt templates",
            "Set up message parameters",
            "Add research documents to the Files Library",
            "Run the processor and monitor results in Live Output"
        ]
        
        for i, step_text in enumerate(steps, 1):
            step_item = QHBoxLayout()
            step_item.setSpacing(15)
            
            # Number in circle
            number_label = QLabel(str(i))
            number_label.setAlignment(Qt.AlignCenter)
            number_label.setStyleSheet(f"""
                background-color: {COLORS['accent']};
                color: white;
                border-radius: 12px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
                font-weight: bold;
                font-size: 12px;
            """)
            
            # Step content
            step_content = QLabel(step_text)
            step_content.setWordWrap(True)
            step_content.setStyleSheet("font-size: 13px;")
            
            step_item.addWidget(number_label)
            step_item.addWidget(step_content, 1)  # 1 = stretch factor
            
            steps_layout.addLayout(step_item)
        
        self.layout.addWidget(steps_frame)
        
        # Add stretch to ensure proper spacing
        self.layout.addStretch(1)
        
        # Copyright information with modern styling
        copyright_label = QLabel("©configurational.tech contributors")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.layout.addWidget(copyright_label)
