from __future__ import annotations

import time
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from .app import RuntimePlan
from .config import ExperimentalConfig
from .cursor_mapping import (
    Point,
    apply_smoothing,
    default_camera_bounds,
    map_point_to_output,
    select_mapping_bounds,
)
from .gesture_engine import (
    ClickDebounceState,
    GestureEngineConfig,
    GestureInput,
    classify_simple_real_mouse_gesture,
    config_from_settings,
    debounce_config_from_settings,
    feedback_style,
    update_click_debounce,
)
from .hand_tracker import HandTracker, HandTrackingResult


@dataclass(frozen=True)
class PauseToggleState:
    holding: bool = False
    hold_frames: int = 0
    toggle_threshold_frames: int = 8
    paused: bool = False
    toggled_this_hold: bool = False


@dataclass(frozen=True)
class PauseToggleResult:
    state: PauseToggleState
    toggled: bool = False


@dataclass(frozen=True)
class SafetyState:
    corner_frames: int = 0
    corner_threshold_frames: int = 24
    quit_requested: bool = False


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


def update_pause_toggle(
    state: PauseToggleState,
    open_palm_active: bool,
) -> PauseToggleResult:
    if open_palm_active:
        next_hold_frames = state.hold_frames + 1
        if (
            not state.toggled_this_hold
            and next_hold_frames >= state.toggle_threshold_frames
        ):
            return PauseToggleResult(
                state=PauseToggleState(
                    holding=True,
                    hold_frames=next_hold_frames,
                    toggle_threshold_frames=state.toggle_threshold_frames,
                    paused=not state.paused,
                    toggled_this_hold=True,
                ),
                toggled=True,
            )
        return PauseToggleResult(
            state=PauseToggleState(
                holding=True,
                hold_frames=next_hold_frames,
                toggle_threshold_frames=state.toggle_threshold_frames,
                paused=state.paused,
                toggled_this_hold=state.toggled_this_hold,
            ),
            toggled=False,
        )

    return PauseToggleResult(
        state=PauseToggleState(
            holding=False,
            hold_frames=0,
            toggle_threshold_frames=state.toggle_threshold_frames,
            paused=state.paused,
            toggled_this_hold=False,
        ),
        toggled=False,
    )


def check_safety(
    state: SafetyState,
    cursor_x: float,
    cursor_y: float,
    screen_width: float | None = None,
    screen_height: float | None = None,
    margin_px: float = 4,
) -> SafetyState:
    near_left = cursor_x <= margin_px
    near_top = cursor_y <= margin_px
    near_right = screen_width is not None and cursor_x >= screen_width - margin_px
    near_bottom = screen_height is not None and cursor_y >= screen_height - margin_px
    if near_left or near_top or near_right or near_bottom:
        next_corner = state.corner_frames + 1
        if next_corner >= state.corner_threshold_frames:
            return SafetyState(
                corner_frames=next_corner,
                corner_threshold_frames=state.corner_threshold_frames,
                quit_requested=True,
            )
        return SafetyState(
            corner_frames=next_corner,
            corner_threshold_frames=state.corner_threshold_frames,
            quit_requested=False,
        )
    return SafetyState(
        corner_frames=0,
        corner_threshold_frames=state.corner_threshold_frames,
        quit_requested=False,
    )


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


def _hand_input_from_tracking(
    result: HandTrackingResult, config: GestureEngineConfig
) -> GestureInput:
    fingers = result.fingers_up or []
    if len(fingers) < 5:
        return GestureInput()
    return GestureInput(
        thumb=bool(fingers[0]),
        index=bool(fingers[1]),
        middle=bool(fingers[2]),
        ring=bool(fingers[3]),
        pinky=bool(fingers[4]),
        pinch_distance_px=result.pinch_distance_px,
        pinch_duration_s=0.0,
        index_middle_vertical_delta_px=result.index_middle_vertical_delta_px or 0.0,
    )


def run_real_mouse_runtime(config: ExperimentalConfig, plan: RuntimePlan) -> int:
    cv2 = import_module("cv2")
    mouse = _create_mouse_controller()

    metadata = build_real_mouse_metadata(config, plan)
    print(f"Real Mouse Runtime metadata: {metadata}")
    print(f"Mouse controller backend: {mouse.backend}")
    print("Press 'q' to quit. Hold open palm to toggle pause.")

    tracker = HandTracker(config, prefer_tasks=True)
    cap = cv2.VideoCapture(config.backend.camera_index)
    cap.set(3, config.backend.camera_width)
    cap.set(4, config.backend.camera_height)

    w_screen, h_screen = mouse.width, mouse.height
    fallback_bounds = default_camera_bounds(
        config.backend.camera_width, config.backend.camera_height
    )
    # TODO: load calibration if available
    mapping_bounds = select_mapping_bounds(
        config.get_condition(plan.condition).calibration_enabled,
        None,
        fallback_bounds,
    )

    gesture_cfg = config_from_settings(config.gesture)
    debounce_cfg = debounce_config_from_settings(config.debounce)

    previous_x, previous_y = w_screen / 2, h_screen / 2
    screen_cursor_x, screen_cursor_y = w_screen / 2, h_screen / 2
    click_debounce = ClickDebounceState()
    pause_toggle = PauseToggleState()
    safety = SafetyState()
    previous_time = 0.0

    while True:
        success, image = cap.read()
        if not success:
            print("Camera frame could not be read.")
            break

        result = tracker.process(image)
        feedback = feedback_style(
            classify_simple_real_mouse_gesture(GestureInput(), gesture_cfg)
        )
        snapshot = RuntimeSnapshot(backend_used=result.backend_used)

        if result.success:
            image = tracker.draw_landmarks(image, result)
            hand = _hand_input_from_tracking(result, gesture_cfg)
            gesture = classify_simple_real_mouse_gesture(hand, gesture_cfg)
            feedback = feedback_style(gesture)

            pause_res = update_pause_toggle(pause_toggle, gesture.name == "pause")
            pause_toggle = pause_res.state
            if pause_res.toggled:
                print(f"Pause toggled: paused={pause_toggle.paused}")

            snapshot = RuntimeSnapshot(
                gesture_name=gesture.name,
                paused=pause_toggle.paused,
                click_ready=click_debounce.armed,
                backend_used=result.backend_used,
                fps=snapshot.fps,
                cursor_x=previous_x,
                cursor_y=previous_y,
            )

            if not pause_toggle.paused:
                if gesture.cursor_enabled:
                    index_tip = result.landmarks[8] if result.landmarks else Point(0, 0)
                    target = map_point_to_output(
                        index_tip, mapping_bounds, w_screen, h_screen
                    )
                    smoothed = apply_smoothing(
                        config.get_condition(plan.condition).smoothing_strategy,
                        Point(previous_x, previous_y),
                        target,
                    )
                    screen_cursor_x = w_screen - smoothed.x
                    screen_cursor_y = smoothed.y
                    mouse.move(screen_cursor_x, screen_cursor_y)
                    previous_x, previous_y = smoothed.x, smoothed.y

                if gesture.click:
                    debounce_res = update_click_debounce(
                        click_debounce, True, time.time(), debounce_cfg
                    )
                    click_debounce = debounce_res.state
                    if debounce_res.emit_click:
                        mouse.click()
                        snapshot = replace(snapshot, click_ready=False)
                else:
                    debounce_res = update_click_debounce(
                        click_debounce, False, time.time(), debounce_cfg
                    )
                    click_debounce = debounce_res.state

                safety = check_safety(
                    safety,
                    screen_cursor_x,
                    screen_cursor_y,
                    screen_width=w_screen,
                    screen_height=h_screen,
                )
                if safety.quit_requested:
                    print("Corner failsafe triggered. Pausing.")
                    pause_toggle = PauseToggleState(paused=True)

        current_time = time.time()
        fps = 0 if previous_time == 0 else 1 / (current_time - previous_time)
        previous_time = current_time
        snapshot = replace(snapshot, fps=fps)

        # Overlay
        overlay_lines = [
            f"Backend: {snapshot.backend_used}",
            f"Gesture: {feedback['label']}",
            f"Paused: {snapshot.paused}",
            f"FPS: {int(fps)}",
            "Quit: q | Pause: open palm",
        ]
        if result.fallback_reason:
            overlay_lines.append(f"Fallback: {result.fallback_reason}")

        for i, line in enumerate(overlay_lines):
            cv2.putText(
                image,
                line,
                (10, 30 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Real Mouse Runtime", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    tracker.close()
    return 0


def replace(snapshot: RuntimeSnapshot, **kwargs: Any) -> RuntimeSnapshot:
    return RuntimeSnapshot(
        gesture_name=kwargs.get("gesture_name", snapshot.gesture_name),
        paused=kwargs.get("paused", snapshot.paused),
        click_ready=kwargs.get("click_ready", snapshot.click_ready),
        backend_used=kwargs.get("backend_used", snapshot.backend_used),
        fps=kwargs.get("fps", snapshot.fps),
        cursor_x=kwargs.get("cursor_x", snapshot.cursor_x),
        cursor_y=kwargs.get("cursor_y", snapshot.cursor_y),
    )
