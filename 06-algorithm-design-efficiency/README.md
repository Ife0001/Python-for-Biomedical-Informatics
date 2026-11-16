# Algorithm Design and Efficiency: Sorting Healthcare-Scale Numeric Data

**Python · Data Structures · Sorting Algorithms · Reproducible Benchmarking · Validation**

## Overview

This educational portfolio project evaluates alternative sorting strategies on **synthetic numerical arrays** intended to illustrate computational design considerations in healthcare-data workflows. No patient records are processed. The work adapts the algorithmic concepts from the author's BMI 5007 quicksort assignment into an independently structured and tested application.

## Analytical question

How do first-element pivot quicksort, randomly selected pivot quicksort, and Python's built-in sorting algorithm compare across input sizes and initial arrangements?

## Methods

- **First-pivot quicksort:** deterministic selection of the first element in each partition.
- **Random-pivot quicksort:** seeded pseudorandom pivot selection for repeatability.
- **Python `sorted`:** optimized built-in reference, included as a practical comparison; implemented in C and not a like-for-like pure-Python algorithm.
- **Three-way partitioning:** groups values less than, equal to, and greater than the pivot, reducing unnecessary work for repeated values.
- **Iterative processing:** uses an explicit stack to avoid recursion-limit failures.
- **Input types:** random integers, already sorted, reverse sorted, and identical integers.
- **Measures:** elapsed time in milliseconds using `perf_counter_ns`, summarized by the median, minimum, and maximum across multiple runs.
- **Correctness:** every algorithm output is checked against Python's `sorted` result on the same data before timings are saved.

## Repository structure

```text
06-algorithm-design-efficiency/
├── .gitignore
├── README.md
├── src/
│   ├── algorithms.py
│   └── benchmark.py
├── tests/
│   └── test_algorithms.py
├── data/
├── outputs/
└── figures/
```

## Run locally

Python 3.10 or newer; **no third-party packages required**. From the project directory:

```bash
python -m unittest discover -s tests -v
python src/benchmark.py
```

To customize the test sizes, trial count, or random seed:

```bash
python src/benchmark.py --sizes 100 500 1000 --trials 5 --seed 42
```

The script writes:

- `outputs/sorting_benchmarks.csv`: timing summaries for each data type, size, and algorithm.
- `outputs/benchmark_metadata.json`: run configuration and verification status.
- `figures/random_array_sorting.svg`: a locally generated SVG chart showing median times for random arrays of the largest selected size.

Generated results are git-ignored because absolute timings vary across computers and Python versions.

## Interpretation and limitations

- **Correctness and speed are separate:** a sorter must return the correct ordering before its speed is meaningful.
- First-element pivot choice can create very uneven partitions on already ordered arrays; randomized selection generally makes it less sensitive to existing order, though no individual run is guaranteed faster.
- Three-way partitioning improves handling of identical values.
- Wall-clock timings vary with hardware, machine load, interpreter, and measurement noise; short timings are especially noisy. For rigorous benchmarking, use isolated environments, larger samples, warm-up, and confidence intervals.
- The benchmark uses synthetic integer arrays, **not real clinical data**. Results do not establish speed or safety for EHR platforms, clinical workflows, or production deployments.

## Origin

This project independently reorganizes and extends algorithm concepts from BMI 5007 coursework. Original assignment code and instructor templates are not included in the public portfolio version.
