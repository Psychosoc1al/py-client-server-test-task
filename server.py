import argparse
import logging
import os
import random
import socket
import select
from datetime import datetime

import dotenv


def receive_metadata(client_socket: socket.socket) -> str:
    try:
        metadata_size = int(os.getenv("METADATA_LENGTH_SIZE"))
        metadata_length_data = b""
        while len(metadata_length_data) < metadata_size:
            try:
                chunk = client_socket.recv(metadata_size - len(metadata_length_data))
                if not chunk:
                    raise ConnectionError("Socket closed prematurely")
                metadata_length_data += chunk
            except BlockingIOError:
                continue

        metadata_length = int(metadata_length_data.decode().strip())

        file_info_data = b""
        while len(file_info_data) < metadata_length:
            try:
                chunk = client_socket.recv(metadata_length - len(file_info_data))
                if not chunk:
                    raise ConnectionError("Socket closed prematurely")
                file_info_data += chunk
            except BlockingIOError:
                continue

        file_info = file_info_data.decode()
        filename, filesize = file_info.split("/")
        filename = str(random.randint(0, 10000)) + filename
        filesize = int(filesize)
        logging.info(f"Receiving {filename} ({filesize} bytes)")

        return filename
    except Exception as e:
        logging.error(f"Error receiving metadata: {e}")
        raise


def receive_file(client_socket: socket.socket, directory: str, bufsize: int) -> None:
    try:
        filename = receive_metadata(client_socket)
        filepath = os.path.join(directory, filename)
        with open(filepath, "wb") as f:
            while True:
                try:
                    chunk = client_socket.recv(bufsize)
                    if not chunk:
                        break
                    f.write(chunk)
                except BlockingIOError:
                    continue

        with open(os.path.join(directory, "file_attributes.txt"), "a") as attr_file:
            attr_file.write(f"{datetime.now().isoformat()},{filename}\n")

        logging.info(f"File {filename} received and saved.")
    except Exception as e:
        logging.error(f"Error handling file transfer: {e}")
    finally:
        client_socket.close()


def start_server(directory: str, host: str, port: int) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(socket.SOMAXCONN)
    server_socket.setblocking(False)

    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)

    bufsize = int(os.getenv("CONNECTION_BUFSIZE"))
    connections = {}
    try:
        logging.info(f"Server listening on {host}:{port}")
        while True:
            events = epoll.poll()
            for descriptor_no, event in events:
                if descriptor_no == server_socket.fileno():
                    client_socket, addr = server_socket.accept()
                    logging.info(f"Connection from {addr}")
                    client_socket.setblocking(False)
                    epoll.register(client_socket.fileno(), select.EPOLLIN)
                    connections[client_socket.fileno()] = client_socket
                elif event & select.EPOLLIN:
                    client_socket = connections[descriptor_no]
                    epoll.unregister(descriptor_no)
                    receive_file(client_socket, directory, bufsize)
                    del connections[descriptor_no]

    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        epoll.unregister(server_socket.fileno())
        epoll.close()
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
