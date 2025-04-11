#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Files Page Processing
Contains processing-related functionality for the Files Page
"""

from PySide6.QtWidgets import (
    QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QTimer, QCoreApplication
import os

from gui.styles import COLORS

def _process_files(self):
    """Process all files in the library with rate limiting"""
    files = self.llm_processor.get_files_list()
    
    if not files:
        QMessageBox.information(
            self, "No Files", 
            "No files available to process. Please add files first."
        )
        return
    
    result = QMessageBox.question(
        self, "Confirm Processing", 
        f"Process {len(files)} file(s) with the LLM?\n\n"
        "This may take some time and could incur API usage charges.\n\n"
        f"A {self.rate_limit_delay}-second delay will be added between files to avoid API rate limits.",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if result != QMessageBox.Yes:
        return
    
    # Disable UI during processing
    self._set_processing_state(True)
    
    try:
        # Start the rate-limited processing
        self.processing_files = files
        self.current_file_index = 0
        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)
        
        # Process the first file immediately
        self._process_next_file()
        
    except Exception as e:
        QMessageBox.critical(
            self, "Processing Error", 
            f"An error occurred during processing: {str(e)}"
        )
        self._set_processing_state(False)

def _process_next_file(self):
    """Process the next file in the queue, with rate limiting"""
    if self.current_file_index >= len(self.processing_files):
        # All files processed
        QMessageBox.information(
            self, "Processing Complete", 
            "All files have been processed successfully.\n\n"
            "You can view the results in the Live Output tab."
        )
        self._set_processing_state(False)
        return
    
    # Get the current file
    filename = self.processing_files[self.current_file_index]
    file_path = os.path.join(self.files_dir, filename)
    
    # Update UI
    self.progress_bar.setValue(self.current_file_index + 1)
    self.progress_bar.setFormat(f"{int((self.current_file_index + 1)/len(self.processing_files)*100)}% "
                                 f"({self.current_file_index + 1} of {len(self.processing_files)} files)")
    
    # Process the file
    try:
        result = self.llm_processor.process_file(file_path)
        
        # Move to the next file with rate limiting
        self.current_file_index += 1
        
        if self.current_file_index < len(self.processing_files):
            # Create countdown dialog
            self.show_countdown_dialog()
        else:
            # All files processed
            QMessageBox.information(
                self, "Processing Complete", 
                "All files have been processed successfully.\n\n"
                "You can view the results in the Live Output tab."
            )
            self._set_processing_state(False)
    
    except Exception as e:
        QMessageBox.warning(
            self, "File Processing Error", 
            f"Error processing file '{filename}': {str(e)}\n\n"
            "Continuing with next file..."
        )
        self.current_file_index += 1
        
        if self.current_file_index < len(self.processing_files):
            self.show_countdown_dialog()
        else:
            QMessageBox.information(
                self, "Processing Complete", 
                "Finished processing files with some errors.\n\n"
                "You can view the successful results in the Live Output tab."
            )
            self._set_processing_state(False)

def show_countdown_dialog(self):
    """Show countdown dialog between files"""
    # Create progress dialog for countdown with Apple-style
    self.countdown_dialog = QProgressDialog(
        f"Waiting {self.rate_limit_delay} seconds before processing next file...",
        "Skip Wait", 0, self.rate_limit_delay, self
    )
    self.countdown_dialog.setWindowTitle("API Rate Limit")
    self.countdown_dialog.setWindowModality(Qt.WindowModal)
    self.countdown_dialog.setCancelButton(None)  # No cancel button
    self.countdown_dialog.setMinimumWidth(400)
    self.countdown_dialog.setAutoClose(False)
    self.countdown_dialog.setAutoReset(False)
    self.countdown_dialog.setStyleSheet(f"""
        QProgressDialog {{
            background-color: {COLORS["frosted_bg"]};
            border: 1px solid {COLORS["frosted_border"]};
            border-radius: 10px;
            padding: 20px;
        }}
        QProgressBar {{
            background-color: rgba(229, 229, 229, 0.7);
            border: none;
            border-radius: 4px;
            text-align: center;
            min-height: 12px;
        }}
        QProgressBar::chunk {{
            background-color: {COLORS["accent"]};
            border-radius: 4px;
        }}
        QPushButton {{
            background-color: {COLORS["accent"]};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }}
    """)
    
    # Start countdown
    self.countdown_seconds = self.rate_limit_delay
    self.countdown_dialog.setValue(0)
    self.countdown_dialog.setLabelText(f"Waiting {self.countdown_seconds} seconds before processing next file...")
    
    # Create timer for countdown
    self.countdown_timer = QTimer(self)
    self.countdown_timer.timeout.connect(self._update_countdown)
    self.countdown_timer.start(1000)  # 1 second interval
    
    # Show dialog
    self.countdown_dialog.show()

def _update_countdown(self):
    """Update the countdown dialog"""
    self.countdown_seconds -= 1
    self.countdown_dialog.setValue(self.rate_limit_delay - self.countdown_seconds)
    self.countdown_dialog.setLabelText(f"Waiting {self.countdown_seconds} seconds before processing next file...")
    
    if self.countdown_seconds <= 0:
        # Stop timer
        self.countdown_timer.stop()
        self.countdown_dialog.close()
        
        # Process next file
        self._process_next_file()

def _update_progress(self, current, total, result):
    """Update progress bar during file processing"""
    self.progress_bar.setMaximum(total)
    self.progress_bar.setValue(current)
    self.progress_bar.setFormat(f"{int(current/total*100)}% ({current} of {total} files)")
    
    # Update application to show progress
    QCoreApplication.processEvents()

def _set_processing_state(self, is_processing):
    """Set UI state during processing"""
    self.add_file_btn.setEnabled(not is_processing)
    self.remove_file_btn.setEnabled(not is_processing)
    self.remove_all_btn.setEnabled(not is_processing)
    self.refresh_btn.setEnabled(not is_processing)
    self.process_btn.setEnabled(not is_processing)
    self.files_list.setEnabled(not is_processing)
    self.delay_spinner.setEnabled(not is_processing)
    self.delay_slider.setEnabled(not is_processing)
