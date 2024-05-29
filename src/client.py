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
    client_gui.FileTransferClientGUI()

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
    # The block below is necessary for loading .env file both in script and executable
    env_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if getattr(sys, "frozen", False):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        env_dir = sys._MEIPASS
    dotenv.load_dotenv(dotenv_path=os.path.join(env_dir, ".env"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    main()
