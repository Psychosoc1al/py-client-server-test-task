import argparse
import logging
import os
import socket
from datetime import datetime

import dotenv


def receive_metadata(client_socket: socket.socket) -> str:
    try:
        metadata_size = int(os.getenv("METADATA_LENGTH_SIZE"))
        metadata_length = int(client_socket.recv(metadata_size).decode().strip())

        file_info = client_socket.recv(metadata_length).decode()
        filename, filesize = file_info.split("/")
        filename = os.path.basename(filename)
        filesize = int(filesize)
        logging.info(f"Receiving {filename} ({filesize} bytes)")

        return filename
    except Exception as e:
        logging.error(f"Error receiving metadata: {e}")
        raise


def receive_file(server_socket: socket.socket, directory: str, bufsize: int) -> None:
    client_socket, addr = server_socket.accept()
    logging.info(f"Connection from {addr}")

    try:
        filename = receive_metadata(client_socket)
        filepath = os.path.join(directory, filename)
        with open(filepath, "wb") as f:
            while True:
                chunk = client_socket.recv(bufsize)
                if not chunk:
                    break
                f.write(chunk)

        with open(os.path.join(directory, "file_attributes.txt"), "a") as attr_file:
            attr_file.write(f"{filename},{datetime.now().isoformat()}\n")

        logging.info(f"File {filename} received and saved.")
    except Exception as e:
        logging.error(f"Error handling file transfer: {e}")
    finally:
        client_socket.close()


def start_server(directory: str, host: str, port: int) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

    server_socket = None
    try:
        server_socket = socket.create_server((host, port))
        logging.info(f"Server listening on {host}:{port}")

        bufsize = int(os.getenv("CONNECTION_BUFSIZE"))
        while True:
            receive_file(server_socket, directory, bufsize)

    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        server_socket.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="File Transfer Server")
    parser.add_argument("directory", help="Directory to save received files")
    parser.add_argument(
        "-H",
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=12345,
        help="Port to bind the server to (default: 12345)",
    )
    args = parser.parse_args()

    try:
        start_server(args.directory, args.host, args.port)
    except Exception as e:
        logging.error(f"Failed to start server: {e}")


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    main()
