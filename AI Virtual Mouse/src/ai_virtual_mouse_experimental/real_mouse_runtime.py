from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any

from .app import RuntimePlan
from .config import ExperimentalConfig
from .hand_control_pipeline import (
    HandControlFrame,
    HandControlPipeline,
)


@dataclass(frozen=True)
class RuntimeSnapshot:
    gesture_name: str = "idle"
    paused: bool = False
    click_ready: bool = False
    backend_used: str = "unknown"
    fps: float = 0.0
    cursor_x: float = 0.0
    cursor_y: float = 0.0


@dataclass(frozen=True)
class MouseController:
    width: int
    height: int
    backend: str
    move: Any
    click: Any


def build_real_mouse_metadata(
    config: ExperimentalConfig, plan: RuntimePlan
) -> dict[str, Any]:
    condition = config.get_condition(plan.condition)
    return {
        "condition": plan.condition,
        "backend": condition.backend,
        "backend_preference": "mediapipe_tasks",
        "backend_fallback_allowed": True,
        "gesture_profile": condition.gesture_profile,
        "real_mouse_profile": "simple_move_click_pause",
        "smoothing_strategy": condition.smoothing_strategy,
        "debounce_enabled": condition.debounce_enabled,
        "debounce_parameters": {
            "stable_frames_required": config.debounce.stable_frames_required,
            "release_frames_required": config.debounce.release_frames_required,
            "cooldown_seconds": config.debounce.cooldown_seconds,
        },
        "calibration_enabled": condition.calibration_enabled,
        "safety_controls": ["keyboard_quit", "pause_toggle", "corner_failsafe"],
    }


def _create_mouse_controller() -> MouseController:
    try:
        autopy = import_module("autopy")
        width, height = autopy.screen.size()
        return MouseController(
            width=int(width),
            height=int(height),
            backend="autopy",
            move=autopy.mouse.move,
            click=autopy.mouse.click,
        )
    except (ImportError, ModuleNotFoundError):
        pyautogui = import_module("pyautogui")
        width, height = pyautogui.size()
        return MouseController(
            width=int(width),
            height=int(height),
            backend="pyautogui",
            move=pyautogui.moveTo,
            click=pyautogui.click,
        )


def run_real_mouse_runtime(config: ExperimentalConfig, plan: RuntimePlan) -> int:
    cv2 = import_module("cv2")
    mouse = _create_mouse_controller()

    metadata = build_real_mouse_metadata(config, plan)
    print(f"Real Mouse Runtime metadata: {metadata}")
    print(f"Mouse controller backend: {mouse.backend}")
    print("Press 'q' to quit. Hold open palm to toggle pause.")

    pipeline = HandControlPipeline(
        config=config,
        condition_name=plan.condition,
        output_width=mouse.width,
        output_height=mouse.height,
        prefer_tasks=True,
        use_simple_profile=True,
    )

    cap = cv2.VideoCapture(config.backend.camera_index)
    cap.set(3, config.backend.camera_width)
    cap.set(4, config.backend.camera_height)

    while True:
        success, image = cap.read()
        if not success:
            print("Camera frame could not be read.")
            break

        frame_result: HandControlFrame = pipeline.process_frame(image)

        # Apply real mouse effects
        if frame_result.cursor_target is not None and not frame_result.paused:
            screen_x = mouse.width - frame_result.cursor_target.x
            screen_y = frame_result.cursor_target.y
            mouse.move(screen_x, screen_y)

        if frame_result.click_fired:
            mouse.click()

        if frame_result.safety_triggered:
            print("Corner failsafe triggered. Pausing.")

        # Overlay
        display_image = (
            frame_result.landmarks_image
            if frame_result.landmarks_image is not None
            else image
        )
        overlay_lines = [
            f"Backend: {frame_result.backend_used}",
            f"Gesture: {frame_result.feedback_label}",
            f"Paused: {frame_result.paused}",
            f"FPS: {int(frame_result.fps)}",
            "Quit: q | Pause: open palm",
        ]
        if frame_result.fallback_reason:
            overlay_lines.append(f"Fallback: {frame_result.fallback_reason}")

        for i, line in enumerate(overlay_lines):
            cv2.putText(
                display_image,
                line,
                (10, 30 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Real Mouse Runtime", display_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    pipeline.close()
    return 0
