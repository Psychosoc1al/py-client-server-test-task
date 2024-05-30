import argparse
import logging
import os
import sys

import dotenv
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

import client_cli
import client_gui


def main_cli(file_path: str, host: str, port: int) -> None:
    try:
        client_cli.send_file(file_path, host, port)
    except Exception as e:
        logging.error(f"Failed to send file: {e}")


def main_gui(icon_dir: str) -> None:
    app = QApplication([])
    app.setWindowIcon(QIcon(os.path.join(icon_dir, "icons/client.ico")))
    client_gui.FileTransferClientGUI()

    app.exec()


def main() -> None:
    # The block below is necessary for loading .env file both in script and executable
    external_data_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if getattr(sys, "frozen", False):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        external_data_dir = sys._MEIPASS
    dotenv.load_dotenv(dotenv_path=os.path.join(external_data_dir, ".env"))

    parser = argparse.ArgumentParser(description="CLI or GUI File Transfer Client")
    subparsers = parser.add_subparsers(dest="mode", help="Mode: cli or gui")

    subparsers.add_parser("gui", help="Run in GUI mode")
    cli_parser = subparsers.add_parser("cli", help="Run in CLI mode")

    cli_parser.add_argument("file_path", help="Path to the file to transfer")
    cli_parser.add_argument("host", help="Server IP address")
    cli_parser.add_argument("port", type=int, help="Server port")

    args = parser.parse_args()

    if args.mode == "cli":
        main_cli(args.file_path, args.host, args.port)
    else:
        main_gui(external_data_dir)


if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        main()
    except KeyboardInterrupt:
        logging.info("Stopping client...")
