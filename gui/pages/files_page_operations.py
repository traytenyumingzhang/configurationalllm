#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Files Page Operations
Contains file operation handlers for the Files Page
"""

import os
import shutil
from PySide6.QtWidgets import (
    QMessageBox, QFileDialog, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer

def file_operations_setup(self):
    """Set up the signals for file operations"""
    # Connect signals
    self.add_file_btn.clicked.connect(self._add_files)
    self.remove_file_btn.clicked.connect(self._remove_selected_files)
    self.remove_all_btn.clicked.connect(self._remove_all_files)
    self.refresh_btn.clicked.connect(self._refresh_files_list)
    self.process_btn.clicked.connect(self._process_files)
    self.files_list.itemSelectionChanged.connect(self._on_selection_changed)
    
    # Connect spinner and slider
    self.delay_spinner.valueChanged.connect(self.delay_slider.setValue)
    self.delay_slider.valueChanged.connect(self.delay_spinner.setValue)
    self.delay_spinner.valueChanged.connect(self._update_delay)

def _update_delay(self, value):
    """Update the rate limit delay"""
    self.rate_limit_delay = value

def _refresh_files_list(self):
    """Refresh the files list"""
    self.files_list.clear()
    
    files = self.llm_processor.get_files_list()
    
    if not files:
        item = QListWidgetItem("No files available")
        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        item.setData(Qt.UserRole, "no_files")
        self.files_list.addItem(item)
        self.process_btn.setEnabled(False)
        self.remove_all_btn.setEnabled(False)
    else:
        for file in files:
            item = QListWidgetItem(file)
            # Store original filename in user role data
            item.setData(Qt.UserRole, file)
            # Force the item to handle the text as rich text to enable word wrapping
            item.setData(Qt.DisplayRole, file)
            # Set tooltip to show full name on hover
            item.setToolTip(file)
            self.files_list.addItem(item)
        self.process_btn.setEnabled(True)
        self.remove_all_btn.setEnabled(True)
    
    # Update progress bar
    self.progress_bar.setMaximum(len(files) if files else 100)
    self.progress_bar.setValue(0)
    self.progress_bar.setFormat("0% (0 of %m files)")

def _add_files(self):
    """Add files to the library"""
    try:
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(
            "Documents (*.pdf *.txt *.md *.docx *.doc *.rtf *.csv *.json *.html *.htm);;"
            "Images (*.jpg *.jpeg *.png);;"
            "All Files (*.*)"
        )
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            files_added = 0
            
            for file_path in file_paths:
                try:
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(self.files_dir, file_name)
                    
                    # Check if file already exists
                    if os.path.exists(dest_path):
                        result = QMessageBox.question(
                            self, "File Exists", 
                            f"File '{file_name}' already exists. Overwrite?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if result != QMessageBox.Yes:
                            continue
                    
                    # Copy file to files directory
                    shutil.copy2(file_path, dest_path)
                    files_added += 1
                
                except Exception as e:
                    QMessageBox.warning(
                        self, "File Error", 
                        f"Error adding file '{os.path.basename(file_path)}': {str(e)}"
                    )
            
            if files_added > 0:
                QMessageBox.information(
                    self, "Files Added", 
                    f"{files_added} file(s) added successfully."
                )
                self._refresh_files_list()
                self.files_updated.emit()
    
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

def _remove_selected_files(self):
    """Remove selected files from the library"""
    selected_items = self.files_list.selectedItems()
    
    if not selected_items:
        return
    
    result = QMessageBox.question(
        self, "Confirm Delete", 
        f"Are you sure you want to delete {len(selected_items)} file(s)?",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if result != QMessageBox.Yes:
        return
    
    files_removed = 0
    
    for item in selected_items:
        # Get filename from the UserRole data to avoid any display formatting issues
        file_name = item.data(Qt.UserRole)
        if file_name == "no_files":
            continue
            
        file_path = os.path.join(self.files_dir, file_name)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                files_removed += 1
        except Exception as e:
            QMessageBox.warning(
                self, "File Error", 
                f"Error removing file '{file_name}': {str(e)}"
            )
    
    if files_removed > 0:
        QMessageBox.information(
            self, "Files Removed", 
            f"{files_removed} file(s) removed successfully."
        )
        self._refresh_files_list()
        self.files_updated.emit()

def _remove_all_files(self):
    """Remove all files from the library"""
    files = self.llm_processor.get_files_list()
    
    if not files:
        QMessageBox.information(
            self, "No Files", 
            "There are no files to remove."
        )
        return
    
    result = QMessageBox.question(
        self, "Confirm Delete All", 
        f"Are you sure you want to delete ALL {len(files)} file(s)?\n\n"
        "This action cannot be undone.",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if result != QMessageBox.Yes:
        return
    
    files_removed = 0
    
    for filename in files:
        file_path = os.path.join(self.files_dir, filename)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                files_removed += 1
        except Exception as e:
            QMessageBox.warning(
                self, "File Error", 
                f"Error removing file '{filename}': {str(e)}"
            )
    
    if files_removed > 0:
        QMessageBox.information(
            self, "All Files Removed", 
            f"All {files_removed} file(s) removed successfully."
        )
        self._refresh_files_list()
        self.files_updated.emit()

def _on_selection_changed(self):
    """Handle files list selection changes"""
    selected_items = self.files_list.selectedItems()
    has_valid_selection = False
    
    for item in selected_items:
        if item.data(Qt.UserRole) != "no_files":
            has_valid_selection = True
            break
            
    self.remove_file_btn.setEnabled(has_valid_selection)
