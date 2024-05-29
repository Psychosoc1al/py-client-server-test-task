import multiprocessing
import os
import random
import subprocess
import sys

import dotenv


def run(
    script_path: str,
    files_dir: str,
    files_sizes: list[int],
    host: str,
    port: int,
) -> None:
    file_path = os.path.join(files_dir, f"test_file_{random.choice(files_sizes)}.txt")
    result = subprocess.run(
        [sys.executable, "cli", script_path, file_path, host, str(port)],
        capture_output=True,
        text=True,
    )
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")


def main() -> None:
    runs_num = 20
    script_path = os.path.abspath("../client.py")
    files_dir = "../test_files"
    files_sizes = [int(size) for size in os.getenv("TEST_FILES_LENGTHS_KIB").split()]
    host = "127.0.0.1"
    port = 12345

    with multiprocessing.Pool(processes=runs_num) as pool:
        pool.starmap(
            run, [(script_path, files_dir, files_sizes, host, port)] * runs_num
        )


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
