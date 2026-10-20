# resource-profiler

`resource-profiler` is a small Python command-line toolkit for collecting process or host resource metrics to CSV files and generating PNG charts from those recordings.

## What it does

The toolkit has two collection modes:

- **Process profiling** launches one command and records metrics for that process while it runs.
- **Host profiling** samples system-wide metrics until you explicitly stop it.

Each mode has a matching plotter that reads the recorded CSV files and saves PNG charts. The plotters do not collect data themselves, and they do not combine process and host recordings.

## Which tools should I use?

| What you want to study | Collect data with | Make charts with |
| --- | --- | --- |
| One specific program you want to run | [`rprof/rprof.py`](rprof/rprof.py) | [`rprof/rprof-plotter.py`](rprof/rprof-plotter.py) |
| Overall computer metrics | [`rprof-host/rprof-host.py`](rprof-host/rprof-host.py) | [`rprof-host/rprof-plotter-host.py`](rprof-host/rprof-plotter-host.py) |

Use process profiling when you want to see metrics for a particular command. Use host profiling when you want to observe the whole computer, including activity from other programs.

## Requirements

- Python 3.10 or later
- `psutil`
- `matplotlib` (needed by either plotter)

The collection scripts need `psutil`; the plotting scripts need `matplotlib`. To use all four tools, install both.

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/danielbougleux/resource-profiler.git
cd resource-profiler
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install psutil matplotlib
```

## Tools

| Metric collection scripts | Functionality |
| --- | --- |
| [`rprof/rprof.py`](rprof/rprof.py) | Run a command and collect its process's metrics. |
| [`rprof-host/rprof-host.py`](rprof-host/rprof-host.py) | Collect metrics for the whole host machine while it is running. |

| Resource graph generation scripts | Functionality |
| --- | --- |
| [`rprof/rprof-plotter.py`](rprof/rprof-plotter.py) | Create charts from process metrics. |
| [`rprof-host/rprof-plotter-host.py`](rprof-host/rprof-plotter-host.py) | Create charts from host metrics. |

Create output directories before running a profiler or plotter; the scripts do not create them automatically. Run commands from the repository root, or use the appropriate path to the script.

The command examples use Bash syntax (common on Linux and macOS).

## First experiment: measure a small program

This repository includes small example programs in [`examples/`](examples/). They are target programs for the profiler: run one of them *through* the process profiler to collect its metrics.  See the [`examples/README.md`](examples/README.md) for complete commands and explanations of each sample workload.

### 1. Process profiler

The process profiler, `rprof`, launches the command you provide and monitors it until it exits. Pass the complete command as one quoted argument:

```bash
mkdir -p results/memory
python rprof/rprof.py \
  --memory \
  --interval 1 \
  --output_dir results/memory \
  "python examples/memory_workload.py"
```

Options:

| Option | Description |
| --- | --- |
| `-c`, `--cpu` | Record process CPU metrics. |
| `-m`, `--memory` | Record process memory usage. |
| `-d`, `--disk` | Record process disk I/O counters. |
| `-g`, `--get-children` | Include resource counters from the process's child processes. |
| `-i`, `--interval SECONDS` | Set the sampling interval; default is `1.5` seconds. |
| `-o`, `--output_dir DIR` | Write CSV files to this directory; default is the current directory. |
| `command` | Required command to launch, enclosed in quotes. |

The selected metrics are written to `cpu.csv`, `memory.csv`, and/or `disk.csv` in the output directory. Each file has a header row and semicolon-separated values, including a local timestamp for each sample.

With `--get-children`, the collector adds counters from child processes to the monitored process.

### 2. Process plotter

Plot graphs that show the recorded metrics over the run. Select the same categories you collected with the process profiler. The input directory must be the directory containing those CSV files:

```bash
mkdir -p results/process/plots
python rprof/rprof-plotter.py \
  --input-dir results/process \
  --cpu --memory --disk \
  --start_point 0 --final_point 60 \
  --output_dir results/process/plots
```

Options:

| Option | Description |
| --- | --- |
| `-i`, `--input-dir DIR` | **Required.** Directory containing profiler CSV files. |
| `-c`, `--cpu` | Generate CPU usage and I/O wait charts. |
| `-m`, `--memory` | Generate a memory usage chart. |
| `-d`, `--disk` | Generate disk read/write operation and byte-delta charts. |
| `-s`, `--start_point SECONDS` | Ignore samples before this elapsed time; default is `0`. |
| `-f`, `--final_point SECONDS` | Ignore samples after this elapsed time; defaults to the end of the recording. |
| `-o`, `--output_dir DIR` | Directory for generated PNG files; defaults to the input directory. |

The elapsed-time window is measured in seconds from the first sample, not as a wall-clock timestamp. The plotter produces:

- Memory: `MemoryUsage.png`
- Disk: `DiskReadOps.png`, `DiskReadMiB.png`, `DiskWriteOps.png`, `DiskWriteMiB.png`
- CPU: `iowait.png`, `cpuusage.png`

### 3. Host profiler

The host profiler samples system-wide metrics until you request it to stop. Unlike the process profiler, it does not start or stop a workload for you. It checks its stop file after every 10 samples, so it may take up to about 10 sampling intervals to exit after you send the stop signal. For example, with `--interval 1.5`, allow up to roughly 15 seconds for shutdown.

Use two terminals for this workflow. In terminal 1, start the host profiler:

```bash
mkdir -p results/host
python rprof-host/rprof-host.py --cpu --cpu_usage --memory --disk --network \
  --interval 1.5 --output_dir results/host
```

In terminal 2, run the program or activity you want to observe. For example:

```bash
python examples/cpu_workload.py
```

After the activity finishes, stop the profiler by writing `1` to its `.mon` file:

```bash
printf 1 > results/host/.mon
```

The profiler creates `.mon` with the value `0` when it starts, so send the stop signal only after startup. Do not delete or replace this file while the profiler is running. The output directory must already exist and be writable by the user running the profiler. Wait for the profiler to exit before running the host plotter.

Options:

| Option | Description |
| --- | --- |
| `-c`, `--cpu` | Record system CPU times. |
| `-u`, `--cpu_usage` | Record CPU usage for each logical CPU. |
| `-m`, `--memory` | Record system virtual-memory statistics. |
| `-d`, `--disk` | Record system disk I/O counters. |
| `-n`, `--network` | Record system network I/O counters. |
| `-i`, `--interval SECONDS` | Set the sampling interval; default is `1.5` seconds. |
| `-o`, `--output_dir DIR` | Write CSV files and `.mon` to this directory; default is the current directory. |

The selected metrics are written to files named `cpu.csv`, `cpu_usage.csv`, `memory.csv`, `disk.csv`, and/or `network.csv`.

### 4. Host plotter

Choose the categories that have corresponding CSV files in the host profiler's output directory:

```bash
mkdir -p results/host/plots
python rprof-host/rprof-plotter-host.py \
  --input-dir results/host \
  --cpu --memory --disk --network \
  --start_point 0 --final_point 120 \
  --output_dir results/host/plots
```

Its options are the same as the process plotter, except that it also supports `-n`, `--network` to generate network charts. In particular, `--input-dir` is required, `--output_dir` defaults to the input directory, and `--start_point`/`--final_point` select an elapsed-time window.

Generated host charts:

- Memory: `MemoryUsage.png`, `Cached.png`, `Inactive.png`
- Disk: `DiskReadOps.png`, `DiskReadMiB.png`, `DiskWriteOps.png`, `DiskWriteMiB.png`
- CPU: `iowait.png`, `cpuusage.png`
- Network: `network_bytes_sent.png`, `network_bytes_received.png`

Disk and network counters are converted to changes between samples for the charts. Host disk read charts show changes in counts and MiB between samples, while disk write charts show counts per second and MiB per second. Network charts show MiB per second based on byte-counter differences and sample timestamps. The first point in a counter-difference chart is zero because there is no earlier sample to compare.

## Understanding the results

- **Sampling interval:** A shorter interval captures more changes but creates larger files and adds more monitoring overhead. The default is 1.5 seconds. Keep the interval consistent when comparing runs.
- **Cumulative counters vs. snapshots:** CPU time, disk I/O, and network I/O counters generally increase over time. Their differences across samples represent activity during that interval. Memory and per-core CPU usage are sampled values rather than cumulative totals.
- **Elapsed time:** Plotter x-axes start at 0 seconds at the first sample. `--start_point` and `--final_point` filter that elapsed-time range; the final point is inclusive.
- **MiB:** Charts labeled MiB use mebibytes (1 MiB = 1,048,576 bytes), not decimal megabytes.
- **Host versus process data:** Host-wide disk and network activity includes other applications and system services. It should not be interpreted as the profiled process's own I/O.
- **Chart files:** PNGs with the same names are overwritten if you plot again to the same output directory.

## Troubleshooting

- **`ModuleNotFoundError` for `psutil` or `matplotlib`:** Activate the virtual environment and install the dependencies with `python -m pip install psutil matplotlib`.
- **Output file or plot cannot be created:** Create the output directory first and check that you have permission to write there.
- **Plotter reports a missing CSV file:** Confirm that you enabled that collection option and that `--input-dir` points to the profiler output directory.
- **A metric is missing or unavailable:** `psutil` exposes different counters on different operating systems and permissions levels. Try a supported metric, or inspect the CSV header to see what was recorded.
- **Process CPU plotting fails on an `iowait` field:** The process plotter's CPU option expects `iowait` in `cpu.csv`; this field is not provided by every platform's process CPU metrics. The collector cannot add a field the operating system does not expose.
- **Host profiler does not stop immediately:** It polls `.mon` every 10 samples; wait for the next check after writing `1`.
- **Very short process creates little data:** The collector may only have time for a few samples before the command exits. Use a longer-running workload or a shorter interval when suitable.

## Notes

- Choose at least one collection option when starting a profiler and at least one chart option when running a plotter.
- Run the plotter only after the selected CSV files have been collected. A plotter cannot generate a chart for a metric whose CSV file is missing or empty.
- `psutil` metrics vary by operating system. Some process-level counters or memory details may be unavailable on a particular platform.
- The CSV timestamps use local time; chart time axes show elapsed seconds from the first sample.
