import logging

import qdarktheme
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QMainWindow,
    QWidget,
    QProgressDialog,
)

from gui_progress_handler import ProgressHandler


class FileTransferClientGUI(QMainWindow):
    """A GUI application for transferring files using PyQt6."""

    _send_progress_dialog: QProgressDialog = None

    def __init__(self):
        """Initializes the FileTransferClientGUI class."""
        super().__init__()
        self._init_ui()

        self._suppress_progress_warning = False
        self.show()

    def _init_ui(self) -> None:
        """Initializes the user interface."""
        qdarktheme.setup_theme(custom_colors={"primary": "#d79df1"})

        self.setWindowTitle("File Transfer Client")
        self.setFixedSize(300, 300)

        self.main_widget = QWidget(self)
        layout = QVBoxLayout()

        self._file_label = QLabel("File:", self.main_widget)
        self._file_input = QLineEdit(self.main_widget)
        self._file_input.textChanged.connect(lambda _: self._handle_button_state())

        self._browse_button = QPushButton("Browse", self.main_widget)
        self._browse_button.clicked.connect(self._browse_file)

        self._host_label = QLabel("Host:", self.main_widget)
        self._host_input = QLineEdit(self.main_widget)
        self._host_input.setPlaceholderText("127.0.0.1 or example.com")
        self._host_input.textChanged.connect(lambda _: self._handle_button_state())

        self._port_label = QLabel("Port:", self.main_widget)
        self._port_input = QLineEdit(self.main_widget)
        self._port_input.setPlaceholderText("12345")
        self._port_input.textChanged.connect(lambda _: self._handle_button_state())

        self._send_button = QPushButton("Send", self.main_widget)
        self._send_button.clicked.connect(self._handle_button_click)
        self._send_button.setDisabled(True)

        self._file_input.returnPressed.connect(self._send_button.click)
        self._host_input.returnPressed.connect(self._send_button.click)
        self._port_input.returnPressed.connect(self._send_button.click)

        layout.addWidget(self._file_label)
        layout.addWidget(self._file_input)
        layout.addWidget(self._browse_button)
        layout.addWidget(self._host_label)
        layout.addWidget(self._host_input)
        layout.addWidget(self._port_label)
        layout.addWidget(self._port_input)
        layout.addWidget(self._send_button)

        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)

    def _browse_file(self) -> None:
        """
        Opens a file dialog to browse and select a file.

        Sets the selected file path in the file input line edit.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File")

        if file_name:
            self._file_input.setText(file_name)

    def _handle_button_state(self) -> None:
        """
        Enables or disables the send button based on the input fields.

        The send button is enabled only if the file, host, and port fields are not empty.
        """
        if (
            self._file_input.text()
            and self._host_input.text()
            and self._port_input.text()
        ):
            self._send_button.setEnabled(True)
        else:
            self._send_button.setDisabled(True)

    def _handle_button_click(self) -> None:
        """
        Handles the click event of the send button to send the selected file.

        Displays a progress dialog while the file transfer is in progress.
        """
        if not self._send_progress_dialog:
            self._init_progress_dialog()

        self._progress_handler.set_info_to_send(
            self._file_input.text(), self._host_input.text(), self._port_input.text()
        )
        self._progress_handler.start()

    def _init_progress_dialog(self):
        """Initializes the progress dialog. Sets handle functions for the progress dialog."""

        def __handle_progress_change(value) -> None:
            self._send_progress_dialog.setValue(value)

            if value == -1:
                self._send_progress_dialog.show()
                self._send_progress_dialog.cancel_button.setEnabled(True)
            elif value == 99:
                self._send_progress_dialog.cancel_button.setDisabled(True)
            elif value == 100:
                QMessageBox.information(self, "Success", "File sent successfully")

        def __handle_progress_error(error_text: str) -> None:
            self._suppress_progress_warning = True
            self._send_progress_dialog.close()
            logging.error(f"Failed to send file: {error_text}")
            QMessageBox.critical(self, "Error", f"Failed to send file: {error_text}")
            self._suppress_progress_warning = False

        def __handle_cancel_click() -> None:
            if self._suppress_progress_warning:
                return

            self._send_progress_dialog.hide()
            self._progress_handler.final_value = -1
            QMessageBox.warning(self, "Warning", "File transfer canceled")
            logging.warning("File transfer canceled")

        self._send_progress_dialog = QProgressDialog("", "Cancel", 0, 100, self)
        self._send_progress_dialog.setWindowTitle("Sending File")
        self._send_progress_dialog.setMinimumWidth(300)
        self._send_progress_dialog.setModal(True)
        self._send_progress_dialog.cancel_button = self._send_progress_dialog.findChild(
            QPushButton
        )

        self._progress_handler = ProgressHandler(self._send_progress_dialog)
        self._progress_handler.progress_change.connect(__handle_progress_change)
        self._progress_handler.error.connect(__handle_progress_error)
        self._send_progress_dialog.canceled.connect(__handle_cancel_click)

    def closeEvent(self, a0):
        logging.info("Closing client GUI...")
        self._suppress_progress_warning = True
        self._progress_handler.terminate()
        super().closeEvent(a0)
