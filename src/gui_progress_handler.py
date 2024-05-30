from PyQt6.QtCore import QThread, pyqtSignal


class ProgressHandler(QThread):
    progress = pyqtSignal(int)
    _final_value: int = 0
    _current_percent: float = 0
    _previous_percent_int: int = 0

    def set_goal(self, goal: int) -> None:
        self._final_value = goal
        self._current_percent = 0

    def update_progress(self, increment: int) -> None:
        if self._final_value == -1:
            raise InterruptedError("File transfer cancelled by user.")
        if self._current_percent == 0:
            self._current_percent += increment / self._final_value * 100

        self._current_percent += increment / self._final_value * 100
        new_percent_int = int(self._current_percent)

        if self._previous_percent_int != new_percent_int:
            print(f"Current progress: {new_percent_int}%")
            self.progress.emit(
                new_percent_int if new_percent_int < 100 else 100
            )  # trick to handle tiny files whose percent sometimes go crazy
            self._previous_percent_int = new_percent_int
