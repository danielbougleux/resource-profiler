"""Run a short, repeatable CPU-bound task for profiler demonstrations."""

import time


def main():
    duration_seconds = 8
    deadline = time.perf_counter() + duration_seconds
    iterations = 0

    while time.perf_counter() < deadline:
        iterations += 1
        _ = (iterations * iterations) % 97

    print(f"Completed {iterations:,} iterations in about {duration_seconds} seconds.")


if __name__ == "__main__":
    main()
