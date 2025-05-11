#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Files Page for managing files.
Integrates UI from files_page_ui.py and handles file operations.
"""

import os
import shutil
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PySide6.QtCore import Signal

# Import the UI setup function
from .files_page_ui import setup_ui

class FilesPage(QWidget):
    """
    Manages the files page UI and file management operations.
    """
    files_updated = Signal() # Emitted when files are added or removed

    def __init__(self, config_manager, llm_processor, main_window=None): # llm_processor might not be needed here anymore
        super().__init__()
        
        self.config_manager = config_manager
        # self.llm_processor = llm_processor # Potentially remove if not used for get_files_list
        self.main_window = main_window 

        self.output_dir = self.config_manager.get_output_dir()
        self.files_dir = os.path.join(self.output_dir, 'files')
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir, exist_ok=True)
        
        # Setup UI using the imported function
        setup_ui(self) 
        
        # Connect signals from UI elements to handler methods
        self._connect_signals()
        
        # Initial population of the file list and UI state update
        self.refresh_files_list()
        # self.update_button_states() # refresh_files_list calls this

    def _connect_signals(self):
        """Connects all UI element signals to their respective slots."""
        # File management buttons
        self.add_file_btn.clicked.connect(self.add_files_action)
        self.remove_file_btn.clicked.connect(self.remove_selected_files_action)
        self.remove_all_btn.clicked.connect(self.remove_all_files_action)
        self.refresh_btn.clicked.connect(self.refresh_files_list)
        
        # File list selection changes
        self.files_list.itemSelectionChanged.connect(self.update_button_states)
        
    # --- File Operations ---
    def refresh_files_list(self):
        """Refreshes the list of files displayed from the files directory."""
        self.files_list.clear()
        if os.path.exists(self.files_dir):
            try:
                files_in_dir = [f for f in os.listdir(self.files_dir) 
                                if os.path.isfile(os.path.join(self.files_dir, f)) and not f.startswith('.')]
                for file_name in sorted(files_in_dir): # Sort for consistent order
                    self.files_list.addItem(file_name)
            except OSError as e:
                QMessageBox.critical(self, "Error Listing Files", f"Could not read files directory: {e}")
        self.update_button_states()

    def add_files_action(self):
        """Opens a dialog to select files and copies them to the files directory."""
        last_dir = self.config_manager.get_setting('last_opened_dir', os.path.expanduser("~"))
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Add", last_dir,
            "All Supported Files (*.txt *.pdf *.docx *.md *.json *.xml *.html *.png *.jpg *.jpeg *.gif *.webp);;Text Files (*.txt *.md *.csv *.json *.xml *.html);;PDF Files (*.pdf);;Word Documents (*.docx);;Image Files (*.png *.jpg *.jpeg *.gif *.webp);;All Files (*)"
        )
        
        if files:
            added_count = 0
            for file_path in files:
                if not file_path: continue
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(self.files_dir, file_name)
                
                if os.path.exists(dest_path):
                    reply = QMessageBox.question(self, "File Exists", 
                                                 f"File '{file_name}' already exists. Overwrite?",
                                                 QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                                                 QMessageBox.No)
                    if reply == QMessageBox.No:
                        continue
                    if reply == QMessageBox.Cancel:
                        break 
                try:
                    shutil.copy2(file_path, dest_path)
                    added_count += 1
                except Exception as e:
                    QMessageBox.warning(self, "Copy Error", f"Could not copy '{file_name}': {e}")
            
            if added_count > 0:
                self.refresh_files_list()
                self.files_updated.emit()
            
            if files: # Ensure files list is not empty before accessing os.path.dirname(files[0])
                self.config_manager.save_setting('last_opened_dir', os.path.dirname(files[0]))

    def remove_selected_files_action(self):
        """Removes selected files from the list and the files directory."""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            # QMessageBox.information(self, "No Selection", "No files selected to remove.") # Can be a bit noisy
            return

        confirm = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove {len(selected_items)} selected file(s)? This action is permanent.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            removed_count = 0
            for item in selected_items:
                file_name = item.text()
                file_path = os.path.join(self.files_dir, file_name)
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        removed_count += 1
                except Exception as e:
                    QMessageBox.warning(self, "Delete Error", f"Could not delete '{file_name}': {e}")
            
            if removed_count > 0:
                self.refresh_files_list() 
                self.files_updated.emit()

    def remove_all_files_action(self):
        """Removes all files from the list and the files directory after confirmation."""
        if self.files_list.count() == 0:
            QMessageBox.information(self, "No Files", "There are no files to remove.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Remove All",
            "Are you sure you want to remove ALL files from the library? This action is permanent.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            all_files_in_list = [self.files_list.item(i).text() for i in range(self.files_list.count())]
            removed_count = 0
            for file_name in all_files_in_list:
                file_path = os.path.join(self.files_dir, file_name)
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        removed_count += 1
                except Exception as e:
                    QMessageBox.warning(self, "Delete Error", f"Could not delete '{file_name}': {e}")
            
            if removed_count > 0:
                self.refresh_files_list()
                self.files_updated.emit()

    # --- UI State Management ---
    def update_button_states(self):
        """Updates the enabled/disabled state of various buttons based on current context."""
        # This page no longer manages processing state, so buttons are always enabled/disabled based on list content
        has_selection = bool(self.files_list.selectedItems())
        is_list_empty = self.files_list.count() == 0
        
        self.remove_file_btn.setEnabled(has_selection)
        self.remove_all_btn.setEnabled(not is_list_empty)
        # Add and refresh buttons are always enabled
        self.add_file_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)

    def enter_page(self):
        """Called when the page is navigated to. Ensures file list is fresh."""
        self.refresh_files_list()

    def leave_page(self):
        """Called when the page is navigated away from."""
        pass
