from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QProgressDialog


class ProgressHandler(QThread):
    """A class to handle progress updates for a QProgressDialog."""

    def __init__(self, progress_dialog: QProgressDialog):
        """
        Initializes the ProgressHandler with a QProgressDialog.

        Args:
            progress_dialog (QProgressDialog): The progress dialog to update.
        """
        super().__init__()

        self._final_value: int = 0
        self._current_percent: float = 0
        self._previous_percent_int: int = 0
        self._progress_dialog = progress_dialog

    def set_goal(self, goal: int) -> None:
        """
        Sets the goal for the progress handler which is file size in bytes.

        Args:
            goal: The final value representing the completion goal.
        """
        self._final_value = goal
        self._current_percent = 0

    def update_progress(self, increment: int) -> None:
        """
        Updates the progress dialog based on the given increment.

        Args:
            increment: The amount to increment the progress by.

        Raises:
            InterruptedError: If the final value is -1, indicating the process was cancelled by the user.
        """
        if self._final_value == -1:
            raise InterruptedError("File transfer cancelled by user.")

        if self._current_percent == 0:
            self._current_percent += (
                increment / self._final_value * 100
            )  # function is not called for the last block, so we handle it at the start
            self._progress_dialog.show()

        self._current_percent += increment / self._final_value * 100
        new_percent_int = int(self._current_percent)

        if self._previous_percent_int != new_percent_int:
            self._progress_dialog.setValue(
                new_percent_int if new_percent_int < 100 else 100
            )  # trick to handle tiny files whose percent sometimes go crazy
            self._previous_percent_int = new_percent_int
