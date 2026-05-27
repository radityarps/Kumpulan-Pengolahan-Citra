from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from uuid import uuid4

from .app import RuntimePlan
from .benchmark_grid import PointClickBenchmarkState, TrialResult
from .config import ExperimentalConfig


@dataclass(frozen=True)
class BenchmarkSessionPaths:
    session_id: str
    session_dir: Path
    metadata_path: Path
    trials_csv_path: Path
    report_path: Path
    completion_plot_path: Path


TRIAL_FIELDNAMES = [
    "session_id",
    "condition",
    "backend",
    "mode",
    "gesture_profile",
    "smoothing_strategy",
    "debounce_enabled",
    "calibration_enabled",
    "benchmark_name",
    "window_width",
    "window_height",
    "target_count",
    "target_radius",
    "random_seed",
    "trial_index",
    "target_x",
    "target_y",
    "click_x",
    "click_y",
    "hit",
    "completion_time_s",
    "false_clicks_before_hit",
]


def utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def create_session_paths(
    config: ExperimentalConfig,
    plan: RuntimePlan,
    output_root: Path | None = None,
    session_id: str | None = None,
) -> BenchmarkSessionPaths:
    resolved_session_id = session_id or f"{utc_timestamp()}-{uuid4().hex[:8]}"
    root = output_root or Path(config.output.root_dir)
    session_dir = root / "sessions" / resolved_session_id
    session_dir.mkdir(parents=True, exist_ok=False)

    return BenchmarkSessionPaths(
        session_id=resolved_session_id,
        session_dir=session_dir,
        metadata_path=session_dir / "metadata.json",
        trials_csv_path=session_dir / "trials.csv",
        report_path=session_dir / "report.md",
        completion_plot_path=session_dir / "completion_times.svg",
    )


def build_session_metadata(
    config: ExperimentalConfig,
    plan: RuntimePlan,
    paths: BenchmarkSessionPaths,
) -> dict:
    return {
        "session_id": paths.session_id,
        "created_at_utc": utc_timestamp(),
        "mode": plan.mode,
        "condition": plan.condition,
        "backend": plan.backend,
        "safe_startup": plan.safe_startup,
        "controls_real_mouse": plan.controls_real_mouse,
        "requires_camera": plan.requires_camera,
        "runtime_metadata": plan.metadata,
        "benchmark": asdict(config.benchmark),
        "gesture": asdict(config.gesture),
        "debounce": asdict(config.debounce),
        "output": {
            "session_dir": str(paths.session_dir),
            "metadata_path": str(paths.metadata_path),
            "trials_csv_path": str(paths.trials_csv_path),
            "report_path": str(paths.report_path),
            "completion_plot_path": str(paths.completion_plot_path),
        },
    }


def write_session_metadata(
    config: ExperimentalConfig,
    plan: RuntimePlan,
    paths: BenchmarkSessionPaths,
) -> Path:
    metadata = build_session_metadata(config, plan, paths)
    paths.metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
    )
    return paths.metadata_path


def trial_to_row(
    result: TrialResult,
    config: ExperimentalConfig,
    plan: RuntimePlan,
    session_id: str,
) -> dict:
    return {
        "session_id": session_id,
        "condition": plan.condition,
        "backend": plan.backend,
        "mode": plan.mode,
        "gesture_profile": plan.metadata.get("gesture_profile"),
        "smoothing_strategy": plan.metadata.get("smoothing_strategy"),
        "debounce_enabled": plan.metadata.get("debounce_enabled"),
        "calibration_enabled": plan.metadata.get("calibration_enabled"),
        "benchmark_name": config.benchmark.name,
        "window_width": config.benchmark.window_width,
        "window_height": config.benchmark.window_height,
        "target_count": config.benchmark.target_count,
        "target_radius": config.benchmark.target_radius,
        "random_seed": config.benchmark.random_seed,
        "trial_index": result.trial_index,
        "target_x": result.target_x,
        "target_y": result.target_y,
        "click_x": result.click_x,
        "click_y": result.click_y,
        "hit": result.hit,
        "completion_time_s": result.completion_time_s,
        "false_clicks_before_hit": result.false_clicks_before_hit,
    }


def write_trials_csv(
    state: PointClickBenchmarkState,
    config: ExperimentalConfig,
    plan: RuntimePlan,
    paths: BenchmarkSessionPaths,
) -> Path:
    with paths.trials_csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=TRIAL_FIELDNAMES)
        writer.writeheader()
        for result in state.results:
            writer.writerow(trial_to_row(result, config, plan, paths.session_id))
    return paths.trials_csv_path


def persist_benchmark_session(
    state: PointClickBenchmarkState,
    config: ExperimentalConfig,
    plan: RuntimePlan,
    output_root: Path | None = None,
    generate_report: bool = True,
) -> BenchmarkSessionPaths:
    paths = create_session_paths(config, plan, output_root=output_root)
    write_session_metadata(config, plan, paths)
    write_trials_csv(state, config, plan, paths)
    if generate_report:
        benchmark_report = import_module(
            "ai_virtual_mouse_experimental.benchmark_report"
        )
        benchmark_report.generate_report_from_session(paths.session_dir)
    return paths


def format_output_paths(paths: BenchmarkSessionPaths) -> str:
    return "\n".join(
        (
            "Benchmark output written:",
            f"- session: {paths.session_dir}",
            f"- metadata: {paths.metadata_path}",
            f"- trials CSV: {paths.trials_csv_path}",
            f"- report: {paths.report_path}",
            f"- completion plot: {paths.completion_plot_path}",
        )
    )
