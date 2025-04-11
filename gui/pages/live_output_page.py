#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Live Output Page
Display LLM outputs in real-time and extracted data tables
"""

import os
import re
import shutil
import pandas as pd
import csv # Added for CSV export
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGroupBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QFrame, QSplitter,
    QTabWidget, QFileDialog, QProgressDialog, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

class LiveOutputPage(QWidget):
    """Live output display page"""

    def __init__(self, llm_processor):
        """Initialize live output page"""
        super().__init__()

        self.llm_processor = llm_processor
        self.output_dir = llm_processor.output_dir
        self.outputs_dir = llm_processor.outputs_dir
        self.merged_output_file = llm_processor.merged_output_file

        # Default delay in seconds
        self.rate_limit_delay = 10

        # Keep track of last monitored file modification times
        self.last_file_mods = {}

        # Reference to the currently displayed table widget for export
        self.current_mega_table = None

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # Page title
        title_label = QLabel("Live Output")
        title_font = title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "View the results of LLM processing in real-time. The outputs include raw responses and "
            "extracted data tables from CSV format code blocks. All tables are merged into a single comprehensive table."
        )
        desc_label.setWordWrap(True)
        self.layout.addWidget(desc_label)

        # Process files section with controls
        process_group = QGroupBox("Process Files")
        process_layout = QVBoxLayout(process_group)

        # Rate limit delay control
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Delay between files (seconds):")
        delay_layout.addWidget(delay_label)

        self.delay_spinner = QSpinBox()
        self.delay_spinner.setMinimum(1)
        self.delay_spinner.setMaximum(60)
        self.delay_spinner.setValue(self.rate_limit_delay)
        self.delay_spinner.setMinimumWidth(80)
        self.delay_spinner.valueChanged.connect(self._update_delay)
        delay_layout.addWidget(self.delay_spinner)

        delay_layout.addStretch()
        process_layout.addLayout(delay_layout)

        # Process button
        self.process_btn = QPushButton("Process All Files")
        self.process_btn.setMinimumHeight(40)
        self.process_btn.setStyleSheet("background-color: #d4edda; color: #155724; font-weight: bold;")
        process_layout.addWidget(self.process_btn)

        self.layout.addWidget(process_group)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)

        # Tabs for different views
        self.tabs = QTabWidget()

        # Raw output tab
        self.raw_output_tab = QWidget()
        raw_layout = QVBoxLayout(self.raw_output_tab)

        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setLineWrapMode(QTextEdit.WidgetWidth)
        raw_layout.addWidget(self.output_text)

        # Buttons for raw output
        raw_buttons_layout = QHBoxLayout()

        # Refresh button
        self.refresh_btn = QPushButton("Refresh Output")
        self.refresh_btn.setMinimumHeight(40)
        raw_buttons_layout.addWidget(self.refresh_btn)

        # Export button
        self.export_btn = QPushButton("Export Output")
        self.export_btn.setMinimumHeight(40)
        raw_buttons_layout.addWidget(self.export_btn)

        # Clear display button
        self.clear_btn = QPushButton("Clear Display")
        self.clear_btn.setMinimumHeight(40)
        raw_buttons_layout.addWidget(self.clear_btn)

        # Clear ALL records button
        self.clear_records_btn = QPushButton("Clear All Records")
        self.clear_records_btn.setMinimumHeight(40)
        self.clear_records_btn.setStyleSheet("background-color: #f8d7da; color: #721c24;")
        raw_buttons_layout.addWidget(self.clear_records_btn)

        raw_layout.addLayout(raw_buttons_layout)

        # Tables tab
        self.tables_tab = QWidget()
        tables_layout = QVBoxLayout(self.tables_tab)

        # Table extraction info
        table_info = QLabel(
            "This tab displays tables extracted from CSV data in code blocks. "
            "ALL tables are merged into a SINGLE comprehensive table regardless of headers. "
            "The 'MODEL_ID' used for processing each section is included in the merged table.\n"
            "To have tables appear here, have the LLM provide data in a code block like:\n\n"
            "```csv\nheader1,header2,header3\nvalue1,value2,value3\n```\n\n"
            "Tables will be automatically extracted and merged into one comprehensive view."
        )
        table_info.setWordWrap(True)
        tables_layout.addWidget(table_info)

        # Table container (will be populated dynamically)
        self.table_container = QVBoxLayout()
        tables_layout.addLayout(self.table_container)

        # Add Export Table Button
        self.export_table_btn = QPushButton("Export Merged Table to CSV")
        self.export_table_btn.setMinimumHeight(40)
        self.export_table_btn.setEnabled(False) # Initially disabled
        tables_layout.addWidget(self.export_table_btn)

        tables_layout.addStretch()

        # Add tabs to tabwidget
        self.tabs.addTab(self.raw_output_tab, "Raw Output")
        self.tabs.addTab(self.tables_tab, "Extracted Tables")

        self.layout.addWidget(self.tabs, 1)  # 1 = stretch factor

        # Auto-refresh checkbox
        self.auto_refresh_layout = QHBoxLayout()
        self.auto_refresh_label = QLabel("Auto-refresh interval (seconds):")
        self.auto_refresh_layout.addWidget(self.auto_refresh_label)

        # Auto-refresh radio buttons
        self.off_btn = QPushButton("Off")
        self.off_btn.setCheckable(True)
        self.off_btn.setChecked(True)
        self.off_btn.setMaximumWidth(60)

        self.interval_5s = QPushButton("5s")
        self.interval_5s.setCheckable(True)
        self.interval_5s.setMaximumWidth(60)

        self.interval_15s = QPushButton("15s")
        self.interval_15s.setCheckable(True)
        self.interval_15s.setMaximumWidth(60)

        self.interval_30s = QPushButton("30s")
        self.interval_30s.setCheckable(True)
        self.interval_30s.setMaximumWidth(60)

        self.auto_refresh_layout.addWidget(self.off_btn)
        self.auto_refresh_layout.addWidget(self.interval_5s)
        self.auto_refresh_layout.addWidget(self.interval_15s)
        self.auto_refresh_layout.addWidget(self.interval_30s)
        self.auto_refresh_layout.addStretch()

        self.layout.addLayout(self.auto_refresh_layout)

        # Set up the timer for auto-refresh
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_output)

        # Connect signals
        self.refresh_btn.clicked.connect(self._refresh_output)
        self.export_btn.clicked.connect(self._export_output)
        self.export_table_btn.clicked.connect(self._export_merged_table) # Connect new button
        self.clear_btn.clicked.connect(self._clear_display)
        self.clear_records_btn.clicked.connect(self._clear_all_records)
        self.process_btn.clicked.connect(self._process_all_files)

        self.off_btn.clicked.connect(lambda: self._set_refresh_interval(0))
        self.interval_5s.clicked.connect(lambda: self._set_refresh_interval(5))
        self.interval_15s.clicked.connect(lambda: self._set_refresh_interval(15))
        self.interval_30s.clicked.connect(lambda: self._set_refresh_interval(30))

        # Initial refresh
        self._refresh_output()

    def _update_delay(self, value):
        """Update the rate limit delay"""
        self.rate_limit_delay = value

    def _process_all_files(self):
        """Process all files in the files directory"""
        files = self.llm_processor.get_files_list()

        if not files:
            QMessageBox.information(
                self, "No Files",
                "No files available to process. Please add files in the Files tab first."
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

        progress = QProgressDialog("Processing files...", "Cancel", 0, len(files), self)
        progress.setWindowTitle("Processing Files")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(True)
        progress.setAutoReset(True)

        def update_progress(current, total, result):
            if progress.wasCanceled():
                return False

            progress.setValue(current)
            progress.setLabelText(f"Processing file {current} of {total}...\n\n{result.get('filename', '')}")

            if current < total:
                progress.setLabelText(f"Processed file {current} of {total}.\n\n"
                                     f"Waiting {self.rate_limit_delay} seconds before next file...")
                for i in range(self.rate_limit_delay):
                    if progress.wasCanceled():
                        return False
                    progress.setLabelText(f"Processed file {current} of {total}.\n\n"
                                         f"Waiting {self.rate_limit_delay - i} seconds before next file...")
                    from PySide6.QtCore import QCoreApplication
                    QCoreApplication.processEvents()
                    import time
                    time.sleep(1)
            return True

        try:
            old_delay = getattr(self.llm_processor, 'rate_limit_delay', None)
            self.llm_processor.rate_limit_delay = self.rate_limit_delay
            results = self.llm_processor.process_all_files(update_progress)
            if old_delay is not None:
                self.llm_processor.rate_limit_delay = old_delay

            if progress.wasCanceled():
                QMessageBox.information(
                    self, "Processing Canceled",
                    "File processing was canceled."
                )
            else:
                QMessageBox.information(
                    self, "Processing Complete",
                    f"All {len(files)} file(s) have been processed successfully."
                )
                self._refresh_output()
        except Exception as e:
            QMessageBox.critical(
                self, "Processing Error",
                f"An error occurred during processing: {str(e)}"
            )
        finally:
            progress.close()

    def _set_refresh_interval(self, seconds):
        """Set auto-refresh interval"""
        self.off_btn.setChecked(seconds == 0)
        self.interval_5s.setChecked(seconds == 5)
        self.interval_15s.setChecked(seconds == 15)
        self.interval_30s.setChecked(seconds == 30)

        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        if seconds > 0:
            self.refresh_timer.start(seconds * 1000)

    def _refresh_output(self):
        """Refresh the output display"""
        try:
            self.output_text.clear()
            self.current_mega_table = None # Reset table reference
            self.export_table_btn.setEnabled(False) # Disable export button

            if os.path.exists(self.merged_output_file):
                with open(self.merged_output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.output_text.setPlainText(content)
                    self._extract_and_merge_all_tables(content) # This will update self.current_mega_table
            else:
                self.output_text.setPlainText("No output available yet. Process files to see results.")
                self._clear_table_display() # Clear table display if no output file

        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing output: {str(e)}")
            self._clear_table_display()

    def _clear_table_display(self):
        """Clears the table display area"""
        self.current_mega_table = None
        self.export_table_btn.setEnabled(False)
        while self.table_container.count():
            item = self.table_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # Add "no tables" message
        no_tables_label = QLabel(
            "No tables found in code blocks or merged output is empty.\n"
            "To create tables, ask the LLM to format data as CSV in code blocks:\n\n"
            "```csv\nheader1,header2,header3\nvalue1,value2,value3\n```"
        )
        no_tables_label.setWordWrap(True)
        no_tables_label.setAlignment(Qt.AlignCenter)
        no_tables_label.setStyleSheet("color: gray;")
        self.table_container.addWidget(no_tables_label)

    def _extract_and_merge_all_tables(self, content):
        """Extract ALL CSV tables from code blocks and merge them into ONE table, including model_id"""
        self._clear_table_display() # Clear previous table first

        # Regular expression to identify section headers
        # Updated to match MODEL_ID: instead of MODEL:
        section_header_pattern = r"={50}\nFILE: (.*)\nTIMESTAMP: (.*)\nAPI_TYPE: (.*)\nMODEL_ID: (.*)\n={50}"
        
        # Find all section headers
        section_headers = re.finditer(section_header_pattern, content)
        
        # Store the positions and model IDs of all section headers
        sections = []
        for match in section_headers:
            sections.append({
                'start_pos': match.start(),
                'end_pos': match.end(),
                'file': match.group(1).strip(),
                'timestamp': match.group(2).strip(),
                'api_type': match.group(3).strip(),
                'model_id': match.group(4).strip()  # Extract the model ID directly
            })
        
        # Add a virtual end section to simplify processing
        if content:
            sections.append({
                'start_pos': len(content),
                'end_pos': len(content),
                'file': None,
                'timestamp': None,
                'api_type': None,
                'model_id': None
            })
        
        all_tables_data = [] # List to hold {'model_id': ..., 'headers': [...], 'rows': [[...], ...]}
        
        # Process each section's content
        for i in range(len(sections) - 1):
            current_section = sections[i]
            next_section = sections[i + 1]
            
            # Get the content between the end of this section header and the start of the next
            section_content = content[current_section['end_pos']:next_section['start_pos']]
            
            # Extract model ID directly from the current section header
            current_model_id = current_section['model_id']
            
            # Process this section's content with the correct model ID
            self._process_content_section(section_content, current_model_id, all_tables_data)
        
        # Process any content before the first section header
        if sections and sections[0]['start_pos'] > 0:
            pre_content = content[:sections[0]['start_pos']]
            if pre_content.strip():  # Only process if there's actual content
                self._process_content_section(pre_content, "N/A", all_tables_data)

        # Create single mega-table from all collected table data
        if all_tables_data:
            # Create a groupbox for the mega table
            table_box = QGroupBox("Comprehensive Merged Table")
            table_layout = QVBoxLayout(table_box)

            # Get all unique headers from all tables AND add MODEL_ID
            all_headers = []
            for table_data in all_tables_data:
                for header in table_data['headers']:
                    if header not in all_headers:
                        all_headers.append(header)

            # Add MODEL_ID header if not already present
            if 'MODEL_ID' not in all_headers:
                all_headers.append('MODEL_ID')

            # Ensure MODEL_ID is the last column for consistency
            if 'MODEL_ID' in all_headers:
                 all_headers.remove('MODEL_ID')
                 all_headers.append('MODEL_ID')

            # Create QTableWidget
            mega_table = QTableWidget()
            mega_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only

            # Set headers for mega table
            mega_table.setColumnCount(len(all_headers))
            mega_table.setHorizontalHeaderLabels(all_headers)

            # Collect all rows from all tables
            all_rows = []
            model_id_col_index = all_headers.index('MODEL_ID') # Get index for MODEL_ID

            total_rows = 0
            for table_data in all_tables_data:
                model_id_for_table = table_data['model_id']
                for row in table_data['rows']:
                    # Create a row with values aligned to the mega table headers
                    mega_row = [""] * len(all_headers)
                    for i, header in enumerate(table_data['headers']):
                        if i < len(row) and header in all_headers:
                            header_index = all_headers.index(header)
                            mega_row[header_index] = row[i]

                    # Add the model_id specific to this table's section
                    mega_row[model_id_col_index] = model_id_for_table

                    all_rows.append(mega_row)
                    total_rows += 1

            # Set rows in mega table
            mega_table.setRowCount(len(all_rows))
            for i, row in enumerate(all_rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value)) # Ensure value is string
                    mega_table.setItem(i, j, item)

            # Resize to content
            mega_table.resizeColumnsToContents()
            mega_table.resizeRowsToContents()

            # Store reference and enable export
            self.current_mega_table = mega_table
            self.export_table_btn.setEnabled(True)

            # Add table to layout
            table_layout.addWidget(mega_table)
            # Clear the placeholder message before adding the table box
            while self.table_container.count():
                 item = self.table_container.takeAt(0)
                 widget = item.widget()
                 if widget: widget.deleteLater()
            self.table_container.addWidget(table_box)

            # Add summary of source tables
            summary_label = QLabel(f"Merged data from {len(all_tables_data)} source tables sections, total {total_rows} rows.")
            summary_label.setStyleSheet("font-style: italic; color: gray;")
            table_layout.addWidget(summary_label)
        else:
            # If no tables found after processing all sections
            self._clear_table_display() # Ensure placeholder is shown

    def _process_content_section(self, section_content, model_id, all_tables_data):
        """Processes a single section of content to find CSV tables"""
        if not section_content:
            return

        # Primarily focus on code blocks
        code_block_pattern = r'```(?:csv)?\s*((?:[^\n]+(?:,|\t)[^\n]+(?:\n|$))+)\s*```' # Ensure comma or tab exists
        matches = re.finditer(code_block_pattern, section_content, re.MULTILINE)

        found_in_section = False
        for match in matches:
            csv_content = match.group(1).strip()
            if not csv_content or csv_content.count('\n') < 1: continue # Need header + 1 row

            try:
                rows = csv_content.strip().split('\n')
                separator = '\t' if '\t' in rows[0] else ','
                headers = [h.strip('"\' ') for h in rows[0].split(separator)] # Strip quotes and spaces
                if not headers: continue

                table_rows = []
                for row_str in rows[1:]:
                    values = row_str.split(separator)
                    clean_values = [val.strip().strip('"\' ') for val in values]
                    # Allow rows with fewer columns than headers, padding with empty strings
                    if len(clean_values) < len(headers):
                        clean_values.extend([""] * (len(headers) - len(clean_values)))
                    table_rows.append(clean_values[:len(headers)]) # Truncate if too long

                if table_rows: # Only add if there are data rows
                    all_tables_data.append({
                        'model_id': model_id,
                        'headers': headers,
                        'rows': table_rows
                    })
                    found_in_section = True
            except Exception as e:
                print(f"Error parsing CSV content in section (model: {model_id}): {e}")
                continue

        # Secondary pattern - "CSV Output:" (only if no code blocks found in this section)
        if not found_in_section:
            csv_marker_pattern = r'CSV Output:\s*((?:[^\n]+(?:,|\t)[^\n]+(?:\n|$))+)'
            matches = re.finditer(csv_marker_pattern, section_content, re.MULTILINE)
            for match in matches:
                csv_content = match.group(1).strip()
                if not csv_content or csv_content.count('\n') < 1: continue

                try:
                    rows = csv_content.strip().split('\n')
                    separator = '\t' if '\t' in rows[0] else ','
                    headers = [h.strip('"\' ') for h in rows[0].split(separator)]
                    if not headers: continue

                    table_rows = []
                    for row_str in rows[1:]:
                         values = row_str.split(separator)
                         clean_values = [val.strip().strip('"\' ') for val in values]
                         if len(clean_values) < len(headers):
                             clean_values.extend([""] * (len(headers) - len(clean_values)))
                         table_rows.append(clean_values[:len(headers)])

                    if table_rows:
                        all_tables_data.append({
                            'model_id': model_id,
                            'headers': headers,
                            'rows': table_rows
                        })
                except Exception as e:
                    print(f"Error parsing CSV Output: content in section (model: {model_id}): {e}")
                    continue

    def _export_output(self):
        """Export the raw output text to a file"""
        try:
            if not self.output_text.toPlainText():
                QMessageBox.information(self, "No Output", "There's no raw output text to export.")
                return

            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter("Text Files (*.txt);;All Files (*.*)")
            file_dialog.setDefaultSuffix("txt")
            file_dialog.setWindowTitle("Export Raw Output")
            file_dialog.setDirectory(os.path.expanduser("~")) # Default to home directory
            file_dialog.selectFile("llm_raw_output_export.txt") # Suggest a filename

            if file_dialog.exec():
                file_path = file_dialog.selectedFiles()[0]
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.toPlainText())
                QMessageBox.information(
                    self, "Export Complete",
                    f"Raw output has been exported to:\n{file_path}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting raw output: {str(e)}")

    def _export_merged_table(self):
        """Export the merged table data to a CSV file"""
        if not self.current_mega_table:
            QMessageBox.information(self, "No Table Data", "There is no merged table data to export.")
            return

        try:
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter("CSV Files (*.csv)")
            file_dialog.setDefaultSuffix("csv")
            file_dialog.setWindowTitle("Export Merged Table")
            file_dialog.setDirectory(os.path.expanduser("~"))
            file_dialog.selectFile("merged_table_export.csv")

            if file_dialog.exec():
                file_path = file_dialog.selectedFiles()[0]

                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    # Write headers
                    headers = [self.current_mega_table.horizontalHeaderItem(j).text()
                               for j in range(self.current_mega_table.columnCount())]
                    writer.writerow(headers)

                    # Write data rows
                    for i in range(self.current_mega_table.rowCount()):
                        row_data = []
                        for j in range(self.current_mega_table.columnCount()):
                            item = self.current_mega_table.item(i, j)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)

                QMessageBox.information(
                    self, "Export Complete",
                    f"Merged table data has been exported to:\n{file_path}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting merged table: {str(e)}")

    def _clear_display(self):
        """Clear the output display (not the actual files)"""
        self.output_text.clear()
        self._clear_table_display() # Use the dedicated function

    def _clear_all_records(self):
        """Clear all output records (the actual files)"""
        try:
            result = QMessageBox.question(
                self, "Clear All Records",
                "Are you sure you want to delete ALL output records?\n\n"
                "This will permanently delete all outputs, prompts, and the merged output file.\n"
                "This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if result != QMessageBox.Yes:
                return

            dirs_to_clear = [
                self.outputs_dir,
                self.llm_processor.prompts_dir,
                self.llm_processor.messages_dir
            ]

            for directory in dirs_to_clear:
                if os.path.exists(directory):
                    # Use shutil.rmtree for efficiency, recreate after
                    try:
                        shutil.rmtree(directory)
                        os.makedirs(directory) # Recreate empty dir
                    except Exception as dir_e:
                        print(f"Could not fully clear directory {directory}: {dir_e}")
                        # Fallback to file-by-file deletion if needed
                        for file in os.listdir(directory):
                            file_path = os.path.join(directory, file)
                            try:
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                            except Exception as file_e:
                                print(f"Could not remove file {file_path}: {file_e}")

            # Clear merged output file
            if os.path.exists(self.merged_output_file):
                try:
                    with open(self.merged_output_file, 'w', encoding='utf-8') as f:
                        f.write("") # Overwrite with empty content
                except Exception as merge_e:
                    print(f"Could not clear merged output file {self.merged_output_file}: {merge_e}")

            self._refresh_output() # Refresh display

            QMessageBox.information(
                self, "Records Cleared",
                "All output records have been successfully deleted."
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"An error occurred while clearing records: {str(e)}"
            )
