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

Run one session with keyboard controls:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline
```

Run one session with hand input:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline --hand-input
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition improved --hand-input
```

Generate a comparison report from saved sessions:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --compare-sessions outputs/sessions/session-a outputs/sessions/session-b
```

## Hand-Driven Benchmark

When `--hand-input` is passed, the benchmark uses webcam hand gestures to drive the simulated Pygame cursor. The cursor remains simulated and the OS mouse is never moved during benchmark evaluation.

The hand-control pipeline shared with the Real Mouse Runtime processes each camera frame and produces cursor movement and click intent. The benchmark applies these to the simulated cursor position.

Baseline hand benchmark uses tutorial-style gestures (index-only move, index+middle pinch click, no pause, no debounce). Improved hand benchmark uses the modern gesture profile (Stable Pinch Click, adaptive smoothing, debounce, pause toggle).

Keyboard/mouse controls remain available as fallback even when hand input is active.

### Hand-Input Metadata

When hand input is used, `metadata.json` includes a `hand_input` section recording:

- gesture profile used (baseline, simple, or improved)
- configured backend and backend actually used
- fallback reason (if any)
- smoothing strategy, debounce, and calibration flags
- technical metrics: cursor path length, mean FPS, jitter estimate

This ensures research artifacts are unambiguous about how the benchmark was controlled.

## Generated Metrics

Each report includes:

- total trials,
- hits and misses,
- hit rate,
- false clicks,
- total click count,
- mean and median completion time,
- jitter estimate based on target-center click distance,
- mean FPS when available,
- cursor path length (hand-input sessions),
- movement jitter estimate (hand-input sessions).

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

Do not claim general mouse-replacement superiority from benchmark results alone. The benchmark evaluates a specific controlled task under specific conditions.
