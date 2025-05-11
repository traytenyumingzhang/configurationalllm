#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Worker for threaded processing of files by LLM.
"""

from PySide6.QtCore import QObject, QRunnable, Signal
import traceback

class WorkerSignals(QObject):
    """
    Defines signals available from a running worker thread.
    Supported signals are:
    - progress: (int, int, int, int, str, int) -> current_file_num, total_files, current_iter, total_iters, current_file_name, overall_progress_percent
    - finished: (str, str) -> message, error_details (None if no error)
    - error: (str) -> error_message (for critical, unhandled errors in worker run)
    """
    progress = Signal(int, int, int, int, str, int)
    finished = Signal(str, str) 
    error = Signal(str)


class ProcessingWorker(QRunnable):
    """
    Worker thread for processing files.
    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    """
    def __init__(self, llm_processor, file_paths, num_iterations, delay_seconds):
        super().__init__()
        self.llm_processor = llm_processor
        self.file_paths = file_paths
        self.num_iterations = num_iterations
        self.delay_seconds = delay_seconds
        self.signals = WorkerSignals()
        self._is_cancelled = False # Internal flag for cancellation

    def run(self):
        """Execute the processing task."""
        try:
            self.llm_processor.process_files_iteratively(
                file_paths_to_process=self.file_paths,
                num_iterations=self.num_iterations,
                delay_seconds=self.delay_seconds,
                progress_callback=self._emit_progress_and_check_cancel,
                completion_callback=self._emit_finished
            )
        except Exception as e:
            error_msg = f"Unhandled error in processing worker: {e}"
            print(error_msg)
            traceback.print_exc()
            self.signals.error.emit(error_msg)
            # Also emit finished with error details to ensure UI cleanup
            self.signals.finished.emit("Processing failed with unhandled error.", error_msg)

    def _emit_progress_and_check_cancel(self, current_file_num, total_files, current_iter, total_iters, current_file_name, overall_progress_percent):
        """Emits progress signal and checks for cancellation. Returns False if cancelled."""
        if self._is_cancelled:
            return False # Signal to LLMProcessor to stop
        self.signals.progress.emit(current_file_num, total_files, current_iter, total_iters, current_file_name, overall_progress_percent)
        return True # Continue processing

    def _emit_finished(self, message, error_details):
        """Emits the finished signal."""
        self.signals.finished.emit(message, error_details)
    
    def cancel(self):
        """Requests cancellation of the processing task."""
        print("Processing cancellation requested for worker.")
        self._is_cancelled = True
        # Cancellation is checked by LLMProcessor via the return value of _emit_progress_and_check_cancel
