from __future__ import annotations

import argparse
import json
from importlib import import_module
from pathlib import Path

from .app import StartupError, build_runtime_plan, describe_plan
from .config import ConfigError, load_config


DEFAULT_CONFIG_PATH = Path("config/experimental.toml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-virtual-mouse-experimental",
        description="Run the experimental AI Virtual Mouse research prototype skeleton.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the experimental TOML configuration file.",
    )
    parser.add_argument(
        "--mode",
        help="Named app mode to run. Defaults to app.default_mode from config.",
    )
    parser.add_argument(
        "--condition",
        help="Named experimental condition. Defaults to app.default_condition from config.",
    )
    parser.add_argument(
        "--allow-real-mouse",
        action="store_true",
        help="Permit modes that control the real OS mouse.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available modes and conditions, then exit.",
    )
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="Print selected runtime metadata as JSON, then exit.",
    )
    parser.add_argument(
        "--download-model",
        action="store_true",
        help="Download the MediaPipe Tasks HandLandmarker model, then exit.",
    )
    parser.add_argument(
        "--overwrite-model",
        action="store_true",
        help="Re-download the HandLandmarker model even when it already exists.",
    )
    parser.add_argument(
        "--smoke-backend",
        action="store_true",
        help="Initialize the selected MediaPipe Tasks backend and print metadata.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(Path(args.config))
        if args.list:
            print(format_config_options(config))
            return 0

        if args.download_model:
            tasks_backend = import_module("ai_virtual_mouse_experimental.tasks_backend")
            model_path = tasks_backend.download_hand_landmarker_model(
                config,
                overwrite=args.overwrite_model,
            )
            print(f"HandLandmarker model ready: {model_path}")
            return 0

        if args.smoke_backend:
            tasks_backend = import_module("ai_virtual_mouse_experimental.tasks_backend")
            metadata = tasks_backend.smoke_test_tasks_backend(config)
            print(json.dumps(metadata.__dict__, indent=2, sort_keys=True))
            return 0

        plan = build_runtime_plan(
            config=config,
            mode_name=args.mode,
            condition_name=args.condition,
            allow_real_mouse=args.allow_real_mouse,
        )
        if args.metadata:
            print(json.dumps(plan.metadata, indent=2, sort_keys=True))
            return 0
    except (ConfigError, StartupError, RuntimeError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(describe_plan(plan))

    try:
        if plan.mode == "benchmark":
            benchmark_shell = import_module("ai_virtual_mouse_experimental.benchmark_shell")
            return benchmark_shell.run_pygame_benchmark_shell(config, plan)

        if plan.mode == "demo" and plan.condition == "baseline":
            baseline = import_module("ai_virtual_mouse_experimental.baseline")
            metadata = baseline.build_baseline_metadata(config, plan)
            print(f"Baseline metadata: {metadata}")
            return baseline.run_frozen_video_baseline(config, plan)
    except RuntimeError as exc:
        parser.exit(2, f"error: {exc}\n")

    print(
        "Skeleton startup complete. Runtime loop is intentionally not implemented "
        "for this mode yet."
    )
    return 0


def format_config_options(config) -> str:
    lines = ["Available modes:"]
    for name, mode in sorted(config.modes.items()):
        lines.append(f"- {name}: {mode.description}")

    lines.append("")
    tasks_backend = import_module("ai_virtual_mouse_experimental.tasks_backend")
    metadata = tasks_backend.build_tasks_backend_metadata(config)
    lines.append("MediaPipe Tasks backend:")
    lines.append(f"- model path: {metadata.model_path}")
    lines.append(f"- model exists: {metadata.model_exists}")
    lines.append("")
    lines.append("Available conditions:")
    for name, condition in sorted(config.conditions.items()):
        flags = [
            f"backend={condition.backend}",
            f"smoothing={condition.smoothing_strategy}",
            f"debounce={condition.debounce_enabled}",
            f"calibration={condition.calibration_enabled}",
        ]
        lines.append(f"- {name}: " + ", ".join(flags))

    return "\n".join(lines)
