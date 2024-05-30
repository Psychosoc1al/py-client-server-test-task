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
    QApplication,
    QProgressDialog,
)

import client_cli
from gui_progress_handler import ProgressHandler


class FileTransferClientGUI(QMainWindow):
    """A GUI application for transferring files using PyQt6."""

    _send_progress_dialog: QProgressDialog = None

    def __init__(self):
        """Initializes the FileTransferClientGUI class."""
        super().__init__()
        self._init_ui()
        self._center_window()

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

    def _send_file(self) -> None:
        """
        Sends the selected file to the specified host and port.

        Displays a success or error message based on the result of the file transfer.
        """

        file_path = self._file_input.text()
        host = self._host_input.text()
        port = int(self._port_input.text())

        try:
            client_cli.send_file(file_path, host, port, self._progress_handler)

            QMessageBox.information(self, "Success", "File sent successfully")
        except InterruptedError as e:
            logging.warning(str(e))
            QMessageBox.warning(self, "Warning", str(e))
        except Exception as e:
            self._send_progress_dialog.close()
            logging.error(f"Failed to send file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to send file: {e}")

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
            self._send_progress_dialog = QProgressDialog("", "Cancel", 0, 100, self)
            self._send_progress_dialog.setWindowTitle("Sending File")
            self._send_progress_dialog.setMinimumWidth(300)
            self._send_progress_dialog.setModal(True)

            self._progress_handler = ProgressHandler(self._send_progress_dialog)
            self._send_progress_dialog.canceled.connect(
                lambda: self._progress_handler.set_goal(-1)
            )

        self._send_file()

    def _center_window(self) -> None:
        """
        Centers the window on the screen (not working in Debian (why?))
        """
        if self.isMaximized():
            return

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)

        self.move(window_geometry.topLeft())
