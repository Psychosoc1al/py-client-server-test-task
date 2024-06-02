from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QProgressDialog

import client_cli


class ProgressHandler(QThread):
    """A class to handle progress updates for a QProgressDialog."""

    progress_change = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, progress_dialog: QProgressDialog):
        """
        Initializes the ProgressHandler with a QProgressDialog.

        Args:
            progress_dialog: The progress dialog to update.
        """
        super().__init__()

        self._final_value: int = 0
        self._current_percent: float = 0
        self._previous_percent_int: int = 0
        self._progress_dialog = progress_dialog
        self._file_path: str = ""
        self._host: str = ""
        self._port: str = ""

    @property
    def final_value(self) -> int:
        """
        Gets the final value for the progress (file size in bytes currently).

        Returns:
            int: The final value for the progress.
        """
        return self._final_value

    @final_value.setter
    def final_value(self, value: int) -> None:
        """
        Sets the final value for the progress (file size in bytes currently).

        Args:
            value: The final value to be set.
        """
        self._final_value = value

    def set_info_to_send(self, file_path: str, host: str, port: str) -> None:
        """
        Sets the information required for sending the file.

        Args:
            file_path: The path to the file to be sent.
            host: The host to which the file will be sent.
            port: The port on the host to which the file will be sent.
        """
        self._file_path = file_path
        self._host = host
        self._port = port
        self._current_percent = 0

    def run(self) -> None:
        """Runs the file sending process in a separate thread."""
        try:
            client_cli.send_file(self._file_path, self._host, int(self._port), self)
        except Exception as e:
            self.error.emit(str(e))

    def update_progress(self, increment: int) -> bool:
        """
        Updates the progress bar of the file sending process.

        Args:
            increment: The increment to add to the current progress.

        Returns:
            True if the process of sending the file should continue, False otherwise.
        """
        if self._final_value == -1:
            return False
        if self._current_percent == 0:
            self.progress_change.emit(-1)

        self._current_percent += increment / self._final_value * 100
        new_percent_int = int(self._current_percent)

        if self._previous_percent_int != new_percent_int:
            self.progress_change.emit(
                min(new_percent_int, 99)
            )  # a trick to handle waiting the server response without closing the dialog
            self._previous_percent_int = new_percent_int

        return self._final_value != -1

    def finish(self) -> None:
        """Marks the progress as complete."""
        self.progress_change.emit(100)
