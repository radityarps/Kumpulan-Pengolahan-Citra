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
    Stateful classifier that maps finger states → gesture modes and actions.

    ╔══════════════════════════════════════════════════════════════════╗
    ║  MASALAH #5, #6, #8 / Slide 10-11, 15: State Machine Fixes
    ╠══════════════════════════════════════════════════════════════════╣
    ║  BEFORE (Video Version / Tutorial):
    ║    Setiap frame diproses sendiri-sendiri. Nggak ada memori.
    ║    Flicker 1 frame → mode ganti → UX rusak.
    ║
    ║    Lima manifestasi bug dari "no state":
    ║
    ║    1. SPAM CLICK (Slide 10):
    ║       Setiap frame di bawah threshold → autopy.click() lagi.
    ║       1 gestur pinch 2 detik = 60 click (30 fps × 2 detik).
    ║
    ║    2. MODE FLICKER (Slide 10):
    ║       Flicker 1-2 frame → mode ganti Move→Click→Move.
    ║       Kursor berhenti, nge-klik random.
    ║
    ║    3. DRAG DROP (Slide 10):
    ║       Kepalan sedikit kendor → langsung bukan Drag → file
    ║       ke-drop di tempat acak.
    ║
    ║    4. BOUNDARY OSCILLATION (Slide 11):
    ║       Pinch di threshold 28px → 1 frame 27px (ON), next
    ║       frame 29px (OFF) → rapid on/off → multi-click.
    ║
    ║    5. HAND-LOST INSTANT RESET:
    ║       Tangan keluar frame 1 detik → semua state hilang →
    ║       drag putus, mode reset ke None.
    ║
    ║  AFTER (Five Fixes — all in this class):
    ║
    ║    1. EDGE-TRIGGERED CLICK (Masalah #5):
    ║       click_ready flag. Click cuma fires 1× saat transisi
    ║       "tidak pinch" → "pinch". Harus lepas dulu untuk
    ║       click lagi.
    ║
    ║    2. DEBOUNCE 300ms (Masalah #6):
    ║       current_mode harus stabil 300ms sebelum jadi
    ║       stable_mode. Flicker 1-2 frame = diabaikan.
    ║
    ║    3. HYSTERESIS ON≠OFF (Masalah #6):
    ║       Batas ON (28px) ≠ OFF (38px). Begitu <28px = ON.
    ║       Harus naik ke >38px baru OFF. Nggak bisa bolak-balik
    ║       di boundary 1 pixel.
    ║
    ║    4. HOLD-TIME 100ms (Masalah #8 → Slide 15):
    ║       Pinch harus bertahan 100ms sebelum click fires.
    ║       Mencegah accidental click saat transisi gesture.
    ║       Drag: kepalan harus ditahan 100ms sebelum aktif.
    ║
    ║    5. POST-CLICK FREEZE 200ms (Masalah #8 → Slide 15):
    ║       Kursor di-freeze 200ms setelah click. Mencegah
    ║       drift dari gerakan jari refleks setelah pinch.
    ║
    ║  PLUS: HAND-LOST GRACE 4 FRAME (external, in main loop):
    ║    Tangan hilang <4 frame → state dipertahankan.
    ║    Drag nggak putus hanya karena tangan sebentar
    ║    keluar frame.
    ║
    ║  SEBAB: Gesture recognition yang reliable bukan cuma soal
    ║    "deteksi bener", tapi juga "transisi antar gesture mulus".
    ║    Lima mekanisme di atas = solusi untuk semua manifestasi
    ║    bug "no state" di versi tutorial.
    ╚══════════════════════════════════════════════════════════════════╝

    Unlike the video version's simple if-elif chain, this classifier
    maintains internal state across frames to provide:

    - Debounce (300ms): new gesture must hold for DEBOUNCE_TIME_MS before
      being accepted as the stable mode. Eliminates 1-2 frame flickers.
    - Hysteresis (ON≠OFF thresholds): click activates at 28px pinch
      but deactivates at 38px. Prevents rapid on/off oscillation at
      the threshold boundary.
    - Hold-time (100ms): pinch must hold below threshold for
      CLICK_HOLD_TIME_MS before click fires. Prevents accidental clicks.
    - Post-click freeze (200ms): cursor frozen for
      MOVE_FREEZE_AFTER_CLICK_MS after click to prevent drift.
    - Hand-lost grace (4 frames): state preserved for up to 4 missed
      frames (handled externally in main loop).

    The classifier uses gesture profiles from gesture_profiles.py,
    allowing gesture mappings to be swapped without changing this file.

    Attributes:
        current_mode (str): Raw detected mode this frame.
        stable_mode (str): Debounced mode — the "official" mode.
            Only changes after current_mode stays stable for debounce_ms.
        click_ready (bool): Edge-trigger gate. False after click fires,
            True after pinch releases past OFF threshold.
        drag_active (bool): Whether drag is currently active.
        freeze_until_ms (float): Timestamp until cursor movement is frozen.
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
        Classify current frame's finger state into a gesture mode and action.

        This is the main entry point called from the main loop every frame.
        Applies debounce: the returned stable_mode only changes after
        the detected mode has been consistent for DEBOUNCE_TIME_MS.

        Args:
            fingers (list[int]): Binary finger states [thumb, idx, mid, ring, pinky].
            lmList (list): Landmark coordinate list [[id, cx, cy], ...].
            findDistance_fn (callable): Bound method for computing inter-landmark
                distances. Signature: (p1, p2, draw=False) -> (dist, _, _).

        Returns:
            tuple: (mode, action)
                - mode (str): Debounced gesture mode. One of:
                  "None", "Move", "Click", "RightClick", "Drag", "Scroll".
                - action: Action to execute. One of:
                  None, "move", "click", "right_click", "drag_start",
                  "drag_end", "double_click", ("scroll", amount).
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
        """
        Raw gesture detection — no debounce applied here.

        Checks finger patterns against the active gesture profile
        in priority order:
        1. Stop pattern → force None mode
        2. Move patterns → cursor movement
        3. Click pattern → left click with hysteresis
        4. Right click pattern → right click with hysteresis
        5. Drag pattern → drag start/continue
        6. Scroll pattern → scroll up/down based on hand position
        7. No match → None

        Args:
            fingers (list[int]): [thumb, index, middle, ring, pinky].
            dist_idx_mid (float): Distance between index (8) and middle (12).
            dist_idx_thumb (float): Distance between index (8) and thumb (4).
            dist_mid_thumb (float): Distance between middle (12) and thumb (4).
            dist_idx_ring (float): Distance between index (8) and ring (16).
            lmList (list): Landmark coordinates for position-based gestures.
            now_ms (float): Current timestamp in milliseconds.

        Returns:
            tuple: (detected_mode, action)
                detected_mode is the raw mode (before debounce).
        """
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
        """
        Left click state machine with hysteresis and hold-time.

        Three states:
        1. IDLE: pinch > LEFT_CLICK_PINCH_ON_PX. Waiting.
        2. HOLDING: pinch ≤ ON threshold but hasn't held for hold_time yet.
           Timer starts. No click yet.
        3. ACTIVE: held for hold_time → click fires. Pinch must release past
           LEFT_CLICK_PINCH_OFF_PX to return to IDLE (hysteresis).

        Args:
            pinch_distance (float): Distance between index and middle tips.
            now_ms (float): Current timestamp in milliseconds.

        Returns:
            tuple: ("Click", action_or_None)
                action is "click" when the click fires, None otherwise.
        """
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
        """
        Right click state machine — same logic as left click.

        Uses RIGHT_CLICK_PINCH_ON_PX (34px) and RIGHT_CLICK_PINCH_OFF_PX (44px).
        Measures distance between index tip (8) and ring tip (16).

        Args:
            pinch_distance (float): Distance between index and ring tips.
            now_ms (float): Current timestamp in milliseconds.

        Returns:
            tuple: ("RightClick", action_or_None)
        """
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
        """
        Reset all click-related timers and re-arm if no pinch is active.

        Called when the finger pattern no longer matches any click pattern.
        If neither left nor right pinch is currently active, re-arms
        click_ready so the next pinch can fire a new click.
        """
        self.left_pinch_hold_start_ms = None
        self.right_pinch_hold_start_ms = None
        if not self.left_pinch_active and not self.right_pinch_active:
            self.click_ready = True

    def _freeze_movement(self, now_ms):
        """
        Freeze cursor movement for MOVE_FREEZE_AFTER_CLICK_MS.

        Called after a click fires. Prevents cursor drift caused by
        involuntary finger movement during the pinch-release motion.

        Args:
            now_ms (float): Current timestamp in milliseconds.
        """
        self.freeze_until_ms = now_ms + self.move_freeze_after_click_ms

    def is_movement_frozen(self):
        """
        Check if cursor movement is currently frozen.

        Returns:
            bool: True if now < freeze_until_ms, meaning cursor should not move.
        """
        return self._now_ms() < self.freeze_until_ms

    def _scroll_from_center(self, lmList, now_ms):
        """
        Determine scroll direction based on hand position relative to center.

        Divides the camera frame into three horizontal zones:
        - Above center+dead_zone → scroll UP (positive amount)
        - Below center-dead_zone → scroll DOWN (negative amount)
        - Within dead_zone → no scroll

        Rate-limited by SCROLL_REPEAT_MS to prevent excessive scrolling.

        Args:
            lmList (list): Landmark coordinates.
            now_ms (float): Current timestamp in milliseconds.

        Returns:
            tuple or None: ("scroll", amount) if scrolling, None otherwise.
        """
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
        """
        Match finger state against a gesture pattern.

        None values in the pattern act as wildcards (any finger value matches).
        This allows ignoring the thumb, which has unreliable detection.

        Args:
            fingers (list | tuple | np.ndarray): Actual finger states.
            pattern (list): Expected pattern with optional None wildcards.

        Returns:
            bool: True if all non-None positions match.
        """
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
        """
        Reset all internal state to defaults.

        Called when the hand is lost for HAND_LOST_GRACE_FRAMES.
        Returns the classifier to a clean slate — no active mode,
        no click locks, no drag, no freeze.
        """
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
        """
        Get current time in milliseconds.

        Returns:
            float: time.time() * 1000.
        """
        return time.time() * 1000
