from __future__ import annotations

import argparse
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(Path(args.config))
        if args.list:
            print(format_config_options(config))
            return 0

        plan = build_runtime_plan(
            config=config,
            mode_name=args.mode,
            condition_name=args.condition,
            allow_real_mouse=args.allow_real_mouse,
        )
    except (ConfigError, StartupError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(describe_plan(plan))
    print("Skeleton startup complete. Runtime loop is intentionally not implemented yet.")
    return 0


def format_config_options(config) -> str:
    lines = ["Available modes:"]
    for name, mode in sorted(config.modes.items()):
        lines.append(f"- {name}: {mode.description}")

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
