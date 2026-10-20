"""Write a bounded temporary file for profiler demonstrations."""

import os
import tempfile
import time
from pathlib import Path


def main():
    block_mebibytes = 1
    block_count = 16
    pause_seconds = 0.25
    block = b"x" * (block_mebibytes * 1024 * 1024)

    with tempfile.TemporaryDirectory(prefix="resource-profiler-") as temp_dir:
        file_path = Path(temp_dir) / "sample.bin"
        with file_path.open("wb") as sample_file:
            for _ in range(block_count):
                sample_file.write(block)
                sample_file.flush()
                os.fsync(sample_file.fileno())
                time.sleep(pause_seconds)

    total_mebibytes = block_mebibytes * block_count
    print(f"Wrote and removed a temporary {total_mebibytes} MiB file.")


if __name__ == "__main__":
    main()
