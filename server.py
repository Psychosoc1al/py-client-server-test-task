import argparse
import os
import socket
from datetime import datetime


def start_server(directory, host="0.0.0.0", port=12345):
    if not os.path.exists(directory):
        os.makedirs(directory)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        file_info = client_socket.recv(1024).decode()
        print(f"Received file info: {file_info}")
        filename, filesize = file_info.split(",")
        filename = os.path.basename(filename)
        filesize = int(filesize)

        filepath = os.path.join(directory, filename)
        with open(filepath, "wb") as f:
            bytes_received = 0
            while bytes_received < filesize:
                chunk = client_socket.recv(min(1024, filesize - bytes_received))
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)

        with open(os.path.join(directory, "file_attributes.txt"), "a") as attr_file:
            attr_file.write(f"{filename},{datetime.now().isoformat()}\n")

        client_socket.close()
        print(f"File {filename} received and saved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Transfer Server")
    parser.add_argument("directory", help="Directory to save received files")
    args = parser.parse_args()
    start_server(args.directory)
