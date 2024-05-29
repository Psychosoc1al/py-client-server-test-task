# import qdarktheme
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

import client_cli


class FileTransferClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()

        self.file_label = QLabel("File:")
        self.file_input = QLineEdit(self)

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self._browse_file)

        self.host_label = QLabel("Host:")
        self.host_input = QLineEdit(self)

        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit(self)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self._send_file)

        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def _browse_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        if file_name:
            self.file_input.setText(file_name)

    def _send_file(self) -> None:
        file_path = self.file_input.text()
        host = self.host_input.text()
        port = int(self.port_input.text())

        if not file_path or not host or not port:
            QMessageBox.warning(self, "Input Error", "Please provide all the inputs.")
            return

        try:
            client_cli.send_file(file_path, host, port)
            QMessageBox.information(self, "Success", "File sent successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send file: {e}")
