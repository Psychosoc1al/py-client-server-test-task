import socket
import os
import argparse


def send_file(file_path, host="127.0.0.1", port=12345):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return

    filesize = os.path.getsize(file_path)
    filename = os.path.basename(file_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Prepare metadata
    file_info = f"{filename},{filesize}"
    metadata_length = f"{len(file_info):<10}".encode()

    # Send metadata length and metadata
    client_socket.send(metadata_length)
    client_socket.send(file_info.encode())

    # Send file content
    with open(file_path, "rb") as f:
        while True:
            bytes_read = f.read(1024)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)

    client_socket.close()
    print(f"File {filename} sent to server.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Transfer Client")
    parser.add_argument("file_path", help="Path of the file to transfer")
    parser.add_argument("host", help="Server IP address")
    parser.add_argument("port", type=int, help="Server port")
    args = parser.parse_args()
    send_file(args.file_path, args.host, args.port)
