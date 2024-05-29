import argparse
import logging
import os
import socket
import sys
from datetime import datetime

import dotenv
import select


def generate_unique_filename(directory: str, filename: str) -> str:
    """
    Generates a unique filename in the specified directory by appending a number
    if a file with the same name already exists.

    Args:
        directory: The directory where the file will be saved.
        filename: The original filename.

    Returns:
        A unique filename with an appended number if needed.
    """
    name, ext = os.path.splitext(filename)
    files_in_directory = os.listdir(directory)

    same_name_count = sum(
        1
        for f in files_in_directory
        if f.startswith(f"{name} (") and f.endswith(f"){ext}") or f == filename
    )

    if same_name_count:
        filename = f"{name} ({same_name_count}){ext}"

    return filename


def receive_metadata(client_socket: socket.socket, directory: str) -> tuple[str, int]:
    """
    Receives metadata from the client socket, including the filename and filesize.

    Args:
        client_socket: The socket connected to the client.
        directory: The directory where the file will be saved.

    Returns:
        A tuple containing the unique filename and filesize.
    """
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
        filename = generate_unique_filename(directory, filename)
        filesize = int(filesize)
        logging.info(f"Receiving {filename} ({filesize} bytes)")
        return filename, filesize
    except Exception as e:
        logging.error(f"Error receiving metadata: {e}")
        raise


def handle_new_connection(
    epoll: select.epoll, server_socket: socket.socket, connections: dict[int, dict]
) -> None:
    """
    Handles a new incoming connection by accepting it, setting it to non-blocking,
    and registering it with epoll.

    Args:
        epoll: The epoll object for managing multiple connections.
        server_socket: The server socket accepting new connections.
        connections: A dictionary tracking active connections.
    """
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
    """
    Handles the reception of metadata from the client, including the filename and filesize.

    Args:
        connection: A dictionary containing connection-specific information.
        client_socket: The socket connected to the client.
        directory: The directory where the file will be saved.
    """
    try:
        filename, filesize = receive_metadata(client_socket, directory)
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
    """
    Handles the reception of the actual file data from the client.

    Args:
        connection: A dictionary containing connection-specific information.
        client_socket: The socket connected to the client.
        epoll: The epoll object for managing multiple connections.
        descriptor_no: The file descriptor number for the connection.
        directory: The directory where the file will be saved.
        bufsize: The buffer size for receiving data.
    """
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
    """
    Cleans up the connection by closing the file and the client socket,
    and unregistering from epoll if provided.

    Args:
        connection: A dictionary containing connection-specific information.
        client_socket: The socket connected to the client.
        epoll: The epoll object for managing multiple connections (optional).
        descriptor_no: The file descriptor number for the connection (optional).
    """
    if connection["file"]:
        connection["file"].close()
    if epoll and descriptor_no:
        epoll.unregister(descriptor_no)
    client_socket.close()


def finalize_file_reception(connection: dict[str], directory: str) -> None:
    """
    Finalizes the file reception by closing the file and logging the received file's details.

    Args:
        connection: A dictionary containing connection-specific information.
        directory: The directory where the file is saved.
    """
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
    """
    Handles different events such as new connections and data reception.

    Args:
        descriptor_no: The file descriptor number for the connection.
        event: The event mask indicating the type of event.
        epoll: The epoll object for managing multiple connections.
        server_socket: The server socket accepting new connections.
        connections: A dictionary tracking active connections.
        directory: The directory where the file will be saved.
        bufsize: The buffer size for receiving data.
    """
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
    """
    Starts the file transfer server, setting up the server socket, epoll object,
    and entering the main event loop.

    Args:
        directory: The directory where the file will be saved.
        host: The host address to bind the server to.
        port: The port number to bind the server to.
    """
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
    # The block below is necessary for loading .env file both in script and executable
    env_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if getattr(sys, "frozen", False):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        env_dir = sys._MEIPASS
    dotenv.load_dotenv(dotenv_path=os.path.join(env_dir, ".env"))

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    main()
