"""
AI Virtual Mouse — Gesture Classifier
Rule-based gesture classification from finger state vectors and inter-landmark distances.

Supports 5 gestures:
    - Move       [1,1,1,0,0] or [0,1,1,0,0]
  - Click      [0,1,0,0,0]  only index up + proximity
  - RightClick [0,0,1,0,0]  only middle up + proximity
  - Drag       [0,1,1,1,0]  three fingers + thumb-index proximity
  - Scroll     [0,1,1,1,1]  four fingers + vertical displacement

Includes debounce (300ms) to prevent spurious mode switching and
edge-triggered click logic to avoid auto-repeat.
"""

import time
import numpy as np
from src.config import (
    CLICK_THRESHOLD_PX,
    DEBOUNCE_TIME_MS,
    DRAG_THRESHOLD_PX,
    ENABLE_BRIGHTNESS_CONTROL,
    ENABLE_VOLUME_CONTROL,
    GESTURE_STYLE,
    PINCH_CONTROL_DEAD_ZONE,
    PINCH_CONTROL_SCALE,
    SCROLL_DEAD_ZONE_PX,
    SCROLL_SENSITIVITY,
)
from src.gesture_profiles import get_profile


class GestureClassifier:
    """
    Rule-based classifier that translates hand landmark data into
    gesture modes and discrete mouse actions.

    Stateful: maintains debounce timer, click-ready flag, drag state,
    and scroll reference position across frames.
    """

    def __init__(
        self,
        click_threshold=CLICK_THRESHOLD_PX,
        drag_threshold=DRAG_THRESHOLD_PX,
        debounce_ms=DEBOUNCE_TIME_MS,
        scroll_sensitivity=SCROLL_SENSITIVITY,
        scroll_dead_zone=SCROLL_DEAD_ZONE_PX,
        gesture_style=GESTURE_STYLE,
        enable_volume_control=ENABLE_VOLUME_CONTROL,
        enable_brightness_control=ENABLE_BRIGHTNESS_CONTROL,
        pinch_control_dead_zone=PINCH_CONTROL_DEAD_ZONE,
        pinch_control_scale=PINCH_CONTROL_SCALE,
    ):
        """
        Initialize gesture classifier with tunable thresholds.

        Args:
            click_threshold (int): Max distance (px) between index(8) and
                                   middle(12) tips to register a click.
            drag_threshold (int): Max distance (px) between thumb(4) and
                                  index(8) tips to start/keep drag.
            debounce_ms (int): Modes must be stable this many milliseconds
                               before they activate.
            scroll_sensitivity (int): Divider for scroll y-delta. Higher → slower.
            scroll_dead_zone (int): Minimum y-pixel change to trigger scroll.
        """
        self.click_threshold = click_threshold
        self.drag_threshold = drag_threshold
        self.debounce_ms = debounce_ms
        self.scroll_sensitivity = scroll_sensitivity
        self.scroll_dead_zone = scroll_dead_zone
        self.gesture_style = gesture_style
        self.profile = get_profile(gesture_style)
        self.enable_volume_control = enable_volume_control
        self.enable_brightness_control = enable_brightness_control
        self.pinch_control_dead_zone = pinch_control_dead_zone
        self.pinch_control_scale = pinch_control_scale

        # Internal state
        self.current_mode = "None"
        self.mode_start_time = 0  # Timestamp (ms) when mode last changed
        self.stable_mode = "None"  # Debounced, active mode
        self.click_ready = True  # Edge-triggered: wait for release
        self.drag_active = False  # Drag toggle state
        self.last_scroll_y = None  # Previous y for scroll delta calc
        self.last_control_x = None
        self.last_control_y = None

    def classify(self, fingers, lmList, findDistance_fn):
        """
        Classify the current gesture and determine the mouse action.

        Args:
            fingers (list[int]): Binary vector [thumb, index, mid, ring, pinky]
                                 from HandDetector.fingersUp().
            lmList (list): Landmark list [[id, x, y], ...].
            findDistance_fn (callable): Signature (p1, p2, draw=False)
                                        Returns (dist, mid, line_info).

        Returns:
            tuple: (mode, action)
                mode (str): "Move" | "Click" | "RightClick" | "Drag" |
                             "Scroll" | "None"
                action: "move" | "click" | "right_click" | "drag_start" |
                        "drag_end" | ("scroll", amount) | None
        """
        if not lmList or not findDistance_fn:
            self.reset()
            return "None", None

        # Normalize fingers to list (handle numpy array)
        fingers = list(fingers) if isinstance(fingers, (list, np.ndarray)) else fingers

        # Compute inter-landmark distances
        dist_idx_mid = 0
        dist_idx_thumb = 0
        dist_mid_thumb = 0
        try:
            dist_idx_mid, _, _ = findDistance_fn(8, 12, draw=False)
            dist_idx_thumb, _, _ = findDistance_fn(4, 8, draw=False)
            dist_mid_thumb, _, _ = findDistance_fn(4, 12, draw=False)
        except (IndexError, TypeError, Exception) as e:
            # Landmark index out of bounds or callable failure
            print(f"[GestureClassifier] Distance calculation failed: {e}")
            self.reset()
            return "None", None

        # Detect gesture mode from finger configuration
        detected_mode, action = self._detect_gesture(
            fingers, dist_idx_mid, dist_idx_thumb, dist_mid_thumb, lmList
        )

        # Apply debounce: mode must remain stable for debounce_ms
        now = self._now_ms()

        # Stop-move gesture should disable movement immediately.
        if detected_mode == "StopMove":
            self.current_mode = "None"
            self.stable_mode = "None"
            self.mode_start_time = now
            return "None", None

        # Movement modes should feel immediate; debounce here causes
        # visible "Mode: None" stalls and non-moving cursor.
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

    def _detect_gesture(self, fingers, dist_idx_mid, dist_idx_thumb, dist_mid_thumb, lmList):
        """
        Internal: map finger vector + distances to (mode, action).

        Args:
            fingers (list[int]): [thumb, index, mid, ring, pinky]
            dist_idx_mid (float): Distance between index(8) and middle(12) tips.
            dist_idx_thumb (float): Distance between thumb(4) and index(8) tips.
            dist_mid_thumb (float): Distance between thumb(4) and middle(12) tips.
            lmList (list): Landmark list for scroll reference.

        Returns:
            tuple: (detected_mode, action)
        """
        stop_pattern = self.profile.get("stop_pattern")
        if stop_pattern is not None and fingers == stop_pattern:
            self.click_ready = True
            self.last_scroll_y = None
            self.last_control_x = None
            self.last_control_y = None
            if self.drag_active:
                self.drag_active = False
                return "StopMove", "drag_end"
            return "StopMove", None

        # --- Move ---
        move_patterns = self.profile["move_patterns"]
        
        # Try direct membership test first (works for lists)
        try:
            is_move_pattern = fingers in move_patterns
        except (ValueError, TypeError):
            # Fallback for numpy arrays: use array_equal against configured patterns.
            is_move_pattern = any(np.array_equal(fingers, pattern) for pattern in move_patterns)
        
        if is_move_pattern:
            self.click_ready = True
            if self.drag_active:
                if dist_idx_thumb > self.drag_threshold:
                    self.drag_active = False
                    return "Move", "move"
                else:
                    return "Drag", "move"  # cursor movement while dragging
            return "Move", "move"

        # --- Click ---
        if fingers == self.profile["click_pattern"]:
            if self.click_ready:
                self.click_ready = False
                return "Click", "click"
            return "Click", None

        # --- Right Click ---
        if fingers == self.profile["right_click_pattern"]:
            if self.click_ready:
                self.click_ready = False
                return "RightClick", "right_click"
            return "RightClick", None

        # --- Drag ---
        if fingers == self.profile["drag_pattern"]:
            if not self.drag_active:
                self.drag_active = True
                return "Drag", "drag_start"
            if self.drag_active:
                return "Drag", "move"
            return "Drag", None

        # --- Scroll ---
        if fingers == self.profile["scroll_pattern"]:
            self.click_ready = True
            action = None
            if self.last_scroll_y is not None and len(lmList) > 8:
                delta_y = self.last_scroll_y - lmList[8][2]
                if abs(delta_y) > self.scroll_dead_zone:
                    scroll_amount = int(delta_y / self.scroll_sensitivity)
                    action = ("scroll", scroll_amount)
            self.last_scroll_y = lmList[8][2] if len(lmList) > 8 else None
            return "Scroll", action

        # --- Brightness control (optional) ---
        if self.enable_brightness_control and fingers == self.profile["brightness_pattern"]:
            action = None
            if len(lmList) > 8:
                curr_x = lmList[8][1]
                if self.last_control_x is not None:
                    delta_x = curr_x - self.last_control_x
                    if abs(delta_x) > self.pinch_control_dead_zone:
                        step = int(delta_x / max(1, self.pinch_control_scale))
                        action = ("brightness", step)
                self.last_control_x = curr_x
            return "Brightness", action

        # --- Volume control (optional) ---
        if self.enable_volume_control and fingers == self.profile["volume_pattern"]:
            action = None
            if len(lmList) > 8:
                curr_y = lmList[8][2]
                if self.last_control_y is not None:
                    delta_y = self.last_control_y - curr_y
                    if abs(delta_y) > self.pinch_control_dead_zone:
                        step = int(delta_y / max(1, self.pinch_control_scale))
                        action = ("volume", step)
                self.last_control_y = curr_y
            return "Volume", action

        # --- No recognized gesture ---
        self.click_ready = True
        self.last_scroll_y = None
        self.last_control_x = None
        self.last_control_y = None
        if self.drag_active:
            self.drag_active = False
            return "None", "drag_end"
        return "None", None

    def reset(self):
        """Reset all internal state (called when hand is lost from frame)."""
        self.current_mode = "None"
        self.stable_mode = "None"
        self.click_ready = True
        self.drag_active = False
        self.last_scroll_y = None
        self.last_control_x = None
        self.last_control_y = None

    @staticmethod
    def _now_ms():
        """Return current time in milliseconds."""
        return time.time() * 1000
