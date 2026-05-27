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

## Interpretation Limits

The benchmark measures controlled point-and-click usability. It can support claims about this benchmark task, such as completion time, hit rate, false clicks, and target-center click distance. It should not be used alone to claim that the virtual mouse is superior to a physical mouse or universally better for all desktop tasks.
