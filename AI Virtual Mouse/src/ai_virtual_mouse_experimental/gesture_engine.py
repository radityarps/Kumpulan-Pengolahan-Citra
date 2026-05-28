from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .config import GestureSettings

GestureName = Literal["idle", "move", "click", "drag", "scroll", "pause"]


@dataclass(frozen=True)
class GestureInput:
    """Synthetic/testable hand state independent from camera and mouse effects."""

    thumb: bool = False
    index: bool = False
    middle: bool = False
    ring: bool = False
    pinky: bool = False
    pinch_distance_px: float | None = None
    pinch_duration_s: float = 0.0
    index_middle_vertical_delta_px: float = 0.0


@dataclass(frozen=True)
class GestureResult:
    name: GestureName
    reason: str
    cursor_enabled: bool = False
    click: bool = False
    drag: bool = False
    scroll_delta: float = 0.0
    paused: bool = False
    feedback_label: str = "Idle"
    feedback_color: tuple[int, int, int] = (160, 160, 160)


@dataclass(frozen=True)
class GestureEngineConfig:
    click_threshold_px: int = 40
    drag_hold_seconds: float = 0.45
    scroll_activation_delta_px: float = 18.0
    scroll_scale: float = 0.1


@dataclass(frozen=True)
class ClickDebounceConfig:
    stable_frames_required: int = 2
    release_frames_required: int = 2
    cooldown_seconds: float = 0.35


@dataclass(frozen=True)
class ClickDebounceState:
    pressed_frames: int = 0
    released_frames: int = 0
    armed: bool = True
    last_click_time_s: float = -9999.0


@dataclass(frozen=True)
class ClickDebounceResult:
    state: ClickDebounceState
    emit_click: bool
    reason: str


def config_from_settings(settings: GestureSettings) -> GestureEngineConfig:
    return GestureEngineConfig(click_threshold_px=settings.click_threshold_px)


def classify_improved_gesture(
    hand: GestureInput,
    config: GestureEngineConfig | None = None,
) -> GestureResult:
    cfg = config or GestureEngineConfig()

    if is_open_palm(hand):
        return _pause_result()

    if hand.index and hand.middle and not hand.ring and not hand.pinky:
        if abs(hand.index_middle_vertical_delta_px) >= cfg.scroll_activation_delta_px:
            return GestureResult(
                name="scroll",
                reason="index_middle_vertical_delta",
                scroll_delta=hand.index_middle_vertical_delta_px * cfg.scroll_scale,
                feedback_label="Scroll",
                feedback_color=(3, 169, 244),
            )

        if is_pinching(hand, cfg):
            if hand.pinch_duration_s >= cfg.drag_hold_seconds:
                return GestureResult(
                    name="drag",
                    reason="pinch_held",
                    cursor_enabled=True,
                    drag=True,
                    feedback_label="Drag",
                    feedback_color=(156, 39, 176),
                )
            return _click_result("pinch_below_threshold")

    if hand.index and not hand.middle and not hand.ring and not hand.pinky:
        return _move_result()

    return GestureResult(name="idle", reason="no_supported_improved_gesture")


def classify_simple_real_mouse_gesture(
    hand: GestureInput,
    config: GestureEngineConfig | None = None,
) -> GestureResult:
    """Simple Real Mouse Profile: move, stable pinch click, and pause only.

    Drag and scroll are intentionally excluded from the first real mouse runtime to
    reduce false positives while controlling the OS cursor.
    """
    cfg = config or GestureEngineConfig()

    if is_open_palm(hand):
        return _pause_result()

    if hand.index and hand.middle and not hand.ring and not hand.pinky:
        if is_pinching(hand, cfg):
            return _click_result("index_middle_stable_pinch")
        return GestureResult(name="idle", reason="index_middle_without_pinch")

    if hand.index and not hand.middle and not hand.ring and not hand.pinky:
        return _move_result()

    return GestureResult(name="idle", reason="no_supported_real_mouse_gesture")


def _pause_result() -> GestureResult:
    return GestureResult(
        name="pause",
        reason="open_palm_pause",
        paused=True,
        feedback_label="Paused",
        feedback_color=(255, 193, 7),
    )


def _click_result(reason: str) -> GestureResult:
    return GestureResult(
        name="click",
        reason=reason,
        click=True,
        feedback_label="Click",
        feedback_color=(76, 175, 80),
    )


def _move_result() -> GestureResult:
    return GestureResult(
        name="move",
        reason="index_only_move",
        cursor_enabled=True,
        feedback_label="Move",
        feedback_color=(233, 30, 99),
    )


def is_open_palm(hand: GestureInput) -> bool:
    return hand.index and hand.middle and hand.ring and hand.pinky


def is_pinching(hand: GestureInput, config: GestureEngineConfig) -> bool:
    return (
        hand.pinch_distance_px is not None
        and hand.pinch_distance_px < config.click_threshold_px
    )


def update_click_debounce(
    state: ClickDebounceState,
    raw_click_active: bool,
    now_s: float,
    config: ClickDebounceConfig | None = None,
) -> ClickDebounceResult:
    cfg = config or ClickDebounceConfig()

    if raw_click_active:
        next_state = ClickDebounceState(
            pressed_frames=state.pressed_frames + 1,
            released_frames=0,
            armed=state.armed,
            last_click_time_s=state.last_click_time_s,
        )
        cooldown_elapsed = now_s - state.last_click_time_s >= cfg.cooldown_seconds
        stable = next_state.pressed_frames >= cfg.stable_frames_required
        if next_state.armed and stable and cooldown_elapsed:
            return ClickDebounceResult(
                state=ClickDebounceState(
                    pressed_frames=next_state.pressed_frames,
                    released_frames=0,
                    armed=False,
                    last_click_time_s=now_s,
                ),
                emit_click=True,
                reason="stable_click_emitted",
            )
        return ClickDebounceResult(next_state, False, "click_not_ready")

    released_frames = state.released_frames + 1
    armed = state.armed or released_frames >= cfg.release_frames_required
    return ClickDebounceResult(
        state=ClickDebounceState(
            pressed_frames=0,
            released_frames=released_frames,
            armed=armed,
            last_click_time_s=state.last_click_time_s,
        ),
        emit_click=False,
        reason="released" if armed else "waiting_for_release",
    )


def debounce_config_from_settings(settings) -> ClickDebounceConfig:
    return ClickDebounceConfig(
        stable_frames_required=settings.stable_frames_required,
        release_frames_required=settings.release_frames_required,
        cooldown_seconds=settings.cooldown_seconds,
    )


def feedback_style(result: GestureResult) -> dict[str, object]:
    return {
        "label": result.feedback_label,
        "color": result.feedback_color,
        "state": result.name,
    }
