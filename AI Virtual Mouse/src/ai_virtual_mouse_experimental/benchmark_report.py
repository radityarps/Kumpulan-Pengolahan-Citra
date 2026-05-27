from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BenchmarkMetrics:
    total_trials: int
    hit_count: int
    miss_count: int
    hit_rate: float
    false_clicks: int
    click_count: int
    mean_completion_time_s: float
    median_completion_time_s: float
    jitter_estimate_px: float
    fps_mean: float | None = None


@dataclass(frozen=True)
class BenchmarkReportPaths:
    report_path: Path
    completion_plot_path: Path


def load_trials_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def load_metadata(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_metrics(rows: list[dict[str, str]], metadata: dict[str, Any] | None = None) -> BenchmarkMetrics:
    benchmark = (metadata or {}).get("benchmark", {})
    expected_trials = int(benchmark.get("target_count") or len(rows))
    hit_rows = [row for row in rows if row.get("hit") == "True"]
    hit_count = len(hit_rows)
    miss_count = max(0, expected_trials - hit_count)
    false_clicks = sum(int(float(row.get("false_clicks_before_hit") or 0)) for row in rows)
    completion_times = [float(row.get("completion_time_s") or 0.0) for row in hit_rows]
    distances = [
        _distance(
            float(row.get("target_x") or 0.0),
            float(row.get("target_y") or 0.0),
            float(row.get("click_x") or 0.0),
            float(row.get("click_y") or 0.0),
        )
        for row in hit_rows
    ]
    fps_values = [float(row["fps"]) for row in rows if row.get("fps")]

    return BenchmarkMetrics(
        total_trials=expected_trials,
        hit_count=hit_count,
        miss_count=miss_count,
        hit_rate=hit_count / expected_trials if expected_trials else 0.0,
        false_clicks=false_clicks,
        click_count=hit_count + false_clicks,
        mean_completion_time_s=_mean(completion_times),
        median_completion_time_s=statistics.median(completion_times) if completion_times else 0.0,
        jitter_estimate_px=_mean(distances),
        fps_mean=_mean(fps_values) if fps_values else None,
    )


def generate_completion_time_svg(rows: list[dict[str, str]], output_path: Path) -> Path:
    hit_rows = [row for row in rows if row.get("hit") == "True"]
    values = [float(row.get("completion_time_s") or 0.0) for row in hit_rows]
    width = 720
    height = 320
    padding = 46
    plot_width = width - padding * 2
    plot_height = height - padding * 2
    max_value = max(values) if values else 1.0
    bar_width = plot_width / max(1, len(values))

    bars = []
    for index, value in enumerate(values):
        bar_height = 0 if max_value == 0 else (value / max_value) * plot_height
        x = padding + index * bar_width
        y = height - padding - bar_height
        bars.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(2, bar_width - 4):.2f}" '
            f'height="{bar_height:.2f}" fill="#58a6ff" />'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#0d1117" />
  <text x="{padding}" y="28" fill="#f0f6fc" font-family="Arial" font-size="18">Completion Time per Hit Trial</text>
  <line x1="{padding}" y1="{height - padding}" x2="{width - padding}" y2="{height - padding}" stroke="#8b949e" />
  <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height - padding}" stroke="#8b949e" />
  {''.join(bars)}
  <text x="{padding}" y="{height - 14}" fill="#8b949e" font-family="Arial" font-size="12">trial index</text>
  <text x="{width - padding - 120}" y="{padding}" fill="#8b949e" font-family="Arial" font-size="12">max {max_value:.2f}s</text>
</svg>
'''
    output_path.write_text(svg, encoding="utf-8")
    return output_path


def generate_markdown_report(
    metadata: dict[str, Any],
    metrics: BenchmarkMetrics,
    plot_path: Path,
    output_path: Path,
) -> Path:
    fps_value = "not captured" if metrics.fps_mean is None else f"{metrics.fps_mean:.2f}"
    benchmark = metadata.get("benchmark", {})
    content = f"""# AI Virtual Mouse Benchmark Report

## Session

- Session ID: `{metadata.get('session_id', 'unknown')}`
- Condition: `{metadata.get('condition', 'unknown')}`
- Backend: `{metadata.get('backend', 'unknown')}`
- Mode: `{metadata.get('mode', 'unknown')}`
- Created at UTC: `{metadata.get('created_at_utc', 'unknown')}`

## Benchmark Parameters

- Benchmark: `{benchmark.get('name', 'unknown')}`
- Target count: `{benchmark.get('target_count', 'unknown')}`
- Target radius: `{benchmark.get('target_radius', 'unknown')}`
- Window: `{benchmark.get('window_width', 'unknown')} x {benchmark.get('window_height', 'unknown')}`
- Random seed: `{benchmark.get('random_seed', 'unknown')}`

## Summary Metrics

| Metric | Value |
|---|---:|
| Total trials | {metrics.total_trials} |
| Hits | {metrics.hit_count} |
| Misses | {metrics.miss_count} |
| Hit rate | {metrics.hit_rate:.2%} |
| False clicks | {metrics.false_clicks} |
| Click count | {metrics.click_count} |
| Mean completion time | {metrics.mean_completion_time_s:.3f}s |
| Median completion time | {metrics.median_completion_time_s:.3f}s |
| Jitter estimate | {metrics.jitter_estimate_px:.3f}px |
| Mean FPS | {fps_value} |

## Plots

![Completion time plot]({plot_path.name})

## Interpretation Notes

This report summarizes a controlled point-and-click benchmark. The jitter estimate is derived from hit click distance to target center when full cursor-path samples are not available. Claims should be limited to the benchmarked condition and task.
"""
    output_path.write_text(content, encoding="utf-8")
    return output_path


def generate_report_from_session(session_dir: Path) -> BenchmarkReportPaths:
    metadata_path = session_dir / "metadata.json"
    trials_path = session_dir / "trials.csv"
    metadata = load_metadata(metadata_path)
    rows = load_trials_csv(trials_path)
    metrics = compute_metrics(rows, metadata)
    plot_path = generate_completion_time_svg(rows, session_dir / "completion_times.svg")
    report_path = generate_markdown_report(metadata, metrics, plot_path, session_dir / "report.md")
    return BenchmarkReportPaths(report_path=report_path, completion_plot_path=plot_path)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
