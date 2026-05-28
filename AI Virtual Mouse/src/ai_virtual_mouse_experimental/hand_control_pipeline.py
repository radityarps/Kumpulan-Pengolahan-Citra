from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

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
    GestureResult,
    classify_improved_gesture,
    classify_simple_real_mouse_gesture,
    config_from_settings,
    debounce_config_from_settings,
    feedback_style,
    update_click_debounce,
)
from .hand_tracker import HandTracker, HandTrackingResult


@dataclass(frozen=True)
class HandControlFrame:
    """Per-frame output from the shared hand-control pipeline."""

    cursor_target: Point | None = None
    click_fired: bool = False
    paused: bool = False
    gesture_name: str = "idle"
    feedback_label: str = "Idle"
    feedback_color: tuple[int, int, int] = (160, 160, 160)
    backend_used: str = "unknown"
    fallback_reason: str | None = None
    fps: float = 0.0
    safety_triggered: bool = False
    hand_detected: bool = False
    landmarks_image: np.ndarray | None = None


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


def hand_input_from_tracking(
    result: HandTrackingResult, config: GestureEngineConfig
) -> GestureInput:
    """Convert raw tracking result to gesture-engine input."""
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


class HandControlPipeline:
    """Shared hand-control pipeline usable by Real Mouse Runtime and Benchmark Runtime.

    Owns: hand tracker, gesture classification, cursor mapping, smoothing,
    debounce, pause toggle, safety state, FPS calculation.

    Does NOT own: camera capture, rendering, or cursor side effects.
    """

    def __init__(
        self,
        config: ExperimentalConfig,
        condition_name: str,
        output_width: int,
        output_height: int,
        prefer_tasks: bool = True,
        use_simple_profile: bool = True,
    ):
        self.config = config
        self.condition_name = condition_name
        self.condition = config.get_condition(condition_name)
        self.output_width = output_width
        self.output_height = output_height
        self.use_simple_profile = use_simple_profile

        self._tracker = HandTracker(config, prefer_tasks=prefer_tasks)
        self._gesture_cfg = config_from_settings(config.gesture)
        self._debounce_cfg = debounce_config_from_settings(config.debounce)

        fallback_bounds = default_camera_bounds(
            config.backend.camera_width, config.backend.camera_height
        )
        self._mapping_bounds = select_mapping_bounds(
            self.condition.calibration_enabled,
            None,
            fallback_bounds,
        )

        self._previous_x: float = output_width / 2
        self._previous_y: float = output_height / 2
        self._click_debounce = ClickDebounceState()
        self._pause_toggle = PauseToggleState()
        self._safety = SafetyState()
        self._previous_time: float = 0.0

    @property
    def backend_used(self) -> str:
        return self._tracker._backend_used

    @property
    def fallback_reason(self) -> str | None:
        return self._tracker._fallback_reason

    @property
    def paused(self) -> bool:
        return self._pause_toggle.paused

    def process_frame(self, frame: np.ndarray) -> HandControlFrame:
        """Process one camera frame and return hand-control state.

        Does NOT apply cursor side effects. The caller decides what to do
        with cursor_target and click_fired.
        """
        result = self._tracker.process(frame)

        # Default: no hand detected
        gesture = self._classify(GestureInput())
        feedback = feedback_style(gesture)
        cursor_target: Point | None = None
        click_fired = False
        safety_triggered = False
        landmarks_image = frame

        if result.success:
            landmarks_image = self._tracker.draw_landmarks(frame, result)
            hand = hand_input_from_tracking(result, self._gesture_cfg)
            gesture = self._classify(hand)
            feedback = feedback_style(gesture)

            # Pause toggle
            pause_res = update_pause_toggle(self._pause_toggle, gesture.name == "pause")
            self._pause_toggle = pause_res.state

            if not self._pause_toggle.paused:
                # Cursor movement
                if gesture.cursor_enabled and result.landmarks:
                    index_tip = result.landmarks[8]
                    target = map_point_to_output(
                        index_tip,
                        self._mapping_bounds,
                        self.output_width,
                        self.output_height,
                    )
                    smoothed = apply_smoothing(
                        self.condition.smoothing_strategy,
                        Point(self._previous_x, self._previous_y),
                        target,
                    )
                    self._previous_x, self._previous_y = smoothed.x, smoothed.y
                    cursor_target = smoothed

                # Click debounce
                if gesture.click:
                    debounce_res = update_click_debounce(
                        self._click_debounce, True, time.time(), self._debounce_cfg
                    )
                    self._click_debounce = debounce_res.state
                    click_fired = debounce_res.emit_click
                else:
                    debounce_res = update_click_debounce(
                        self._click_debounce, False, time.time(), self._debounce_cfg
                    )
                    self._click_debounce = debounce_res.state

                # Safety
                if cursor_target is not None:
                    self._safety = check_safety(
                        self._safety,
                        cursor_target.x,
                        cursor_target.y,
                        screen_width=self.output_width,
                        screen_height=self.output_height,
                    )
                    if self._safety.quit_requested:
                        self._pause_toggle = PauseToggleState(paused=True)
                        safety_triggered = True

        # FPS
        current_time = time.time()
        fps = (
            0.0
            if self._previous_time == 0.0
            else 1.0 / max(current_time - self._previous_time, 1e-6)
        )
        self._previous_time = current_time

        return HandControlFrame(
            cursor_target=cursor_target,
            click_fired=click_fired,
            paused=self._pause_toggle.paused,
            gesture_name=gesture.name,
            feedback_label=str(feedback["label"]),
            feedback_color=feedback["color"],  # type: ignore[arg-type]
            backend_used=result.backend_used,
            fallback_reason=result.fallback_reason,
            fps=fps,
            safety_triggered=safety_triggered,
            hand_detected=result.success,
            landmarks_image=landmarks_image,
        )

    def close(self) -> None:
        self._tracker.close()

    def _classify(self, hand: GestureInput) -> GestureResult:
        if self.use_simple_profile:
            return classify_simple_real_mouse_gesture(hand, self._gesture_cfg)
        return classify_improved_gesture(hand, self._gesture_cfg)
