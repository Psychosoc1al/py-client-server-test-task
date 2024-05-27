import os
import random
import string

import dotenv


def generate_text_file(filename: str, size_kib: int) -> None:
    size_bytes = size_kib * 1024
    chars = string.ascii_letters + string.digits + string.punctuation
    with open(filename, "w") as f:
        while f.tell() < size_bytes:
            f.write("".join(random.choices(chars, k=1024)))


def generate_files(sizes_kib: list[int]) -> None:
    if not os.path.exists("../test_files"):
        os.makedirs("../test_files")

    files_num = len(sizes_kib)
    for i in range(files_num):
        size = sizes_kib[i]
        filename = os.path.join("../test_files", f"test_file_{size}.txt")

        generate_text_file(filename, size)
        print(f"Generated {filename} with size {size}KiB")


def main() -> None:
    dotenv.load_dotenv()
    sizes_kib = [int(size) for size in os.getenv("TEST_FILES_LENGTHS_KIB").split()]

    generate_files(sizes_kib)


if __name__ == "__main__":
    main()
