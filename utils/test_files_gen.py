import os
import random
import string


def generate_text_file(filename: str, size_kb: int) -> None:
    size_bytes = size_kb * 1024
    chars = string.ascii_letters + string.digits + string.punctuation
    with open(filename, "w") as f:
        while f.tell() < size_bytes:
            f.write("".join(random.choices(chars, k=1024)))


def generate_files(sizes_kb: list[int]) -> None:
    if not os.path.exists("../test_files"):
        os.makedirs("../test_files")

    files_num = len(sizes_kb)
    for i in range(files_num):
        size = sizes_kb[i]
        filename = os.path.join("../test_files", f"test_file_{size}.txt")

        generate_text_file(filename, size)
        print(f"Generated {filename} with size {size}KB")


def main() -> None:
    sizes_kb = [1, 5, 10, 50, 100, 500, 1000, 10000, 100000]

    generate_files(sizes_kb)


if __name__ == "__main__":
    main()
