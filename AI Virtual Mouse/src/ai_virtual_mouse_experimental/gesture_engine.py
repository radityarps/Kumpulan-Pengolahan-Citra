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


def config_from_settings(settings: GestureSettings) -> GestureEngineConfig:
    return GestureEngineConfig(click_threshold_px=settings.click_threshold_px)


def classify_improved_gesture(
    hand: GestureInput,
    config: GestureEngineConfig | None = None,
) -> GestureResult:
    cfg = config or GestureEngineConfig()

    if is_open_palm(hand):
        return GestureResult(
            name="pause",
            reason="open_palm_pause",
            paused=True,
            feedback_label="Paused",
            feedback_color=(255, 193, 7),
        )

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
            return GestureResult(
                name="click",
                reason="pinch_below_threshold",
                click=True,
                feedback_label="Click",
                feedback_color=(76, 175, 80),
            )

    if hand.index and not hand.middle:
        return GestureResult(
            name="move",
            reason="index_only_move",
            cursor_enabled=True,
            feedback_label="Move",
            feedback_color=(233, 30, 99),
        )

    return GestureResult(name="idle", reason="no_supported_improved_gesture")


def is_open_palm(hand: GestureInput) -> bool:
    return hand.index and hand.middle and hand.ring and hand.pinky


def is_pinching(hand: GestureInput, config: GestureEngineConfig) -> bool:
    return (
        hand.pinch_distance_px is not None
        and hand.pinch_distance_px < config.click_threshold_px
    )


def feedback_style(result: GestureResult) -> dict[str, object]:
    return {
        "label": result.feedback_label,
        "color": result.feedback_color,
        "state": result.name,
    }
