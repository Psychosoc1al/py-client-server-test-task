import argparse
import os
import socket
from datetime import datetime


def start_server(directory, host="0.0.0.0", port=12345):
    if not os.path.exists(directory):
        os.makedirs(directory)

    server_socket = socket.create_server((host, port))
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Receive metadata length
        metadata_length = int(client_socket.recv(10).decode().strip())
        file_info = client_socket.recv(metadata_length).decode()
        filename, filesize = file_info.split(",")
        filename = os.path.basename(filename)
        filesize = int(filesize)
        print(f"Receiving {filename} ({filesize} bytes)")

        filepath = os.path.join(directory, filename)
        with open(filepath, "wb") as f:
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                f.write(chunk)

        with open(os.path.join(directory, "file_attributes.txt"), "a") as attr_file:
            attr_file.write(f"{filename},{filesize},{datetime.now().isoformat()}\n")

        client_socket.close()
        print(f"File {filename} received and saved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Transfer Server")
    parser.add_argument("directory", help="Directory to save received files")
    args = parser.parse_args()
    start_server(args.directory)
