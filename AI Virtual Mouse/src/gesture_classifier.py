"""
AI Virtual Mouse — Gesture Classifier
Rule-based gesture classification from finger states and inter-landmark distances.

Supports profile-based gesture mappings, pinch hysteresis for click stability,
and a short cursor freeze window after click transitions to reduce drift.
"""

import time
import numpy as np
from src.config import (
    CLICK_THRESHOLD_PX,
    DEBOUNCE_TIME_MS,
    DRAG_THRESHOLD_PX,
    GESTURE_STYLE,
    FRAME_HEIGHT,
    SCROLL_DEAD_ZONE_PX,
    SCROLL_SENSITIVITY,
    SCROLL_CENTER_DEAD_ZONE_PX,
    SCROLL_STEP_AMOUNT,
    SCROLL_REPEAT_MS,
    LEFT_CLICK_PINCH_ON_PX,
    LEFT_CLICK_PINCH_OFF_PX,
    RIGHT_CLICK_PINCH_ON_PX,
    RIGHT_CLICK_PINCH_OFF_PX,
    CLICK_HOLD_TIME_MS,
    MOVE_FREEZE_AFTER_CLICK_MS,
)
from src.gesture_profiles import get_profile


class GestureClassifier:
    """
    Stateful classifier that maps landmarks into gesture modes and actions.
    """

    def __init__(
        self,
        click_threshold=CLICK_THRESHOLD_PX,
        drag_threshold=DRAG_THRESHOLD_PX,
        debounce_ms=DEBOUNCE_TIME_MS,
        scroll_sensitivity=SCROLL_SENSITIVITY,
        scroll_dead_zone=SCROLL_DEAD_ZONE_PX,
        scroll_center_dead_zone=SCROLL_CENTER_DEAD_ZONE_PX,
        scroll_step_amount=SCROLL_STEP_AMOUNT,
        scroll_repeat_ms=SCROLL_REPEAT_MS,
        gesture_style=GESTURE_STYLE,
        left_click_on=LEFT_CLICK_PINCH_ON_PX,
        left_click_off=LEFT_CLICK_PINCH_OFF_PX,
        right_click_on=RIGHT_CLICK_PINCH_ON_PX,
        right_click_off=RIGHT_CLICK_PINCH_OFF_PX,
        click_hold_ms=CLICK_HOLD_TIME_MS,
        move_freeze_after_click_ms=MOVE_FREEZE_AFTER_CLICK_MS,
    ):
        self.click_threshold = click_threshold
        self.drag_threshold = drag_threshold
        self.debounce_ms = debounce_ms
        self.scroll_sensitivity = scroll_sensitivity
        self.scroll_dead_zone = scroll_dead_zone
        self.scroll_center_dead_zone = scroll_center_dead_zone
        self.scroll_step_amount = scroll_step_amount
        self.scroll_repeat_ms = scroll_repeat_ms
        self.scroll_center_y = FRAME_HEIGHT // 2
        self.gesture_style = gesture_style
        self.profile = get_profile(gesture_style)

        self.left_click_on = left_click_on
        self.left_click_off = left_click_off
        self.right_click_on = right_click_on
        self.right_click_off = right_click_off
        self.click_hold_ms = click_hold_ms
        self.move_freeze_after_click_ms = move_freeze_after_click_ms

        # Internal state
        self.current_mode = "None"
        self.mode_start_time = 0
        self.stable_mode = "None"
        self.click_ready = True
        self.drag_active = False
        self.last_scroll_action_ms = 0

        self.left_pinch_active = False
        self.right_pinch_active = False
        self.left_pinch_hold_start_ms = None
        self.right_pinch_hold_start_ms = None
        self.freeze_until_ms = 0

    def classify(self, fingers, lmList, findDistance_fn):
        """
        Returns:
            tuple: (mode, action)
        """
        if not lmList or not findDistance_fn:
            self.reset()
            return "None", None

        fingers = list(fingers) if isinstance(fingers, (list, np.ndarray)) else fingers

        dist_idx_mid = 0
        dist_idx_thumb = 0
        dist_mid_thumb = 0
        dist_idx_ring = 0
        try:
            dist_idx_mid, _, _ = findDistance_fn(8, 12, draw=False)
            dist_idx_thumb, _, _ = findDistance_fn(4, 8, draw=False)
            dist_mid_thumb, _, _ = findDistance_fn(4, 12, draw=False)
            dist_idx_ring, _, _ = findDistance_fn(8, 16, draw=False)
        except (IndexError, TypeError, Exception) as e:
            print(f"[GestureClassifier] Distance calculation failed: {e}")
            self.reset()
            return "None", None

        now = self._now_ms()
        detected_mode, action = self._detect_gesture(
            fingers=fingers,
            dist_idx_mid=dist_idx_mid,
            dist_idx_thumb=dist_idx_thumb,
            dist_mid_thumb=dist_mid_thumb,
            dist_idx_ring=dist_idx_ring,
            lmList=lmList,
            now_ms=now,
        )

        if detected_mode == "StopMove":
            self.current_mode = "None"
            self.stable_mode = "None"
            self.mode_start_time = now
            return "None", action

        if detected_mode in ("Move", "Drag"):
            self.current_mode = detected_mode
            self.stable_mode = detected_mode
            self.mode_start_time = now
            return self.stable_mode, action

        if detected_mode != self.current_mode:
            self.current_mode = detected_mode
            self.mode_start_time = now
        else:
            if now - self.mode_start_time >= self.debounce_ms:
                self.stable_mode = detected_mode

        return self.stable_mode, action

    def _detect_gesture(
        self,
        fingers,
        dist_idx_mid,
        dist_idx_thumb,
        dist_mid_thumb,
        dist_idx_ring,
        lmList,
        now_ms,
    ):
        stop_pattern = self.profile.get("stop_pattern")
        if stop_pattern is not None and self._match_pattern(fingers, stop_pattern):
            self._clear_click_states()
            self.last_scroll_action_ms = 0
            if self.drag_active:
                self.drag_active = False
                return "StopMove", "drag_end"
            return "StopMove", None

        move_patterns = self.profile["move_patterns"]
        is_move_pattern = any(self._match_pattern(fingers, pattern) for pattern in move_patterns)
        if is_move_pattern:
            self._clear_click_states()
            if self.drag_active:
                self.drag_active = False
                return "Move", "drag_end"
            return "Move", "move"

        if self._match_pattern(fingers, self.profile["click_pattern"]):
            return self._handle_left_click(dist_idx_mid, now_ms)

        if self._match_pattern(fingers, self.profile["right_click_pattern"]):
            return self._handle_right_click(dist_idx_ring, now_ms)

        if self._match_pattern(fingers, self.profile["drag_pattern"]):
            self._clear_click_states()
            if not self.drag_active:
                self.drag_active = True
                return "Drag", "drag_start"
            return "Drag", "move"

        if self._match_pattern(fingers, self.profile["scroll_pattern"]):
            self._clear_click_states()
            return "Scroll", self._scroll_from_center(lmList, now_ms)

        self._clear_click_states()
        self.last_scroll_action_ms = 0
        if self.drag_active:
            self.drag_active = False
            return "None", "drag_end"
        return "None", None

    def _handle_left_click(self, pinch_distance, now_ms):
        if self.left_pinch_active:
            if pinch_distance >= self.left_click_off:
                self.left_pinch_active = False
                self.left_pinch_hold_start_ms = None
                if not self.right_pinch_active:
                    self.click_ready = True
            return "Click", None

        if pinch_distance <= self.left_click_on:
            if self.left_pinch_hold_start_ms is None:
                self.left_pinch_hold_start_ms = now_ms
                return "Click", None
            if now_ms - self.left_pinch_hold_start_ms >= self.click_hold_ms:
                self.left_pinch_active = True
                self.left_pinch_hold_start_ms = None
                self.click_ready = False
                self._freeze_movement(now_ms)
                return "Click", "click"
            return "Click", None

        self.left_pinch_hold_start_ms = None
        if not self.right_pinch_active:
            self.click_ready = True
        return "Click", None

    def _handle_right_click(self, pinch_distance, now_ms):
        if self.right_pinch_active:
            if pinch_distance >= self.right_click_off:
                self.right_pinch_active = False
                self.right_pinch_hold_start_ms = None
                if not self.left_pinch_active:
                    self.click_ready = True
            return "RightClick", None

        if pinch_distance <= self.right_click_on:
            if self.right_pinch_hold_start_ms is None:
                self.right_pinch_hold_start_ms = now_ms
                return "RightClick", None
            if now_ms - self.right_pinch_hold_start_ms >= self.click_hold_ms:
                self.right_pinch_active = True
                self.right_pinch_hold_start_ms = None
                self.click_ready = False
                self._freeze_movement(now_ms)
                return "RightClick", "right_click"
            return "RightClick", None

        self.right_pinch_hold_start_ms = None
        if not self.left_pinch_active:
            self.click_ready = True
        return "RightClick", None

    def _clear_click_states(self):
        self.left_pinch_hold_start_ms = None
        self.right_pinch_hold_start_ms = None
        if not self.left_pinch_active and not self.right_pinch_active:
            self.click_ready = True

    def _freeze_movement(self, now_ms):
        self.freeze_until_ms = now_ms + self.move_freeze_after_click_ms

    def is_movement_frozen(self):
        return self._now_ms() < self.freeze_until_ms

    def _scroll_from_center(self, lmList, now_ms):
        if len(lmList) <= 8:
            return None

        if now_ms - self.last_scroll_action_ms < self.scroll_repeat_ms:
            return None

        index_y = lmList[8][2]
        top_zone = self.scroll_center_y - self.scroll_center_dead_zone
        bottom_zone = self.scroll_center_y + self.scroll_center_dead_zone

        if index_y < top_zone:
            self.last_scroll_action_ms = now_ms
            return ("scroll", self.scroll_step_amount)
        if index_y > bottom_zone:
            self.last_scroll_action_ms = now_ms
            return ("scroll", -self.scroll_step_amount)
        return None

    @staticmethod
    def _match_pattern(fingers, pattern):
        if pattern is None:
            return False
        if not isinstance(fingers, (list, tuple, np.ndarray)):
            return False
        if len(fingers) != len(pattern):
            return False
        for finger_val, expected in zip(fingers, pattern, strict=False):
            if expected is None:
                continue
            if int(finger_val) != int(expected):
                return False
        return True

    def reset(self):
        self.current_mode = "None"
        self.stable_mode = "None"
        self.click_ready = True
        self.drag_active = False
        self.last_scroll_action_ms = 0
        self.left_pinch_active = False
        self.right_pinch_active = False
        self.left_pinch_hold_start_ms = None
        self.right_pinch_hold_start_ms = None
        self.freeze_until_ms = 0

    @staticmethod
    def _now_ms():
        return time.time() * 1000
