import qdarktheme
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QMainWindow,
    QWidget,
)

import client_cli


class FileTransferClientGUI(QMainWindow):
    """A GUI application for transferring files using PyQt6."""

    def __init__(self):
        """Initializes the FileTransferClientGUI class."""
        super().__init__()
        self._init_ui()

        self.show()

    def _init_ui(self) -> None:
        """Initializes the user interface."""
        qdarktheme.setup_theme(custom_colors={"primary": "#d79df1"})

        self.setWindowTitle("File Transfer Client")
        self.setMinimumSize(300, 300)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowMaximizeButtonHint
        )

        self.main_widget = QWidget()
        layout = QVBoxLayout()

        self.file_label = QLabel("File:")
        self.file_input = QLineEdit(self)
        self.file_input.textChanged.connect(lambda _: self._handle_button_state())

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self._browse_file)

        self.host_label = QLabel("Host:")
        self.host_input = QLineEdit(self)
        self.host_input.setPlaceholderText("127.0.0.1 or example.com")
        self.host_input.textChanged.connect(lambda _: self._handle_button_state())

        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("12345")
        self.port_input.textChanged.connect(lambda _: self._handle_button_state())

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self._send_file)
        self.send_button.setDisabled(True)

        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.send_button)

        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)

    def _browse_file(self) -> None:
        """
        Opens a file dialog to browse and select a file.

        Sets the selected file path in the file input line edit.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File")

        if file_name:
            self.file_input.setText(file_name)

    def _send_file(self) -> None:
        """
        Sends the selected file to the specified host and port.

        Displays a success or error message based on the result of the file transfer.
        """
        file_path = self.file_input.text()
        host = self.host_input.text()
        port = int(self.port_input.text())

        try:
            client_cli.send_file(file_path, host, port)
            QMessageBox.information(self, "Success", "File sent successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send file: {e}")

    def _handle_button_state(self) -> None:
        """
        Enables or disables the send button based on the input fields.

        The send button is enabled only if the file, host, and port fields are not empty.
        """
        if self.file_input.text() and self.host_input.text() and self.port_input.text():
            self.send_button.setEnabled(True)
        else:
            self.send_button.setDisabled(True)
