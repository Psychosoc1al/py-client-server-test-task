import argparse
import os
import socket
from datetime import datetime

import dotenv


def receive_filename(client_socket: socket.socket) -> str:
    metadata_size = int(os.getenv("METADATA_LENGTH_SIZE"))
    metadata_length = int(client_socket.recv(metadata_size).decode().strip())

    file_info = client_socket.recv(metadata_length).decode()
    filename, filesize = file_info.split("/")
    filename = os.path.basename(filename)
    filesize = int(filesize)
    print(f"Receiving {filename} ({filesize} bytes)")

    return filename


def start_server(directory: str, host: str = "0.0.0.0", port: int = 12345) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

    server_socket = socket.create_server((host, port))
    print(f"Server listening on {host}:{port}")

    bufsize = int(os.getenv("CONNECTION_BUFSIZE"))
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        filename = receive_filename(client_socket)

        filepath = os.path.join(directory, filename)
        with open(filepath, "wb") as f:
            while True:
                chunk = client_socket.recv(bufsize)
                if not chunk:
                    break
                f.write(chunk)

        with open(os.path.join(directory, "file_attributes.txt"), "a") as attr_file:
            attr_file.write(f"{filename},{datetime.now().isoformat()}\n")

        client_socket.close()
        print(f"File {filename} received and saved.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="File Transfer Server")
    parser.add_argument("directory", help="Directory to save received files")
    args = parser.parse_args()
    start_server(args.directory)


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
