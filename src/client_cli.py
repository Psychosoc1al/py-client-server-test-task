import logging
import os
import socket

import tqdm

import gui_progress_handler


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

    logging.info(f"File {filename} metadata sent to server")
    return filename


def send_file(
    file_path: str,
    host: str,
    port: int,
    progress_handler: "gui_progress_handler.ProgressHandler" = None,
) -> None:
    """
    Send a file to a server.

    This function establishes a connection to the server, sends the file metadata,
    and then sends the file in chunks. If the GUI progress handler is provided,
    it will be used to update the progress bar of the sending process.

    Args:
        file_path: The path of the file to be sent.
        host: The IP address of the server.
        port: The port number of the server.
        progress_handler: The GUI progress handler for updating the progress bar of sending the file.

    Raises:
        FileNotFoundError: If the file to be sent does not exist.
        ConnectionResetError: If the server fails to receive the file.

    Notes:
        CONNECTION_BUFSIZE is an environment variable that specifies the buffer size
        for the connection. Must be set before running the script (see .env).
    """
    with socket.create_connection((host, port)) as client_socket:
        filename = send_metadata(file_path, client_socket)

        read_size = int(os.getenv("CONNECTION_BUFSIZE"))
        file_size = os.path.getsize(file_path)

        if progress_handler:
            progress_handler.final_value = file_size

        offset = 0
        with open(file_path, "rb") as f, tqdm.tqdm(
            desc="Sending file", total=file_size, ncols=80, unit="B", unit_scale=True
        ) as pbar:
            while offset < file_size:
                sent = client_socket.sendfile(f, offset, read_size * 4)
                if not sent:
                    raise ConnectionResetError(f"Server failed to receive {filename}")
                offset += sent
                pbar.update(sent)

                if progress_handler and not progress_handler.update_progress(sent):
                    client_socket.close()
                    return

        success = client_socket.recv(1)
        client_socket.close()

        if not success:
            raise ConnectionResetError(f"Server failed to receive {filename}")

        logging.info(f"File {filename} sent successfully")
        if progress_handler:
            progress_handler.finish()
