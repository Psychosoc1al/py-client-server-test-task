import argparse
import logging
import os
import random
import socket
from datetime import datetime

import dotenv
import select


def receive_metadata(client_socket: socket.socket) -> tuple[str, int]:
    try:
        metadata_size = int(os.getenv("METADATA_LENGTH_SIZE"))
        metadata_length_data = client_socket.recv(metadata_size)
        if not metadata_length_data:
            raise ConnectionError("Socket closed prematurely")

        metadata_length = int(metadata_length_data.decode().strip())
        file_info_data = client_socket.recv(metadata_length)
        if not file_info_data:
            raise ConnectionError("Socket closed prematurely")

        filename, filesize = file_info_data.decode().split("/")
        filename = f"{random.randint(0, 10000)}{filename}"
        filesize = int(filesize)
        logging.info(f"Receiving {filename} ({filesize} bytes)")
        return filename, filesize
    except Exception as e:
        logging.error(f"Error receiving metadata: {e}")
        raise


def handle_new_connection(
    epoll: select.epoll, server_socket: socket.socket, connections: dict[int, dict]
) -> None:
    client_socket, addr = server_socket.accept()
    logging.info(f"Connection from {addr}")
    client_socket.setblocking(False)
    epoll.register(client_socket.fileno(), select.EPOLLIN)
    connections[client_socket.fileno()] = {
        "socket": client_socket,
        "state": "RECEIVE_METADATA",
        "file": None,
        "filename": None,
        "filesize": 0,
        "received": 0,
    }


def handle_metadata_reception(
    connection: dict[str], client_socket: socket.socket, directory: str
) -> None:
    try:
        filename, filesize = receive_metadata(client_socket)
        filepath = os.path.join(directory, filename)
        file = open(filepath, "wb")
        connection.update(
            {
                "state": "RECEIVE_FILE",
                "file": file,
                "filename": filename,
                "filesize": filesize,
            }
        )
    except Exception as e:
        logging.error(f"Error in metadata reception: {e}")
        cleanup_connection(connection, client_socket)


def handle_file_reception(
    connection: dict[str],
    client_socket: socket.socket,
    epoll: select.epoll,
    descriptor_no: int,
    directory: str,
    bufsize: int,
) -> None:
    try:
        chunk = client_socket.recv(bufsize)
        if chunk:
            connection["file"].write(chunk)
            connection["received"] += len(chunk)
            if connection["received"] >= connection["filesize"]:
                finalize_file_reception(connection, directory)
                cleanup_connection(connection, client_socket, epoll, descriptor_no)
        else:
            cleanup_connection(connection, client_socket, epoll, descriptor_no)
    except BlockingIOError:
        return
    except Exception as e:
        logging.error(f"Error in file reception: {e}")
        cleanup_connection(connection, client_socket, epoll, descriptor_no)


def cleanup_connection(
    connection: dict[str],
    client_socket: socket.socket,
    epoll: select.epoll = None,
    descriptor_no: int = None,
) -> None:
    if connection["file"]:
        connection["file"].close()
    if epoll and descriptor_no:
        epoll.unregister(descriptor_no)
    client_socket.close()


def finalize_file_reception(connection: dict[str], directory: str) -> None:
    connection["file"].close()
    logging.info(f"File {connection['filename']} received and saved.")
    with open(os.path.join(directory, "file_attributes.txt"), "a") as attr_file:
        attr_file.write(f"{datetime.now().isoformat()},{connection['filename']}\n")


def handle_event(
    descriptor_no: int,
    event: int,
    epoll: select.epoll,
    server_socket: socket.socket,
    connections: dict[int, dict[str]],
    directory: str,
    bufsize: int,
) -> None:
    if descriptor_no == server_socket.fileno():
        handle_new_connection(epoll, server_socket, connections)
    elif event & select.EPOLLIN:
        connection = connections[descriptor_no]
        client_socket = connection["socket"]

        if connection["state"] == "RECEIVE_METADATA":
            handle_metadata_reception(connection, client_socket, directory)
        if connection["state"] == "RECEIVE_FILE":
            handle_file_reception(
                connection,
                client_socket,
                epoll,
                descriptor_no,
                directory,
                bufsize,
            )


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
                handle_event(
                    descriptor_no,
                    event,
                    epoll,
                    server_socket,
                    connections,
                    directory,
                    bufsize,
                )
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
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    main()
