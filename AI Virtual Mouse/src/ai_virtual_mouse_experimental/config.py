from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """Raised when experimental configuration is missing or invalid."""


@dataclass(frozen=True)
class AppSettings:
    name: str
    default_mode: str
    default_condition: str
    safe_startup: bool
    allow_real_mouse: bool


@dataclass(frozen=True)
class BackendSettings:
    name: str
    camera_index: int
    camera_width: int
    camera_height: int
    model_path: str
    model_url: str
    auto_download_model: bool


@dataclass(frozen=True)
class ModeSettings:
    description: str
    requires_camera: bool
    controls_real_mouse: bool


@dataclass(frozen=True)
class ConditionSettings:
    backend: str
    gesture_profile: str
    smoothing_strategy: str
    debounce_enabled: bool
    calibration_enabled: bool


@dataclass(frozen=True)
class BenchmarkSettings:
    name: str
    window_width: int
    window_height: int
    target_count: int
    target_radius: int
    random_seed: int
    countdown_seconds: int


@dataclass(frozen=True)
class GestureSettings:
    move_finger: str
    click_gesture: str
    click_threshold_px: int
    drag_gesture: str
    scroll_gesture: str
    pause_gesture: str


@dataclass(frozen=True)
class OutputSettings:
    root_dir: str
    csv_dir: str
    plot_dir: str
    report_dir: str


@dataclass(frozen=True)
class ExperimentalConfig:
    app: AppSettings
    backend: BackendSettings
    modes: dict[str, ModeSettings]
    conditions: dict[str, ConditionSettings]
    benchmark: BenchmarkSettings
    gesture: GestureSettings
    output: OutputSettings

    def get_mode(self, name: str) -> ModeSettings:
        try:
            return self.modes[name]
        except KeyError as exc:
            options = ", ".join(sorted(self.modes))
            raise ConfigError(f"Unknown mode '{name}'. Available modes: {options}") from exc

    def get_condition(self, name: str) -> ConditionSettings:
        try:
            return self.conditions[name]
        except KeyError as exc:
            options = ", ".join(sorted(self.conditions))
            raise ConfigError(
                f"Unknown condition '{name}'. Available conditions: {options}"
            ) from exc


def load_config(path: Path) -> ExperimentalConfig:
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    with path.open("rb") as config_file:
        raw = tomllib.load(config_file)

    config = parse_config(raw)
    validate_config(config)
    return config


def parse_config(raw: dict) -> ExperimentalConfig:
    try:
        modes = {
            name: ModeSettings(**value) for name, value in raw["modes"].items()
        }
        conditions = {
            name: ConditionSettings(**value)
            for name, value in raw["conditions"].items()
        }
        return ExperimentalConfig(
            app=AppSettings(**raw["app"]),
            backend=BackendSettings(**raw["backend"]),
            modes=modes,
            conditions=conditions,
            benchmark=BenchmarkSettings(**raw["benchmark"]),
            gesture=GestureSettings(**raw["gesture"]),
            output=OutputSettings(**raw["output"]),
        )
    except KeyError as exc:
        raise ConfigError(f"Missing required configuration section: {exc.args[0]}") from exc
    except TypeError as exc:
        raise ConfigError(f"Invalid configuration shape: {exc}") from exc


def validate_config(config: ExperimentalConfig) -> None:
    config.get_mode(config.app.default_mode)
    config.get_condition(config.app.default_condition)

    if config.backend.camera_width <= 0 or config.backend.camera_height <= 0:
        raise ConfigError("Camera dimensions must be positive integers.")
    if config.benchmark.target_count <= 0:
        raise ConfigError("Benchmark target_count must be greater than zero.")
    if config.benchmark.target_radius <= 0:
        raise ConfigError("Benchmark target_radius must be greater than zero.")
    if config.gesture.click_threshold_px <= 0:
        raise ConfigError("Gesture click_threshold_px must be greater than zero.")
