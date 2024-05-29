import logging
import os
import socket


def send_metadata(file_path: str, client_socket: socket.socket) -> str:
    """
    Send metadata of the file to the server.

    This function sends the metadata of the file, including the filename and
    file size, to the server using the provided socket.

    Args:
        file_path: The path of the file whose metadata is to be sent.
        client_socket: The socket object for the connection to the server.

    Returns:
        The filename of the file whose metadata was sent.

    Notes:
        METADATA_LENGTH_SIZE is an environment variable that specifies the size of the
        metadata length in bytes. Must be set before running the script (see .env).
    """
    filesize = os.path.getsize(file_path)
    filename = os.path.basename(file_path)

    file_info = f"{filename}/{filesize}"
    metadata_size = int(os.getenv("METADATA_LENGTH_SIZE"))
    metadata_length = f"{len(file_info):<{metadata_size}}".encode()

    client_socket.sendall(metadata_length)
    client_socket.sendall(file_info.encode())

    logging.info(f"File {filename} metadata sent to server.")
    return filename


def send_file(file_path: str, host: str, port: int) -> None:
    """
    Send a file to a server.

    This function establishes a connection to the server, sends the file metadata,
    and then sends the file in chunks.

    Args:
        file_path: The path of the file to be sent.
        host: The IP address of the server.
        port: The port number of the server.

    Returns:
        None

    Raises:
        socket.error: If the connection to the server cannot be established.

    Notes:
        CONNECTION_BUFSIZE is an environment variable that specifies the buffer size
        for the connection. Must be set before running the script (see .env).
    """
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} does not exist.")
        return

    with socket.create_connection((host, port)) as client_socket:
        filename = send_metadata(file_path, client_socket)

        read_size = int(os.getenv("CONNECTION_BUFSIZE"))
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(read_size), b""):
                client_socket.sendall(chunk)

        logging.info(f"File {filename} sent to server.")
