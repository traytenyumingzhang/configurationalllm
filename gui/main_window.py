#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window
Application's main window and navigation
"""

import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QStackedWidget,
    QFrame, QSizePolicy, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QThreadPool 
from PySide6.QtGui import QFont, QIcon, QPixmap

from gui.pages.home_page import HomePage
from gui.pages.api_settings_page import APISettingsPage
from gui.pages.prompts_page import PromptsPage
from gui.pages.message_page import MessagePage
from gui.pages.files_page import FilesPage
from gui.pages.processing_settings_page import ProcessingSettingsPage
from gui.pages.live_output_page import LiveOutputPage
from gui.pages.about_page import AboutPage

from utils.config_manager import ConfigManager
from core.llm_processor import LLMProcessor
from gui.styles import get_application_stylesheet, GREEK_ICONS, COLORS

class MainWindow(QMainWindow):
    """Main application window"""
    
    APP_VERSION = "1.0.1" # Define app version

    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        self.config_manager = ConfigManager()
        self.llm_processor = LLMProcessor(self.config_manager)
        
        self.setStyleSheet(get_application_stylesheet())
        
        self.setWindowTitle("Configurational LLM")
        self.setMinimumSize(1200, 800) 
        
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)
        
        self._init_sidebar()
        self._init_content_area()
        self._init_pages()
        
        self.page_stack.setCurrentIndex(0)
        self.nav_list.setCurrentRow(0)
    
    def _init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMaximumWidth(280) 
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15) 
        
        app_logo_layout = QHBoxLayout()
        app_logo_layout.setAlignment(Qt.AlignCenter)
        app_logo = QLabel("λ")
        logo_font = app_logo.font(); logo_font.setPointSize(36); logo_font.setBold(True)
        app_logo.setFont(logo_font); app_logo.setStyleSheet(f"color: {COLORS['accent']};")
        app_logo_layout.addWidget(app_logo)
        sidebar_layout.addLayout(app_logo_layout)
        
        app_title = QLabel("Configurational LLM")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        sidebar_layout.addWidget(app_title)
        
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("font-size: 15px;") 
        self.nav_list.setIconSize(QSize(22, 22)) 

        nav_items = [
            (GREEK_ICONS.get("home", "🏠"), "Home", "Home"),
            (GREEK_ICONS.get("settings", "⚙️"), "API Settings", "API Settings"),
            (GREEK_ICONS.get("prompts", "📜"), "Prompts", "Prompts"),
            (GREEK_ICONS.get("message", "✉️"), "Message", "Message"),
            (GREEK_ICONS.get("files", "📁"), "Files Library", "Files Library"),
            (GREEK_ICONS.get("config", "🛠️"), "Processing Settings", "Processing Settings"), 
            (GREEK_ICONS.get("output", "📊"), "Live Output", "Live Output"),
            (GREEK_ICONS.get("about", "ℹ️"), "About", "About")
        ]
        
        for icon_char, item_text, item_data in nav_items:
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(8, 8, 8, 8) 
            
            icon_label = QLabel(icon_char)
            icon_font = icon_label.font(); icon_font.setPointSize(16); 
            icon_label.setFont(icon_font); icon_label.setMinimumWidth(30) 
            item_layout.addWidget(icon_label)
            
            text_label = QLabel(item_text)
            item_layout.addWidget(text_label)
            
            item.setData(Qt.UserRole, item_data)
            self.nav_list.addItem(item)
            item.setSizeHint(item_widget.sizeHint())
            self.nav_list.setItemWidget(item, item_widget)
        
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        
        version_label = QLabel(f"Version λ - {self.APP_VERSION}") # Use APP_VERSION
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(f"color: {COLORS.get('text_secondary', '#888')}; font-size: 12px;")
        sidebar_layout.addWidget(version_label)
        
        self.main_layout.addWidget(self.sidebar)
    
    def _init_content_area(self):
        self.content_area = QFrame()
        self.content_area.setObjectName("content_area")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(20, 20, 20, 20) 
        content_layout.setSpacing(0)
        self.page_stack = QStackedWidget()
        content_layout.addWidget(self.page_stack)
        self.main_layout.addWidget(self.content_area, 1)
    
    def _init_pages(self):
        pages_config = [
            (HomePage, []),
            (APISettingsPage, [self.config_manager]),
            (PromptsPage, [self.config_manager]),
            (MessagePage, [self.config_manager]),
            (FilesPage, [self.config_manager, self.llm_processor]),
            (ProcessingSettingsPage, [self.config_manager]), 
            (LiveOutputPage, [self.config_manager, self.llm_processor]), 
            (AboutPage, [self.config_manager]) # Pass APP_VERSION to AboutPage if needed
        ]

        for PageClass, args in pages_config:
            # Pass main_window, which contains APP_VERSION if AboutPage needs it directly
            # Or AboutPage can fetch it from main_window instance if passed
            page_instance = PageClass(*args, main_window=self) 
            self.page_stack.addWidget(page_instance)

            if hasattr(page_instance, 'settings_updated'):
                if isinstance(page_instance, (APISettingsPage, PromptsPage, MessagePage)):
                    page_instance.settings_updated.connect(self.llm_processor.refresh_settings)
    
    def _connect_signals(self):
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)

    def _on_nav_changed(self, row):
        self.page_stack.setCurrentIndex(row)
        current_page = self.page_stack.widget(row)
        if hasattr(current_page, 'enter_page'):
            current_page.enter_page()

    def closeEvent(self, event):
        QThreadPool.globalInstance().waitForDone(-1) 
        super().closeEvent(event)
