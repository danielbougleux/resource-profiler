# Example workloads

These small Python programs are **workloads**: programs that you can run as targets of `rprof` or use to create activity while the host profiler is running. They use only Python's standard library and do not need extra packages.

Run commands from the repository root (the folder containing `README.md`). The examples finish on their own and are intentionally bounded: the CPU and memory examples run for about 8 seconds, and the disk example writes a temporary 16 MiB file and then removes it.

The commands below use Bash-style directory creation and `python3`, and work in a Linux/macOS terminal.

## Choose an example

| Program | What it demonstrates | Select this metric |
| --- | --- | --- |
| [`cpu_workload.py`](cpu_workload.py) | Repeated calculations that keep a CPU busy for about 8 seconds. | `--cpu` |
| [`memory_workload.py`](memory_workload.py) | Allocates and touches about 32 MiB, then holds it for about 8 seconds. | `--memory` |
| [`disk_workload.py`](disk_workload.py) | Writes a 16 MiB temporary file in small steps, then deletes it. | `--disk` |

## Profile one example process

Create a separate directory for each run. This prevents one example from overwriting another example's CSV files.

### CPU example

```bash
mkdir -p results/cpu results/cpu/plots
python3 rprof/rprof.py \
  --cpu \
  --interval 0.5 \
  --output_dir results/cpu \
  "python3 examples/cpu_workload.py"

python3 rprof/rprof-plotter.py \
  --input-dir results/cpu \
  --cpu \
  --output_dir results/cpu/plots
```

Open `results/cpu/plots/cpuusage.png`. The CPU example runs for about 8 seconds; an interval of 0.5 seconds should collect several samples during the run.

### Memory example

```bash
mkdir -p results/memory results/memory/plots
python3 rprof/rprof.py \
  --memory \
  --interval 0.5 \
  --output_dir results/memory \
  "python3 examples/memory_workload.py"

python3 rprof/rprof-plotter.py \
  --input-dir results/memory \
  --memory \
  --output_dir results/memory/plots
```

Open `results/memory/plots/MemoryUsage.png`. The program keeps its allocation alive while it sleeps, giving the profiler time to take multiple samples. The memory plot uses PSS, which is not available on every operating system; if that field is missing, inspect `memory.csv` and your platform's `psutil` support.

### Disk example

```bash
mkdir -p results/disk results/disk/plots
python3 rprof/rprof.py \
  --disk \
  --interval 0.5 \
  --output_dir results/disk \
  "python3 examples/disk_workload.py"

python3 rprof/rprof-plotter.py \
  --input-dir results/disk \
  --disk \
  --output_dir results/disk/plots
```

Open the `DiskRead...` and `DiskWrite...` PNG files in `results/disk/plots`. The example writes a temporary file in several steps and removes it when finished. Process-level disk counters depend on operating-system support and may not be available everywhere.

## Try host profiling instead

Host profiling measures the whole computer, not just the example program. In terminal 1, start the host profiler with the metric you want:

```bash
mkdir -p results/host results/host/plots
python3 rprof-host/rprof-host.py \
  --cpu \
  --interval 0.5 \
  --output_dir results/host
```

In terminal 2, run an example:

```bash
python3 examples/cpu_workload.py
```

After the example finishes, stop the profiler by writing `1` to its control file:

```bash
printf 1 > results/host/.mon
```

Wait for the host profiler to exit. It checks the control file every 10 samples, so it may take up to about 10 sampling intervals to stop. Then generate the host CPU charts:

```bash
python3 rprof-host/rprof-plotter-host.py \
  --input-dir results/host \
  --cpu \
  --output_dir results/host/plots
```

Because host profiling includes all system activity, other applications may also affect the charts. Try a memory or disk example by changing the collection and plot options to `--memory` or `--disk`.

## What to look at

- A CSV file is the raw time-stamped data; a PNG is a chart made from one of those files.
- The chart's horizontal axis is elapsed seconds since the first sample, not time of day.
- Use a separate output folder for each run. Profilers overwrite same-named CSV files in an existing output folder.
- Sampling may miss very brief activity. A shorter interval takes more samples but adds monitoring overhead.
- These example programs illustrate metric collection. Their results depend on your computer and should not be used to compare computer performance.

## Small experiments to try

1. **Change the sampling interval.** Run the CPU example once with `--interval 0.5` and once with `--interval 1.0`, using a different output folder for each run. Compare the number of data rows in `cpu.csv`. The longer interval should produce fewer samples.
2. **Change the memory allocation.** In `memory_workload.py`, change `memory_mebibytes` from `32` to `64`. Run it again and compare the memory chart. Keep the allocation modest, especially on shared or low-memory computers.
3. **Change the amount of disk writing.** In `disk_workload.py`, change `block_count` from `16` to `24`. This increases the temporary file from 16 MiB to 24 MiB; the file is still automatically removed when the example ends.
4. **Compare process and host profiling.** Run the same CPU example once through the process profiler and once while the host profiler is running. The process chart focuses on that program; the host chart also includes other computer activity.
