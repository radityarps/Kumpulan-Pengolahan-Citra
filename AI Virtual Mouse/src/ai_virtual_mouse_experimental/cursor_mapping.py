from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Bounds:
    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def validate(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Bounds must have positive width and height.")


@dataclass(frozen=True)
class CalibrationConfig:
    margin_px: float = 24.0
    min_width_px: float = 80.0
    min_height_px: float = 80.0


@dataclass(frozen=True)
class SmoothingConfig:
    fixed_factor: float = 7.0
    min_factor: float = 3.0
    max_factor: float = 12.0
    fast_movement_threshold_px: float = 260.0


def default_camera_bounds(width: int, height: int, frame_reduction: int = 100) -> Bounds:
    return Bounds(
        left=frame_reduction,
        top=frame_reduction,
        right=width - frame_reduction,
        bottom=height - frame_reduction,
    )


def calibrate_bounds(samples: list[Point], config: CalibrationConfig | None = None) -> Bounds:
    if not samples:
        raise ValueError("Calibration requires at least one sample point.")

    cfg = config or CalibrationConfig()
    min_x = min(point.x for point in samples) - cfg.margin_px
    max_x = max(point.x for point in samples) + cfg.margin_px
    min_y = min(point.y for point in samples) - cfg.margin_px
    max_y = max(point.y for point in samples) + cfg.margin_px

    if max_x - min_x < cfg.min_width_px:
        center_x = (min_x + max_x) / 2
        min_x = center_x - cfg.min_width_px / 2
        max_x = center_x + cfg.min_width_px / 2
    if max_y - min_y < cfg.min_height_px:
        center_y = (min_y + max_y) / 2
        min_y = center_y - cfg.min_height_px / 2
        max_y = center_y + cfg.min_height_px / 2

    return Bounds(left=min_x, top=min_y, right=max_x, bottom=max_y)


def map_point_to_output(point: Point, source: Bounds, output_width: int, output_height: int) -> Point:
    source.validate()
    clamped_x = min(max(point.x, source.left), source.right)
    clamped_y = min(max(point.y, source.top), source.bottom)
    mapped_x = (clamped_x - source.left) / source.width * output_width
    mapped_y = (clamped_y - source.top) / source.height * output_height
    return Point(mapped_x, mapped_y)


def fixed_smooth(previous: Point, target: Point, factor: float = 7.0) -> Point:
    if factor <= 0:
        raise ValueError("Smoothing factor must be positive.")
    return Point(
        x=previous.x + (target.x - previous.x) / factor,
        y=previous.y + (target.y - previous.y) / factor,
    )


def adaptive_smooth(
    previous: Point,
    target: Point,
    config: SmoothingConfig | None = None,
) -> Point:
    cfg = config or SmoothingConfig()
    movement = math.hypot(target.x - previous.x, target.y - previous.y)
    if cfg.fast_movement_threshold_px <= 0:
        factor = cfg.fixed_factor
    else:
        speed_ratio = min(1.0, movement / cfg.fast_movement_threshold_px)
        factor = cfg.max_factor - (cfg.max_factor - cfg.min_factor) * speed_ratio
    factor = min(max(factor, cfg.min_factor), cfg.max_factor)
    return fixed_smooth(previous, target, factor)


def select_mapping_bounds(
    calibration_enabled: bool,
    calibrated_bounds: Bounds | None,
    fallback_bounds: Bounds,
) -> Bounds:
    if calibration_enabled and calibrated_bounds is not None:
        return calibrated_bounds
    return fallback_bounds


def apply_smoothing(
    strategy: str,
    previous: Point,
    target: Point,
    config: SmoothingConfig | None = None,
) -> Point:
    if strategy == "adaptive":
        return adaptive_smooth(previous, target, config)
    if strategy == "fixed":
        return fixed_smooth(previous, target, (config or SmoothingConfig()).fixed_factor)
    if strategy == "none":
        return target
    raise ValueError(f"Unknown smoothing strategy: {strategy}")
