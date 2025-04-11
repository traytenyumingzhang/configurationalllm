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
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

from gui.pages.home_page import HomePage
from gui.pages.api_settings_page import APISettingsPage
from gui.pages.prompts_page import PromptsPage
from gui.pages.message_page import MessagePage
from gui.pages.files_page import FilesPage
from gui.pages.live_output_page import LiveOutputPage
from gui.pages.about_page import AboutPage

from utils.config_manager import ConfigManager
from core.llm_processor import LLMProcessor
from gui.styles import get_application_stylesheet, GREEK_ICONS, COLORS

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        # Initialize configuration and LLM processor
        self.config_manager = ConfigManager()
        self.llm_processor = LLMProcessor(self.config_manager)
        
        # Apply stylesheet
        self.setStyleSheet(get_application_stylesheet())
        
        # Main window properties
        self.setWindowTitle("Configurational LLM")
        self.setMinimumSize(1200, 800)
        
        # Initialize UI components
        self._init_ui()
        
        # Connect signals and slots
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize UI components"""
        # Central widget and main layout
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)
        
        # Left sidebar for navigation
        self._init_sidebar()
        
        # Right side content area
        self._init_content_area()
        
        # Initialize pages
        self._init_pages()
        
        # Show initial page (Home)
        self.page_stack.setCurrentIndex(0)
        self.nav_list.setCurrentRow(0)
    
    def _init_sidebar(self):
        """Initialize left sidebar with navigation"""
        # Sidebar container
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMaximumWidth(250)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(20)
        
        # App title with apple-style logo
        app_logo_layout = QHBoxLayout()
        app_logo_layout.setAlignment(Qt.AlignCenter)
        
        # App logo (using stylized Greek letter from our GREEK_ICONS)
        app_logo = QLabel("λ")  # Lambda for logo
        logo_font = app_logo.font()
        logo_font.setPointSize(36)
        logo_font.setBold(True)
        app_logo.setFont(logo_font)
        app_logo.setStyleSheet(f"color: {COLORS['accent']};")
        app_logo_layout.addWidget(app_logo)
        
        sidebar_layout.addLayout(app_logo_layout)
        
        # App title
        app_title = QLabel("Configurational LLM")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        sidebar_layout.addWidget(app_title)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("font-size: 15px;")
        self.nav_list.setIconSize(QSize(20, 20))
        
        # Navigation items with Greek letter icons
        nav_items = [
            (GREEK_ICONS["home"], "Home", "Home"),
            (GREEK_ICONS["settings"], "API Settings", "API Settings"),
            (GREEK_ICONS["prompts"], "Prompts", "Prompts"),
            (GREEK_ICONS["message"], "Message", "Message"),
            (GREEK_ICONS["files"], "Files Library", "Files Library"),
            (GREEK_ICONS["output"], "Live Output", "Live Output"),
            (GREEK_ICONS["about"], "About", "About")
        ]
        
        for icon_text, item_text, item_data in nav_items:
            item = QListWidgetItem()
            
            # Create a widget for the item with icon and text in layout
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 5, 5, 5)
            
            # Greek letter icon
            icon_label = QLabel(icon_text)
            icon_font = icon_label.font()
            icon_font.setPointSize(15)
            icon_label.setFont(icon_font)
            icon_label.setMinimumWidth(25)
            item_layout.addWidget(icon_label)
            
            # Item text
            text_label = QLabel(item_text)
            item_layout.addWidget(text_label)
            
            # Set data for navigation
            item.setData(Qt.UserRole, item_data)
            
            # Add to list widget
            self.nav_list.addItem(item)
            item.setSizeHint(item_widget.sizeHint())
            self.nav_list.setItemWidget(item, item_widget)
        
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        
        # App version at bottom of sidebar
        version_label = QLabel("Version λ - 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        sidebar_layout.addWidget(version_label)
        
        # Add sidebar to main layout
        self.main_layout.addWidget(self.sidebar)
    
    def _init_content_area(self):
        """Initialize right content area with stacked pages"""
        # Content area container
        self.content_area = QFrame()
        self.content_area.setObjectName("content_area")
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(0)
        
        # Stacked widget for pages
        self.page_stack = QStackedWidget()
        content_layout.addWidget(self.page_stack)
        
        # Add content area to main layout
        self.main_layout.addWidget(self.content_area, 1)  # 1 = stretch factor
    
    def _init_pages(self):
        """Initialize and add pages to stack"""
        # Home page
        home_page = HomePage()
        self.page_stack.addWidget(home_page)
        
        # API Settings page
        api_settings_page = APISettingsPage(self.config_manager)
        self.page_stack.addWidget(api_settings_page)
        
        # Prompts page
        prompts_page = PromptsPage(self.config_manager)
        self.page_stack.addWidget(prompts_page)
        
        # Message page
        message_page = MessagePage(self.config_manager)
        self.page_stack.addWidget(message_page)
        
        # Files page
        files_page = FilesPage(self.config_manager, self.llm_processor)
        self.page_stack.addWidget(files_page)
        
        # Live Output page
        live_output_page = LiveOutputPage(self.llm_processor)
        self.page_stack.addWidget(live_output_page)
        
        # About page
        about_page = AboutPage(self.config_manager)
        self.page_stack.addWidget(about_page)
    
    def _connect_signals(self):
        """Connect signals and slots"""
        # Navigation
        self.nav_list.currentRowChanged.connect(self.page_stack.setCurrentIndex)
        
        # Connect API settings update signal to refresh LLM processor
        for i in range(self.page_stack.count()):
            page = self.page_stack.widget(i)
            if hasattr(page, 'settings_updated'):
                page.settings_updated.connect(self.llm_processor.refresh_settings)
