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
import csv 
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGroupBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QFrame, QSplitter,
    QTabWidget, QFileDialog, QProgressBar 
)
from PySide6.QtCore import Qt, Signal, QTimer, QThreadPool
from PySide6.QtGui import QFont, QColor, QPalette

from ..processing_worker import ProcessingWorker, WorkerSignals

class LiveOutputPage(QWidget):
    """Live output display page"""

    def __init__(self, config_manager, llm_processor, main_window=None):
        super().__init__()

        self.config_manager = config_manager
        self.llm_processor = llm_processor
        self.main_window = main_window
        self.output_dir = llm_processor.output_dir
        self.outputs_dir = llm_processor.outputs_dir
        self.merged_output_file = llm_processor.merged_output_file
        self.processing_worker = None 

        self.last_file_mods = {}
        self.current_mega_table = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        title_label = QLabel("Live Output")
        title_font = title_label.font()
        title_font.setPointSize(18); title_font.setBold(True)
        title_label.setFont(title_font)
        self.layout.addWidget(title_label)

        desc_label = QLabel(
            "View the results of LLM processing. Raw responses are shown, and tables from CSV code blocks are extracted and merged. "
            "Configure processing parameters on the 'Processing Settings' page."
        )
        desc_label.setWordWrap(True)
        self.layout.addWidget(desc_label)

        process_controls_group = QFrame()
        process_controls_group.setObjectName("frosted_card")
        process_controls_layout = QVBoxLayout(process_controls_group)
        process_controls_layout.setContentsMargins(15,15,15,15); process_controls_layout.setSpacing(10)

        self.process_btn = QPushButton("Process All Files")
        self.process_btn.setMinimumHeight(45); self.process_btn.setObjectName("primary_button")
        self.process_btn.setStyleSheet("font-size: 15px; font-weight: bold;")
        process_controls_layout.addWidget(self.process_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0); self.progress_bar.setMaximum(100); self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True); self.progress_bar.setFormat("Not processing")
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: rgba(229, 229, 229, 0.7); border: none; border-radius: 8px;
                           text-align: center; color: rgba(0, 0, 0, 0.7); font-weight: bold;
                           min-height: 25px; font-size: 13px; padding: 0px 4px; }
            QProgressBar::chunk { background-color: #0071E3; border-radius: 8px; }
        """)
        process_controls_layout.addWidget(self.progress_bar)
        self.layout.addWidget(process_controls_group)

        separator = QFrame(); separator.setFrameShape(QFrame.HLine); separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)

        self.tabs = QTabWidget()
        self.raw_output_tab = QWidget()
        raw_layout = QVBoxLayout(self.raw_output_tab)
        self.output_text = QTextEdit(); self.output_text.setReadOnly(True)
        self.output_text.setLineWrapMode(QTextEdit.WidgetWidth)
        raw_layout.addWidget(self.output_text)
        
        raw_buttons_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Output"); self.refresh_btn.setMinimumHeight(40)
        raw_buttons_layout.addWidget(self.refresh_btn)
        self.export_btn = QPushButton("Export Output"); self.export_btn.setMinimumHeight(40)
        raw_buttons_layout.addWidget(self.export_btn)
        self.clear_btn = QPushButton("Clear Display"); self.clear_btn.setMinimumHeight(40)
        raw_buttons_layout.addWidget(self.clear_btn)
        self.clear_records_btn = QPushButton("Clear All Records"); self.clear_records_btn.setMinimumHeight(40)
        self.clear_records_btn.setStyleSheet("background-color: #f8d7da; color: #721c24;")
        raw_buttons_layout.addWidget(self.clear_records_btn)
        raw_layout.addLayout(raw_buttons_layout)

        self.tables_tab = QWidget()
        tables_layout = QVBoxLayout(self.tables_tab)
        table_info = QLabel(
            "This tab displays tables extracted from CSV data in code blocks. "
            "ALL tables are merged into a SINGLE comprehensive table. "
            "The 'MODEL_ID', 'MD5_Hash', and 'Iteration_Num' for each section are included.\n" # Updated info
            "To have tables appear here, have the LLM provide data in a code block like:\n\n"
            "```csv\nheader1,header2,header3\nvalue1,value2,value3\n```"
        )
        table_info.setWordWrap(True); tables_layout.addWidget(table_info)
        self.table_container = QVBoxLayout(); tables_layout.addLayout(self.table_container)
        self.export_table_btn = QPushButton("Export Merged Table to CSV"); self.export_table_btn.setMinimumHeight(40)
        self.export_table_btn.setEnabled(False); tables_layout.addWidget(self.export_table_btn)
        tables_layout.addStretch()

        self.tabs.addTab(self.raw_output_tab, "Raw Output")
        self.tabs.addTab(self.tables_tab, "Extracted Tables")
        self.layout.addWidget(self.tabs, 1)

        self.auto_refresh_layout = QHBoxLayout()
        self.auto_refresh_label = QLabel("Auto-refresh interval (seconds):")
        self.auto_refresh_layout.addWidget(self.auto_refresh_label)
        self.off_btn = QPushButton("Off"); self.off_btn.setCheckable(True); self.off_btn.setChecked(True); self.off_btn.setMaximumWidth(60)
        self.interval_5s = QPushButton("5s"); self.interval_5s.setCheckable(True); self.interval_5s.setMaximumWidth(60)
        self.interval_15s = QPushButton("15s"); self.interval_15s.setCheckable(True); self.interval_15s.setMaximumWidth(60)
        self.interval_30s = QPushButton("30s"); self.interval_30s.setCheckable(True); self.interval_30s.setMaximumWidth(60)
        for btn in [self.off_btn, self.interval_5s, self.interval_15s, self.interval_30s]: self.auto_refresh_layout.addWidget(btn)
        self.auto_refresh_layout.addStretch(); self.layout.addLayout(self.auto_refresh_layout)

        self.refresh_timer = QTimer(self); self.refresh_timer.timeout.connect(self._refresh_output)
        self.refresh_btn.clicked.connect(self._refresh_output)
        self.export_btn.clicked.connect(self._export_output)
        self.export_table_btn.clicked.connect(self._export_merged_table)
        self.clear_btn.clicked.connect(self._clear_display)
        self.clear_records_btn.clicked.connect(self._clear_all_records)
        self.process_btn.clicked.connect(self.start_processing_action)
        self.off_btn.clicked.connect(lambda: self._set_refresh_interval(0))
        self.interval_5s.clicked.connect(lambda: self._set_refresh_interval(5))
        self.interval_15s.clicked.connect(lambda: self._set_refresh_interval(15))
        self.interval_30s.clicked.connect(lambda: self._set_refresh_interval(30))

        self._refresh_output(); self.update_button_states()

    def start_processing_action(self):
        if self.processing_worker is not None and not QThreadPool.globalInstance().waitForDone(1):
            QMessageBox.warning(self, "Processing Busy", "A processing task is already running."); return
        files_to_process_names = self.llm_processor.get_files_list()
        if not files_to_process_names:
            QMessageBox.information(self, "No Files", "No files in library to process."); return
        num_iterations = self.config_manager.get_setting('num_iterations', 1)
        rate_limit_delay = self.config_manager.get_setting('rate_limit_delay', 5)
        confirm_msg = (f"Process {len(files_to_process_names)} file(s)?\n"
                       f"Iterations per file: {num_iterations}\n"
                       f"Delay per step: {rate_limit_delay}s\n\nThis may take time and incur API costs.")
        if QMessageBox.question(self, "Confirm Processing", confirm_msg, QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes: return
        self.update_button_states(is_processing=True)
        self.progress_bar.setValue(0); self.progress_bar.setFormat("Starting...")
        file_paths = [os.path.join(self.llm_processor.files_dir, name) for name in files_to_process_names]
        self.processing_worker = ProcessingWorker(self.llm_processor, file_paths, num_iterations, rate_limit_delay)
        self.processing_worker.signals.progress.connect(self._update_live_progress)
        self.processing_worker.signals.finished.connect(self._handle_processing_finished)
        self.processing_worker.signals.error.connect(self._handle_processing_error)
        QThreadPool.globalInstance().start(self.processing_worker)

    def _update_live_progress(self, cur_f, tot_f, cur_i, tot_i, f_name, progress_val):
        self.progress_bar.setValue(progress_val)
        self.progress_bar.setFormat(f"File {cur_f}/{tot_f} ({f_name}) - Iter. {cur_i}/{tot_i} - {progress_val}%")

    def _handle_processing_finished(self, message, error_details):
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat(message if not error_details else f"Completed with errors: {message}")
        if error_details: QMessageBox.warning(self, "Processing Finished with Errors", f"{message}\n\nDetails:\n{error_details}")
        else: QMessageBox.information(self, "Processing Finished", message)
        self._refresh_output(); self.processing_worker = None; self.update_button_states(is_processing=False)

    def _handle_processing_error(self, error_message):
        QMessageBox.critical(self, "Critical Processing Error", f"A critical error occurred:\n{error_message}")
        self.progress_bar.setFormat("Processing failed critically.")
        self.processing_worker = None; self.update_button_states(is_processing=False); self._refresh_output()

    def update_button_states(self, is_processing=None):
        if is_processing is None: is_processing = self.processing_worker is not None and not QThreadPool.globalInstance().waitForDone(1)
        self.process_btn.setEnabled(not is_processing)
        self.refresh_btn.setEnabled(not is_processing)
        self.export_btn.setEnabled(not is_processing and bool(self.output_text.toPlainText()))
        self.export_table_btn.setEnabled(not is_processing and self.current_mega_table is not None)
        self.clear_btn.setEnabled(not is_processing); self.clear_records_btn.setEnabled(not is_processing)
        for btn in [self.off_btn, self.interval_5s, self.interval_15s, self.interval_30s]: btn.setEnabled(not is_processing)

    def _set_refresh_interval(self, seconds):
        for btn, val in [(self.off_btn,0), (self.interval_5s,5), (self.interval_15s,15), (self.interval_30s,30)]: btn.setChecked(seconds == val)
        if self.refresh_timer.isActive(): self.refresh_timer.stop()
        if seconds > 0: self.refresh_timer.start(seconds * 1000)

    def _refresh_output(self):
        try:
            self.output_text.clear(); self.current_mega_table = None; self.export_table_btn.setEnabled(False)
            if os.path.exists(self.merged_output_file):
                with open(self.merged_output_file, 'r', encoding='utf-8') as f: content = f.read()
                self.output_text.setPlainText(content); self._extract_and_merge_all_tables(content)
            else:
                self.output_text.setPlainText("No output. Process files to see results."); self._clear_table_display()
            self.update_button_states()
        except Exception as e: QMessageBox.warning(self, "Refresh Error", f"Error: {e}"); self._clear_table_display()

    def _clear_table_display(self):
        self.current_mega_table = None; self.export_table_btn.setEnabled(False)
        while self.table_container.count():
            item = self.table_container.takeAt(0); widget = item.widget(); 
            if widget: widget.deleteLater()
        no_tables_label = QLabel("No tables found or merged output is empty.\nAsk LLM for CSV in code blocks: ```csv\nh1,h2\nv1,v2\n```")
        no_tables_label.setWordWrap(True); no_tables_label.setAlignment(Qt.AlignCenter)
        no_tables_label.setStyleSheet("color: gray;"); self.table_container.addWidget(no_tables_label)

    def _extract_and_merge_all_tables(self, content):
        self._clear_table_display()
        # Updated regex to capture MD5 and Iteration
        section_header_pattern = r"={50}\nFILE: (.*?)\nMD5: (.*?)\nITERATION: (.*?)\nTIMESTAMP: (.*?)\nAPI_TYPE: (.*?)\nMODEL_ID: (.*?)\n={50}"
        sections = []
        for match in re.finditer(section_header_pattern, content):
            sections.append({
                'start_pos': match.start(), 
                'end_pos': match.end(), 
                'md5': match.group(2).strip(), 
                'iteration': match.group(3).strip(), # Capture Iteration
                'model_id': match.group(6).strip()  # Group index adjusted for new capture group
            })
        if content and not sections: # Handle content that might not have full headers (e.g. old format or error output)
             sections.append({'start_pos': 0, 'end_pos': 0, 'md5': 'N/A', 'iteration': 'N/A', 'model_id': 'N/A'})


        if content: sections.append({'start_pos': len(content), 'end_pos': len(content), 'md5': None, 'iteration': None, 'model_id': None})
        
        all_tables_data = []
        for i in range(len(sections) -1):
            current_section = sections[i]
            section_content = content[current_section['end_pos']:sections[i+1]['start_pos']]
            self._process_content_section(section_content, current_section['model_id'], current_section['md5'], current_section['iteration'], all_tables_data)
        
        if not sections and content.strip(): # If no headers found at all, but there is content
             self._process_content_section(content, "N/A", "N/A", "N/A", all_tables_data)
        elif sections and sections[0]['start_pos'] > 0: # Content before first header
            self._process_content_section(content[:sections[0]['start_pos']], "N/A", "N/A", "N/A", all_tables_data)


        if all_tables_data:
            table_box = QGroupBox("Comprehensive Merged Table")
            table_layout = QVBoxLayout(table_box)
            all_headers = []
            for table_data in all_tables_data:
                for header in table_data['headers']:
                    if header not in all_headers: all_headers.append(header)
            
            special_headers = ['MODEL_ID', 'MD5_Hash', 'Iteration_Num'] # Added Iteration_Num
            for sp_header in special_headers:
                if sp_header not in all_headers: all_headers.append(sp_header)
            
            final_headers = [h for h in all_headers if h not in special_headers]
            final_headers.extend(special_headers) 

            mega_table = QTableWidget(); mega_table.setEditTriggers(QTableWidget.NoEditTriggers)
            mega_table.setColumnCount(len(final_headers)); mega_table.setHorizontalHeaderLabels(final_headers)
            
            all_rows_for_widget = []
            model_id_col_idx = final_headers.index('MODEL_ID')
            md5_col_idx = final_headers.index('MD5_Hash')
            iter_col_idx = final_headers.index('Iteration_Num') # Get index for Iteration_Num

            for table_data in all_tables_data:
                for row_values in table_data['rows']:
                    mega_row = [""] * len(final_headers)
                    for i, header in enumerate(table_data['headers']):
                        if i < len(row_values) and header in final_headers:
                            mega_row[final_headers.index(header)] = row_values[i]
                    mega_row[model_id_col_idx] = table_data['model_id']
                    mega_row[md5_col_idx] = table_data['md5'] 
                    mega_row[iter_col_idx] = table_data['iteration'] # Add Iteration data
                    all_rows_for_widget.append(mega_row)
            
            mega_table.setRowCount(len(all_rows_for_widget))
            for i, row_data in enumerate(all_rows_for_widget):
                for j, value in enumerate(row_data):
                    mega_table.setItem(i, j, QTableWidgetItem(str(value)))
            
            mega_table.resizeColumnsToContents(); mega_table.resizeRowsToContents()
            self.current_mega_table = mega_table; self.export_table_btn.setEnabled(True)
            
            while self.table_container.count():
                 item = self.table_container.takeAt(0)
                 if item.widget(): item.widget().deleteLater()
            self.table_container.addWidget(table_box); table_layout.addWidget(mega_table)
            summary_label = QLabel(f"Merged data from {len(all_tables_data)} source tables, total {len(all_rows_for_widget)} rows.")
            summary_label.setStyleSheet("font-style: italic; color: gray;"); table_layout.addWidget(summary_label)
        else: self._clear_table_display()

    def _process_content_section(self, section_content, model_id, md5_hash, iteration_num, all_tables_data): # Added iteration_num
        if not section_content: return
        code_block_pattern = r'```(?:csv)?\s*((?:[^\n]+(?:,|\t)[^\n]+(?:\n|$))+)\s*```'
        found_in_section = False
        for match in re.finditer(code_block_pattern, section_content, re.MULTILINE):
            csv_content = match.group(1).strip()
            if not csv_content or csv_content.count('\n') < 1: continue
            try:
                rows = csv_content.strip().split('\n')
                separator = '\t' if '\t' in rows[0] else ','
                headers = [h.strip('"\' ') for h in rows[0].split(separator)]
                if not headers: continue
                table_rows_data = [[val.strip().strip('"\' ') for val in r.split(separator)] for r in rows[1:]]
                for r_idx, r_vals in enumerate(table_rows_data):
                    if len(r_vals) < len(headers): table_rows_data[r_idx].extend([""] * (len(headers) - len(r_vals)))
                    table_rows_data[r_idx] = table_rows_data[r_idx][:len(headers)]
                if table_rows_data:
                    all_tables_data.append({'model_id': model_id, 'md5': md5_hash, 'iteration': iteration_num, 'headers': headers, 'rows': table_rows_data}) # Store iteration
                    found_in_section = True
            except Exception as e: print(f"Error parsing CSV (model: {model_id}, md5: {md5_hash}, iter: {iteration_num}): {e}")

    def _export_output(self):
        if not self.output_text.toPlainText(): QMessageBox.information(self, "No Output", "No text to export."); return
        path, _ = QFileDialog.getSaveFileName(self, "Export Raw Output", os.path.expanduser("~/llm_raw_output.txt"), "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f: f.write(self.output_text.toPlainText())
                QMessageBox.information(self, "Export Complete", f"Output exported to:\n{path}")
            except Exception as e: QMessageBox.critical(self, "Export Error", f"Error: {e}")

    def _export_merged_table(self):
        if not self.current_mega_table: QMessageBox.information(self, "No Table", "No table data to export."); return
        path, _ = QFileDialog.getSaveFileName(self, "Export Merged Table", os.path.expanduser("~/merged_llm_table.csv"), "CSV Files (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    headers = [self.current_mega_table.horizontalHeaderItem(j).text() for j in range(self.current_mega_table.columnCount())]
                    writer.writerow(headers)
                    for i in range(self.current_mega_table.rowCount()):
                        writer.writerow([self.current_mega_table.item(i,j).text() if self.current_mega_table.item(i,j) else "" for j in range(self.current_mega_table.columnCount())])
                QMessageBox.information(self, "Export Complete", f"Table exported to:\n{path}")
            except Exception as e: QMessageBox.critical(self, "Export Error", f"Error: {e}")

    def _clear_display(self): self.output_text.clear(); self._clear_table_display()

    def _clear_all_records(self):
        if QMessageBox.question(self, "Clear All Records", "Delete ALL output records permanently?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            try:
                dirs_to_clear = [self.outputs_dir, self.llm_processor.prompts_dir, self.llm_processor.messages_dir]
                for directory in dirs_to_clear:
                    if os.path.exists(directory): shutil.rmtree(directory); os.makedirs(directory)
                if os.path.exists(self.merged_output_file):
                    with open(self.merged_output_file, 'w', encoding='utf-8') as f: f.write("")
                if os.path.exists(self.llm_processor.summary_csv_file): 
                    os.remove(self.llm_processor.summary_csv_file)
                    self.llm_processor._initialize_csv() 
                self._refresh_output()
                QMessageBox.information(self, "Records Cleared", "All records deleted.")
            except Exception as e: QMessageBox.critical(self, "Error", f"Error clearing records: {e}")

    def enter_page(self): self._refresh_output(); self.update_button_states()
    def leave_page(self):
        if self.refresh_timer.isActive(): self.refresh_timer.stop()
