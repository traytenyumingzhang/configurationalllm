#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ultra Minimal Files Page
"""

import os
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal

class FilesPage(QWidget):
    """Ultra simple files page"""
    
    # Required signal for inter-component communication
    files_updated = Signal()
    
    def __init__(self, config_manager, llm_processor):
        super().__init__()
        
        self.config_manager = config_manager
        self.llm_processor = llm_processor
        self.output_dir = config_manager.get_output_dir()
        self.files_dir = os.path.join(self.output_dir, 'files')
        
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)
        
        # Ultra basic layout
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Files")
        layout.addWidget(title)
        
        # Files list
        self.files_list = QListWidget()
        layout.addWidget(self.files_list)
        
        # Buttons
        buttons = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.remove_btn = QPushButton("Remove")
        self.remove_all_btn = QPushButton("Delete All")  # Added Delete All button
        
        buttons.addWidget(self.add_btn)
        buttons.addWidget(self.remove_btn)
        buttons.addWidget(self.remove_all_btn)  # Added to layout
        
        layout.addLayout(buttons)
        
        # Connect buttons
        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn.clicked.connect(self.remove_files)
        self.remove_all_btn.clicked.connect(self.remove_all_files)  # Connect new button
        
        # Load files
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh files list"""
        self.files_list.clear()
        files = self.llm_processor.get_files_list()
        for file in files:
            self.files_list.addItem(file)
    
    def add_files(self):
        """Add files"""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:  # Only proceed if files were selected
            for file_path in files:
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(self.files_dir, file_name)
                shutil.copy2(file_path, dest_path)
            self.refresh_list()
            self.files_updated.emit()  # Emit signal when files are updated
    
    def remove_files(self):
        """Remove selected files"""
        items = self.files_list.selectedItems()
        if items:  # Only proceed if items are selected
            for item in items:
                file_name = item.text()
                file_path = os.path.join(self.files_dir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.refresh_list()
            self.files_updated.emit()  # Emit signal when files are updated
    
    def remove_all_files(self):
        """Remove all files from directory"""
        files = self.llm_processor.get_files_list()
        if not files:
            QMessageBox.information(self, "No Files", "No files to delete.")
            return
            
        result = QMessageBox.question(
            self, "Confirm Delete All", 
            f"Are you sure you want to delete all {len(files)} files?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            for file_name in files:
                file_path = os.path.join(self.files_dir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.refresh_list()
            self.files_updated.emit()  # Emit signal when files are updated
