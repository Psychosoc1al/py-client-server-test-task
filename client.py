import argparse
import logging
import os
import sys

import dotenv
from PyQt6.QtWidgets import QApplication

import client_cli
import client_gui


def main_cli(file_path: str, host: str, port: int) -> None:
    try:
        client_cli.send_file(file_path, host, port)
    except Exception as e:
        logging.error(f"Failed to send file: {e}")


def main_gui() -> None:
    app = QApplication([])
    client = client_gui.FileTransferClientGUI()
    client.show()
    app.exec()


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI or GUI File Transfer Client")
    subparsers = parser.add_subparsers(dest="mode", help="Mode: cli or gui")

    cli_parser = subparsers.add_parser("cli", help="Run in CLI mode")
    cli_parser.add_argument("file_path", help="Path to the file to transfer")
    cli_parser.add_argument("host", help="Server IP address")
    cli_parser.add_argument("port", type=int, help="Server port")

    subparsers.add_parser("gui", help="Run in GUI mode")

    args = parser.parse_args()

    if args.mode == "cli":
        main_cli(args.file_path, args.host, args.port)
    else:
        main_gui()


if __name__ == "__main__":
    dotenv.load_dotenv(
        os.path.join(os.path.dirname(__file__), ".env")  # must-have for binary
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    main()
