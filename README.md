# MLPerf-Prof

Common profiling utilities for MLPerf-HPC using [timemory](https://github.com/NERSC/timemory).

## Overview

- Command-line options
- Decorators
- Context-managers
- Basic timers

## Usage

This package is designed to work regardless of whether or not [timemory](https://github.com/NERSC/timemory)
in installed.

```python
#!/usr/bin/env python

import sys
import argparse
import traceback
import mlperf_prof


def parse_args():
    parser = argparse.ArgumentParser('example')
    parser.add_argument('--test', action='store_true',
                        help='Test adding user options')

    '''add the mlperf command-line options'''
    args = mlperf_prof.parse_args(parser)
    if args.test:
        print('Testing...')


def fibonacci(n):
    return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)


@mlperf_prof.marker(['wall_clock', 'cpu_clock'], mode='full')
def main():
    '''Use decorator with wall-clock and cpu-clock components
    Set the mode to full which writes the function name, line number
    and file instead of just the function
    '''
    import time

    '''Use a manual wall-clock timer'''
    t = mlperf_prof.timer('wall')
    t.start()
    '''Use the full function profiler as a context-manager'''
    with mlperf_prof.profile():
        fibonacci(10)
    t.stop()
    print('\nmanual timer: {} {}\n'.format(t.get(), t.display_units()))


if __name__ == '__main__':
    try:
        parse_args()
        main()
        '''Finalize the results before exiting'''
        mlperf_prof.finalize()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
```

### Command Line Options

```python
$ python3.7 ./examples/basic.py --help
usage: example [-h] [--test] [--disable-prof] [-c METRICS [METRICS ...]] [-P]
               [-T] [--perf-output-dir PERF_OUTPUT_DIR]
               [--perf-output-mode {text,json,cout,flamegraph,plot} [{text,json,cout,flamegraph,plot} ...]]

optional arguments:
  -h, --help            show this help message and exit
  --test                Test adding user options
  --disable-prof        Disable performance analysis
  -c METRICS [METRICS ...], --metrics METRICS [METRICS ...]
                        Select metrics to collect
  -P, --profile         Enable full Python profiling
  -T, --trace           Enable full Python tracing (line-by-line)
  --perf-output-dir PERF_OUTPUT_DIR
                        Output directory
  --perf-output-mode {text,json,cout,flamegraph,plot} [{text,json,cout,flamegraph,plot} ...]
                        Output types
```

### Example

- Execute with `wall_clock` and `peak_rss` components
- Set the output modes to text and json

```console
$ python3.7 ./examples/basic.py -c wall_clock peak_rss --perf-output-mode text json

manual timer: 0.005261713 sec

[cpu]|0> Outputting 'timemory-basic-output/cpu.json'...
[cpu]|0> Outputting 'timemory-basic-output/cpu.txt'...

[wall]|0> Outputting 'timemory-basic-output/wall.json'...
[wall]|0> Outputting 'timemory-basic-output/wall.txt'...

[peak_rss]|0> Outputting 'timemory-basic-output/peak_rss.json'...
[peak_rss]|0> Outputting 'timemory-basic-output/peak_rss.txt'...
```

### Expected Output

- `wall_clock` component was explicitly listed in decorator and selected via command-line
- The decorator components are evaluated before command-line args are applied --> fixed
- Profiling components in context-manager were set via command-line args

```console
$ cat timemory-basic-output/wall.txt
|---------------------------------------------------------------------------------------------------------------------------------------|
|                                                REAL-CLOCK TIMER (I.E. WALL-CLOCK TIMER)                                               |
|---------------------------------------------------------------------------------------------------------------------------------------|
|                   LABEL                     | COUNT  | DEPTH  | METRIC | UNITS  |  SUM   | MEAN   |  MIN   |  MAX   | STDDEV | % SELF |
|---------------------------------------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| >>> main/__init__.py:77                     |      1 |      0 | wall   | sec    |  0.005 |  0.005 |  0.005 |  0.005 |  0.000 |   11.7 |
| >>> |_fibonacci@basic.py:20                 |      2 |      1 | wall   | sec    |  0.005 |  0.002 |  0.002 |  0.003 |  0.001 |    2.1 |
| >>>   |_fibonacci@basic.py:20               |      4 |      2 | wall   | sec    |  0.005 |  0.001 |  0.001 |  0.002 |  0.001 |    5.1 |
| >>>     |_fibonacci@basic.py:20             |      8 |      3 | wall   | sec    |  0.004 |  0.001 |  0.000 |  0.001 |  0.000 |    8.2 |
| >>>       |_fibonacci@basic.py:20           |     16 |      4 | wall   | sec    |  0.004 |  0.000 |  0.000 |  0.001 |  0.000 |   17.6 |
| >>>         |_fibonacci@basic.py:20         |     32 |      5 | wall   | sec    |  0.003 |  0.000 |  0.000 |  0.000 |  0.000 |   36.2 |
| >>>           |_fibonacci@basic.py:20       |     52 |      6 | wall   | sec    |  0.002 |  0.000 |  0.000 |  0.000 |  0.000 |   58.6 |
| >>>             |_fibonacci@basic.py:20     |     44 |      7 | wall   | sec    |  0.001 |  0.000 |  0.000 |  0.000 |  0.000 |   75.9 |
| >>>               |_fibonacci@basic.py:20   |     16 |      8 | wall   | sec    |  0.000 |  0.000 |  0.000 |  0.000 |  0.000 |   86.3 |
| >>>                 |_fibonacci@basic.py:20 |      2 |      9 | wall   | sec    |  0.000 |  0.000 |  0.000 |  0.000 |  0.000 |  100.0 |
|---------------------------------------------------------------------------------------------------------------------------------------|
```

- `peak_rss` was added to profiling components via command-line arg
- The decorator components are evaluated before command-line args are applied

```console
$ cat timemory-basic-output/peak_rss.txt
|---------------------------------------------------------------------------------------------------------------------------------------|
|           MEASURES CHANGES IN THE HIGH-WATER MARK FOR THE AMOUNT OF MEMORY ALLOCATED IN RAM. MAY FLUCTUATE IF SWAP IS ENABLED         |
|---------------------------------------------------------------------------------------------------------------------------------------|
|                  LABEL                    | COUNT  | DEPTH  | METRIC   | UNITS  |  SUM   | MEAN   |  MIN   |  MAX   | STDDEV | % SELF |
|-------------------------------------------|--------|--------|----------|--------|--------|--------|--------|--------|--------|--------|
| >>> fibonacci@basic.py:20                 |      3 |      0 | peak_rss | MB     |  0.025 |  0.008 |  0.000 |  0.025 |  0.017 |    0.0 |
| >>> |_fibonacci@basic.py:20               |      5 |      1 | peak_rss | MB     |  0.025 |  0.005 |  0.000 |  0.025 |  0.012 |    0.0 |
| >>>   |_fibonacci@basic.py:20             |      9 |      2 | peak_rss | MB     |  0.025 |  0.003 |  0.000 |  0.025 |  0.009 |    0.0 |
| >>>     |_fibonacci@basic.py:20           |     17 |      3 | peak_rss | MB     |  0.025 |  0.001 |  0.000 |  0.025 |  0.006 |    0.0 |
| >>>       |_fibonacci@basic.py:20         |     33 |      4 | peak_rss | MB     |  0.025 |  0.001 |  0.000 |  0.025 |  0.004 |   16.7 |
| >>>         |_fibonacci@basic.py:20       |     53 |      5 | peak_rss | MB     |  0.020 |  0.000 |  0.000 |  0.020 |  0.003 |   20.0 |
| >>>           |_fibonacci@basic.py:20     |     45 |      6 | peak_rss | MB     |  0.016 |  0.000 |  0.000 |  0.016 |  0.002 |    0.0 |
| >>>             |_fibonacci@basic.py:20   |     17 |      7 | peak_rss | MB     |  0.016 |  0.001 |  0.000 |  0.016 |  0.004 |  100.0 |
| >>>               |_fibonacci@basic.py:20 |      2 |      8 | peak_rss | MB     |  0.000 |  0.000 |  0.000 |  0.000 |  0.000 |    0.0 |
|---------------------------------------------------------------------------------------------------------------------------------------|
```

- `cpu_clock` was explicitly added to decorator

```console
$ cat timemory-basic-output/cpu.txt
|-------------------------------------------------------------------------------------------------------------------|
|                                 TOTAL CPU TIME SPENT IN BOTH USER- AND KERNEL-MODE                                |
|-------------------------------------------------------------------------------------------------------------------|
|         LABEL           | COUNT  | DEPTH  | METRIC | UNITS  |  SUM   | MEAN   |  MIN   |  MAX   | STDDEV | % SELF |
|-------------------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| >>> main/__init__.py:77 |      1 |      0 | cpu    | sec    |  0.000 |  0.000 |  0.000 |  0.000 |  0.000 |    0.0 |
|-------------------------------------------------------------------------------------------------------------------|
```
