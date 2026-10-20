"""Hold a small, fixed amount of memory for profiler demonstrations."""

import time


def main():
    memory_mebibytes = 32
    duration_seconds = 8
    memory = bytearray(memory_mebibytes * 1024 * 1024)

    # Touch one byte per page so the operating system backs the allocation.
    for index in range(0, len(memory), 4096):
        memory[index] = 1

    print(f"Holding about {memory_mebibytes} MiB for {duration_seconds} seconds.")
    time.sleep(duration_seconds)


if __name__ == "__main__":
    main()
