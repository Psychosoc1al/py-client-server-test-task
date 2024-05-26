import argparse
import logging
import os
import socket

import dotenv


def send_metadata(file_path: str, client_socket: socket.socket) -> str:
    try:
        filesize = os.path.getsize(file_path)
        filename = os.path.basename(file_path)

        file_info = f"{filename}/{filesize}"
        metadata_size = int(os.getenv("METADATA_LENGTH_SIZE"))
        metadata_length = f"{len(file_info):<{metadata_size}}".encode()

        client_socket.sendall(metadata_length)
        client_socket.sendall(file_info.encode())

        logging.info(f"File {filename} metadata sent to server.")
        return filename
    except Exception as e:
        logging.error(f"Error sending metadata: {e}")
        raise


def send_file(file_path: str, host: str, port: int) -> None:
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} does not exist.")
        return

    client_socket = None
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        filename = send_metadata(file_path, client_socket)

        read_size = int(os.getenv("CONNECTION_BUFSIZE"))
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(read_size)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)

        logging.info(f"File {filename} sent to server.")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except Exception as e:
        logging.error(f"Error sending file: {e}")
    finally:
        client_socket.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="File Transfer Client")
    parser.add_argument("file_path", help="Path of the file to transfer")
    parser.add_argument("host", help="Server IP address")
    parser.add_argument("port", type=int, help="Server port")
    args = parser.parse_args()

    try:
        send_file(args.file_path, args.host, args.port)
    except Exception as e:
        logging.error(f"Failed to send file: {e}")


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    main()
