from __future__ import annotations

import math
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

GESTURE_PROFILE_BASELINE = "baseline"
GESTURE_PROFILE_SIMPLE = "simple"
GESTURE_PROFILE_IMPROVED = "improved"


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
        gesture_profile: str | None = None,
    ):
        self.config = config
        self.condition_name = condition_name
        self.condition = config.get_condition(condition_name)
        self.output_width = output_width
        self.output_height = output_height

        # Determine gesture profile
        if gesture_profile is not None:
            self._gesture_profile = gesture_profile
        elif condition_name == "baseline":
            self._gesture_profile = GESTURE_PROFILE_BASELINE
        elif use_simple_profile:
            self._gesture_profile = GESTURE_PROFILE_SIMPLE
        else:
            self._gesture_profile = GESTURE_PROFILE_IMPROVED

        self._tracker = HandTracker(config, prefer_tasks=prefer_tasks)
        self._gesture_cfg = config_from_settings(config.gesture)
        self._debounce_cfg = debounce_config_from_settings(config.debounce)
        self._debounce_enabled = self.condition.debounce_enabled

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

        # Technical metrics
        self._path_length: float = 0.0
        self._fps_samples: list[float] = []
        self._movement_deltas: list[float] = []

    @property
    def backend_used(self) -> str:
        return self._tracker._backend_used

    @property
    def fallback_reason(self) -> str | None:
        return self._tracker._fallback_reason

    @property
    def paused(self) -> bool:
        return self._pause_toggle.paused

    @property
    def gesture_profile(self) -> str:
        return self._gesture_profile

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
                    prev_x, prev_y = self._previous_x, self._previous_y
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

                    # Track path length and movement delta
                    delta = math.hypot(smoothed.x - prev_x, smoothed.y - prev_y)
                    self._path_length += delta
                    self._movement_deltas.append(delta)

                # Click debounce (conditional)
                if gesture.click:
                    if self._debounce_enabled:
                        debounce_res = update_click_debounce(
                            self._click_debounce,
                            True,
                            time.time(),
                            self._debounce_cfg,
                        )
                        self._click_debounce = debounce_res.state
                        click_fired = debounce_res.emit_click
                    else:
                        click_fired = True
                else:
                    if self._debounce_enabled:
                        debounce_res = update_click_debounce(
                            self._click_debounce,
                            False,
                            time.time(),
                            self._debounce_cfg,
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
        if fps > 0:
            self._fps_samples.append(fps)

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
        if self._gesture_profile == GESTURE_PROFILE_BASELINE:
            return _classify_baseline_as_gesture_result(hand, self._gesture_cfg)
        if self._gesture_profile == GESTURE_PROFILE_SIMPLE:
            return classify_simple_real_mouse_gesture(hand, self._gesture_cfg)
        return classify_improved_gesture(hand, self._gesture_cfg)

    def build_metadata(self) -> dict[str, object]:
        """Return metadata dict suitable for benchmark session logging."""
        return {
            "hand_input": True,
            "condition": self.condition_name,
            "gesture_profile": self._gesture_profile,
            "configured_backend": self.condition.backend,
            "backend_used": self._tracker._backend_used,
            "fallback_reason": self._tracker._fallback_reason,
            "smoothing_strategy": self.condition.smoothing_strategy,
            "debounce_enabled": self._debounce_enabled,
            "calibration_enabled": self.condition.calibration_enabled,
            "technical_metrics": self.technical_metrics(),
        }

    def technical_metrics(self) -> dict[str, object]:
        """Return accumulated technical movement metrics."""
        fps_samples = self._fps_samples
        mean_fps = sum(fps_samples) / len(fps_samples) if fps_samples else 0.0
        jitter = _compute_jitter(self._movement_deltas)
        return {
            "cursor_path_length_px": round(self._path_length, 2),
            "mean_fps": round(mean_fps, 1),
            "fps_sample_count": len(fps_samples),
            "jitter_estimate_px": round(jitter, 3),
            "movement_sample_count": len(self._movement_deltas),
        }


def _compute_jitter(deltas: list[float]) -> float:
    """Compute jitter as standard deviation of movement deltas."""
    if len(deltas) < 2:
        return 0.0
    mean = sum(deltas) / len(deltas)
    variance = sum((d - mean) ** 2 for d in deltas) / len(deltas)
    return math.sqrt(variance)


def _classify_baseline_as_gesture_result(
    hand: GestureInput, config: GestureEngineConfig
) -> GestureResult:
    """Baseline tutorial gesture: index-only move, index+middle pinch click.

    No pause, no drag, no scroll. Matches frozen video behavior.
    """
    if hand.index and not hand.middle and not hand.ring and not hand.pinky:
        return GestureResult(
            name="move",
            reason="baseline_index_only",
            cursor_enabled=True,
            feedback_label="Move",
            feedback_color=(233, 30, 99),
        )

    if hand.index and hand.middle and not hand.ring and not hand.pinky:
        if (
            hand.pinch_distance_px is not None
            and hand.pinch_distance_px < config.click_threshold_px
        ):
            return GestureResult(
                name="click",
                reason="baseline_index_middle_pinch",
                click=True,
                feedback_label="Click",
                feedback_color=(76, 175, 80),
            )
        return GestureResult(
            name="idle",
            reason="baseline_index_middle_no_pinch",
            cursor_enabled=True,
            feedback_label="Click Ready",
            feedback_color=(255, 193, 7),
        )

    return GestureResult(name="idle", reason="baseline_no_gesture")
