# Benchmark Methodology

The experimental branch compares final user experience in the same controlled point-and-click benchmark.

## Conditions

Run the same benchmark command with different `--condition` values:

- `baseline`: frozen video tutorial behavior.
- `smoothing_only`: baseline gestures with adaptive smoothing enabled.
- `debounce_only`: baseline gestures with click debouncing enabled.
- `calibration_only`: baseline gestures with calibrated mapping enabled.
- `improved`: full improved condition with modern backend metadata, adaptive smoothing, calibration, and debouncing.

## Fair Comparison Rule

All sessions used in one comparison should use the same benchmark configuration: target count, radius, random seed, and window size. The condition is the experimental treatment.

## Commands

Run one session:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline
```

Generate a comparison report from saved sessions:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --compare-sessions outputs/sessions/session-a outputs/sessions/session-b
```

## Generated Metrics

Each report includes:

- total trials,
- hits and misses,
- hit rate,
- false clicks,
- total click count,
- mean and median completion time,
- jitter estimate based on target-center click distance,
- mean FPS when available.

Generated artifacts per session:

- `metadata.json`: condition, backend, mode, benchmark parameters, gesture parameters, debounce parameters, and output paths.
- `trials.csv`: trial-level target/click/outcome rows.
- `completion_times.svg`: completion-time plot.
- `report.md`: session-level Markdown report.

## Automated Test Coverage

Pure logic has automated tests for target generation, benchmark trial state, CSV/session logging, metrics/report generation, gesture classification, calibration mapping, adaptive smoothing, and click debouncing. Camera and OS mouse behavior remain boundary integrations and should be smoke-tested manually.

## Real Mouse Runtime vs Benchmark Runtime

The **Real Mouse Runtime** controls the actual OS cursor and is used for the live demo. The **Benchmark Runtime** uses a simulated cursor inside Pygame and is used for controlled measurement. They share the same hand-control pipeline where practical, but the benchmark does not move the OS mouse for safety and measurement accuracy.

## Interpretation Limits

The benchmark measures controlled point-and-click usability. It can support claims about this benchmark task, such as completion time, hit rate, false clicks, and target-center click distance. It should not be used alone to claim that the virtual mouse is superior to a physical mouse or universally better for all desktop tasks.
