import multiprocessing
import os
import subprocess
import sys


def run(
    script_path: str,
    file_path: str,
    host: str,
    port: int,
) -> None:
    result = subprocess.run(
        [sys.executable, script_path, file_path, host, str(port)],
        capture_output=True,
        text=True,
    )
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")


def main() -> None:
    runs_num = 6
    script_path = os.path.abspath("../client.py")
    file_path = "../test_files/test_file_100000.txt"
    host = "127.0.0.1"
    port = 12345

    with multiprocessing.Pool(processes=runs_num) as pool:
        pool.starmap(run, [(script_path, file_path, host, port)] * runs_num)


if __name__ == "__main__":
    main()
