#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
About Page
Information about the application and settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

class AboutPage(QWidget):
    """About information page"""
    
    def __init__(self, config_manager):
        """Initialize about page"""
        super().__init__()
        
        self.config_manager = config_manager
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Page title
        title_label = QLabel("About Configurational LLM")
        title_font = title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.layout.addWidget(title_label)
        
        # Version info
        version_label = QLabel("Version λ-1.0.0")
        self.layout.addWidget(version_label)
        
        # Copyright
        copyright_label = QLabel("©configurational.tech contributors")
        copyright_label.setStyleSheet("font-style: italic;")
        self.layout.addWidget(copyright_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)
        
        # Contributors group
        contributors_group = QGroupBox("Contributors")
        contributors_layout = QVBoxLayout(contributors_group)
        
        # CRediT statement
        credit_label = QLabel("CRediT statement:")
        contributors_layout.addWidget(credit_label)
        
        # Contributors list with CRediT roles
        contributors = [
            "Yuming (Trayten) Zhang: Conceptualisation, Methodology, Software, Validation, Resources, Visualisation.",
            "Linrui Zhong: Validation, Investigation.",
            "Tiago Moreira: Supervision (external to the core team).",
            "Jonathan Wistow: Supervision (external to the core team)."
        ]
        
        for contributor in contributors:
            label = QLabel(contributor)
            contributors_layout.addWidget(label)
        
        self.layout.addWidget(contributors_group)
        
        # Logos (Durham and Tsinghua)
        logos_group = QGroupBox("Academic Affiliations to contributors")
        logos_layout = QHBoxLayout(logos_group)
        
        # Durham logo
        durham_logo = QLabel()
        durham_pixmap = QPixmap("logos/durham.png")
        
        if not durham_pixmap.isNull():
            # Scale while maintaining aspect ratio
            durham_pixmap = durham_pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            durham_logo.setPixmap(durham_pixmap)
            durham_logo.setAlignment(Qt.AlignCenter)
        else:
            durham_logo.setText("Durham University")
            durham_logo.setAlignment(Qt.AlignCenter)
        
        # Tsinghua logo
        tsinghua_logo = QLabel()
        tsinghua_pixmap = QPixmap("logos/tsinghua-LOGO-01.png")
        
        if not tsinghua_pixmap.isNull():
            # Scale while maintaining aspect ratio
            tsinghua_pixmap = tsinghua_pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            tsinghua_logo.setPixmap(tsinghua_pixmap)
            tsinghua_logo.setAlignment(Qt.AlignCenter)
        else:
            tsinghua_logo.setText("Tsinghua University")
            tsinghua_logo.setAlignment(Qt.AlignCenter)
        
        logos_layout.addWidget(durham_logo)
        logos_layout.addWidget(tsinghua_logo)
        
        self.layout.addWidget(logos_group)
        
        # Font note
        font_note = QLabel(
            "Note: This application uses system default fonts to avoid potential copyright issues."
        )
        font_note.setStyleSheet("color: gray; font-style: italic;")
        font_note.setWordWrap(True)
        self.layout.addWidget(font_note)
        
        # Third-party licenses
        licenses_group = QGroupBox("Third-Party Licenses")
        licenses_layout = QVBoxLayout(licenses_group)
        
        license_intro = QLabel(
            "This software incorporates third-party components under their respective licenses:"
        )
        license_intro.setWordWrap(True)
        licenses_layout.addWidget(license_intro)
        
        # List of third-party licenses
        third_party_licenses = [
            "Python: Python Software Foundation License",
            "PySide6: LGPL-3.0",
            "anthropic: MIT License",
            "openai: MIT License",
            "PyPDF2: BSD License",
            "pandas: BSD-3 License",
            "requests: Apache License 2.0",
            "google-generativeai: Apache License 2.0"
        ]
        
        for license_info in third_party_licenses:
            label = QLabel("- " + license_info)
            label.setWordWrap(True)
            licenses_layout.addWidget(label)
        
        compliance_note = QLabel(
            "Users must comply with all terms of these licenses when using this software."
        )
        compliance_note.setWordWrap(True)
        compliance_note.setStyleSheet("font-weight: bold;")
        licenses_layout.addWidget(compliance_note)
        
        self.layout.addWidget(licenses_group)
        
        # Add stretch to push content to the top
        self.layout.addStretch()
