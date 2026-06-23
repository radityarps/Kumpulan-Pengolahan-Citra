from __future__ import annotations

from dataclasses import dataclass, field
from importlib.util import find_spec
from typing import Any

from .config import ExperimentalConfig


@dataclass(frozen=True)
class RuntimePlan:
    mode: str
    condition: str
    backend: str
    safe_startup: bool
    controls_real_mouse: bool
    requires_camera: bool
    output_root: str
    metadata: dict[str, Any] = field(default_factory=dict)


class StartupError(RuntimeError):
    """Raised when the experimental app cannot start safely."""


def build_runtime_plan(
    config: ExperimentalConfig,
    mode_name: str | None = None,
    condition_name: str | None = None,
    allow_real_mouse: bool = False,
) -> RuntimePlan:
    mode_key = mode_name or config.app.default_mode
    condition_key = condition_name or config.app.default_condition

    mode = config.get_mode(mode_key)
    condition = config.get_condition(condition_key)
    backend_name = condition.backend

    controls_real_mouse = mode.controls_real_mouse
    if controls_real_mouse and not (config.app.allow_real_mouse or allow_real_mouse):
        raise StartupError(
            "Selected mode controls the real OS mouse. Re-run with "
            "--allow-real-mouse only when you intentionally want that behavior."
        )

    if mode.requires_camera:
        missing = missing_dependencies(("cv2", "mediapipe"))
        if missing:
            joined = ", ".join(missing)
            raise StartupError(
                f"Selected mode requires camera tracking dependencies: {joined}. "
                "Install project requirements before running this mode."
            )

    return RuntimePlan(
        mode=mode_key,
        condition=condition_key,
        backend=backend_name,
        safe_startup=config.app.safe_startup,
        controls_real_mouse=controls_real_mouse,
        requires_camera=mode.requires_camera,
        output_root=config.output.root_dir,
        metadata={
            "condition": condition_key,
            "backend": backend_name,
            "gesture_profile": condition.gesture_profile,
            "smoothing_strategy": condition.smoothing_strategy,
            "debounce_enabled": condition.debounce_enabled,
            "debounce_parameters": {
                "stable_frames_required": config.debounce.stable_frames_required,
                "release_frames_required": config.debounce.release_frames_required,
                "cooldown_seconds": config.debounce.cooldown_seconds,
            },
            "calibration_enabled": condition.calibration_enabled,
            "benchmark_name": config.benchmark.name,
        },
    )


def missing_dependencies(module_names: tuple[str, ...]) -> list[str]:
    return [
        module_name for module_name in module_names if find_spec(module_name) is None
    ]


def describe_plan(plan: RuntimePlan) -> str:
    real_mouse = "enabled" if plan.controls_real_mouse else "disabled"
    camera = "required" if plan.requires_camera else "not required"
    return "\n".join(
        (
            "Experimental AI Virtual Mouse startup plan",
            f"- mode: {plan.mode}",
            f"- condition: {plan.condition}",
            f"- backend: {plan.backend}",
            f"- safe startup: {plan.safe_startup}",
            f"- real OS mouse control: {real_mouse}",
            f"- camera: {camera}",
            f"- output root: {plan.output_root}",
            f"- gesture profile: {plan.metadata.get('gesture_profile')}",
            f"- smoothing strategy: {plan.metadata.get('smoothing_strategy')}",
            f"- debounce enabled: {plan.metadata.get('debounce_enabled')}",
            f"- calibration enabled: {plan.metadata.get('calibration_enabled')}",
        )
    )
