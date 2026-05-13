"""
AI Virtual Mouse — Phase 6 Test Suite
Unit tests for GestureClassifier, CoordinateMapper, and MouseController.

Run: python tests/test_phase6.py
"""

import math
import os
import sys
import time
import unittest

# Ensure project root on path (only needed when run directly, not via -m)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    CLICK_THRESHOLD_PX,
    DEBOUNCE_TIME_MS,
    DRAG_THRESHOLD_PX,
    FRAME_HEIGHT,
    SCROLL_DEAD_ZONE_PX,
    SCROLL_SENSITIVITY,
)
from src.gesture_classifier import GestureClassifier


# ── Mock helpers ────────────────────────────────────────────────────────────


def make_lmList(coords):
    """Build lmList from list of (x, y) tuples. Returns [[id, x, y], ...]."""
    return [[i, x, y] for i, (x, y) in enumerate(coords)]


# A realistic 21-landmark set: hand spread open, palm roughly center
# Indices: 0=wrist, 1-4=thumb, 5-8=index, 9-12=middle, 13-16=ring, 17-20=pinky
FULL_LANDMARKS = make_lmList(
    [
        (320, 400),  # 0  wrist
        (280, 320),  # 1  thumb cmc
        (250, 250),  # 2  thumb mcp
        (220, 190),  # 3  thumb ip
        (190, 140),  # 4  thumb tip
        (300, 300),  # 5  index mcp
        (260, 220),  # 6  index pip
        (240, 160),  # 7  index dip
        (220, 110),  # 8  index tip
        (330, 280),  # 9  middle mcp
        (310, 190),  # 10 middle pip
        (305, 130),  # 11 middle dip
        (300, 80),  # 12 middle tip
        (360, 300),  # 13 ring mcp
        (370, 220),  # 14 ring pip
        (380, 170),  # 15 ring dip
        (385, 130),  # 16 ring tip
        (390, 320),  # 17 pinky mcp
        (410, 260),  # 18 pinky pip
        (420, 220),  # 19 pinky dip
        (425, 190),  # 20 pinky tip
    ]
)


# Distance function using Euclidean distance on lmList
def make_distance_fn(lmList):
    def fn(p1, p2, draw=False):
        if p1 >= len(lmList) or p2 >= len(lmList):
            return 0, (0, 0), (0, 0, 0, 0)
        x1, y1 = lmList[p1][1], lmList[p1][2]
        x2, y2 = lmList[p2][1], lmList[p2][2]
        d = math.hypot(x2 - x1, y2 - y1)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        return d, (cx, cy), (x1, y1, x2, y2)

    return fn


# ── GestureClassifier Unit Tests ────────────────────────────────────────────


class TestGestureClassifier(unittest.TestCase):
    """Comprehensive tests for rule-based gesture classification"""

    def setUp(self):
        self.cf = GestureClassifier(
            click_threshold=CLICK_THRESHOLD_PX,
            drag_threshold=DRAG_THRESHOLD_PX,
            debounce_ms=DEBOUNCE_TIME_MS,
            scroll_sensitivity=SCROLL_SENSITIVITY,
            scroll_dead_zone=SCROLL_DEAD_ZONE_PX,
            gesture_style="practical_no_thumb",
        )
        self.lm = FULL_LANDMARKS
        self.dist_fn = make_distance_fn(self.lm)

    def make_dist_fn_with_pinch(self, idx_mid=None, idx_ring=None):
        """Override selected pinch distances while keeping others realistic."""
        base_fn = make_distance_fn(self.lm)

        def fn(p1, p2, draw=False):
            pair = {p1, p2}
            if idx_mid is not None and pair == {8, 12}:
                return idx_mid, (0, 0), (0, 0, 0, 0)
            if idx_ring is not None and pair == {8, 16}:
                return idx_ring, (0, 0), (0, 0, 0, 0)
            return base_fn(p1, p2, draw=draw)

        return fn

    def call_classify(self, fingers, lmList=None, wait_debounce=True):
        """Helper: call classify and optionally wait for debounce."""
        if lmList is None:
            lmList = self.lm
        mode, action = self.cf.classify(fingers, lmList, self.dist_fn)
        if wait_debounce:
            # Advance time to pass debounce
            self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
            mode, action = self.cf.classify(fingers, lmList, self.dist_fn)
        return mode, action

    # ── T1: Move Mode ──────────────────────────────────────────────────
    def test_t1_move_mode(self):
        """T1: index only up (thumb ignored) → Move mode, action=move"""
        mode, action = self.call_classify([0, 1, 0, 0, 0])
        self.assertEqual(mode, "Move")
        self.assertEqual(action, "move")
        mode, action = self.call_classify([1, 1, 0, 0, 0])
        self.assertEqual(mode, "Move")
        self.assertEqual(action, "move")

    # ── T2: Click Mode ─────────────────────────────────────────────────
    def test_t2_click_entry_triggers(self):
        """T2: index+middle pinch should click once after hold"""
        pinch_fn = self.make_dist_fn_with_pinch(idx_mid=20)
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_fn)
        self.assertIsNone(action)
        # Debounce + hold window passed, action fires once
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_fn)
        self.assertEqual(action, "click")
        self.assertEqual(mode, "Click")
        # Holding pinch should not repeat
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_fn)
        self.assertIsNone(action)

    def test_t2_click_near_tips_trigger(self):
        """T2: no click when pinch hold time has not elapsed"""
        pinch_fn = self.make_dist_fn_with_pinch(idx_mid=20)
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_fn)
        self.assertIsNone(action)
        self.cf._now_ms = lambda: time.time() * 1000 + 50
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_fn)
        self.assertIsNone(action)

    def test_t2_click_rearms_after_release(self):
        """T2: releasing pinch should re-arm click trigger"""
        pinch_on_fn = self.make_dist_fn_with_pinch(idx_mid=20)
        pinch_off_fn = self.make_dist_fn_with_pinch(idx_mid=80)
        self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertEqual(action, "click")
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertIsNone(action)
        # release to move and click_ready should be restored
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_off_fn)
        self.assertIsNone(action)
        mode, action = self.cf.classify([0, 1, 0, 0, 0], self.lm, self.dist_fn)
        self.assertTrue(self.cf.click_ready)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 5
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertIsNone(action)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 205
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertEqual(action, "click")

    # ── T3: Right Click ────────────────────────────────────────────────
    def test_t3_right_click_mode(self):
        """T3: index+ring pinch gesture → RightClick mode"""
        pinch_fn = self.make_dist_fn_with_pinch(idx_ring=22)
        mode, action = self.cf.classify([0, 1, 1, 1, 0], self.lm, pinch_fn)
        self.assertIsNone(action)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 1, 1, 0], self.lm, pinch_fn)
        self.assertEqual(action, "right_click")
        self.assertEqual(mode, "RightClick")

    # ── T4: Drag Mode ──────────────────────────────────────────────────
    def test_t4_drag_start(self):
        """T4: fist [*,0,0,0,0] → drag_start"""
        mode, action = self.cf.classify([0, 0, 0, 0, 0], self.lm, self.dist_fn)
        self.assertEqual(action, "drag_start")  # fires immediately
        mode, action = self.cf.classify([0, 0, 0, 0, 0], self.lm, self.dist_fn)
        self.assertEqual(mode, "Drag")
        self.assertEqual(action, "move")
        self.assertTrue(self.cf.drag_active)

    def test_t4_drag_end_on_finger_change(self):
        """T4: drag ends when fingers change from 3 to 2"""
        # First activate drag
        self.cf.classify([0, 0, 0, 0, 0], self.lm, self.dist_fn)
        self.assertTrue(self.cf.drag_active)  # drag activated immediately
        mode, action = self.cf.classify([0, 0, 0, 0, 0], self.lm, self.dist_fn)
        self.assertEqual(mode, "Drag")
        self.assertEqual(action, "move")

        # Now switch to Move (index only)
        mode, action = self.cf.classify([0, 1, 0, 0, 0], self.lm, self.dist_fn)
        self.assertEqual(self.cf.current_mode, "Move")  # detected, not yet stable
        # Advance time to pass debounce
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 0, 0, 0], self.lm, self.dist_fn)
        self.assertEqual(mode, "Move")
        self.assertEqual(action, "move")
        self.assertFalse(self.cf.drag_active)

    # ── T5: Scroll Mode ────────────────────────────────────────────────
    def test_t5_scroll_mode(self):
        """T5: [thumb,1,1,1,1] → Scroll mode"""
        mode, action = self.cf.classify([0, 1, 1, 1, 1], self.lm, self.dist_fn)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 1, 1, 1], self.lm, self.dist_fn)
        self.assertEqual(mode, "Scroll")

    def test_t5_scroll_uses_center_boundary(self):
        """T5: scroll direction follows index position vs frame center"""
        scroll_up_lm = [row[:] for row in self.lm]
        scroll_down_lm = [row[:] for row in self.lm]
        scroll_up_lm[8][2] = 120
        scroll_down_lm[8][2] = FRAME_HEIGHT - 60

        self.cf._now_ms = lambda: 1000
        self.cf.classify([0, 1, 1, 1, 1], scroll_up_lm, make_distance_fn(scroll_up_lm))
        self.cf._now_ms = lambda: 1400
        mode, action_up = self.cf.classify(
            [0, 1, 1, 1, 1], scroll_up_lm, make_distance_fn(scroll_up_lm)
        )
        self.assertEqual(mode, "Scroll")
        self.assertIsNotNone(action_up)
        self.assertEqual(action_up[0], "scroll")
        self.assertGreater(action_up[1], 0)

        self.cf._now_ms = lambda: 1800
        mode, action_down = self.cf.classify(
            [0, 1, 1, 1, 1], scroll_down_lm, make_distance_fn(scroll_down_lm)
        )
        self.assertEqual(mode, "Scroll")
        self.assertIsNotNone(action_down)
        self.assertEqual(action_down[0], "scroll")
        self.assertLess(action_down[1], 0)

    # ── T6: Hand Lost ──────────────────────────────────────────────────
    def test_t6_hand_lost_reset(self):
        """T6: empty lmList → mode=None"""
        mode, action = self.cf.classify([0, 0, 0, 0, 0], [], self.dist_fn)
        self.assertEqual(mode, "None")
        self.assertIsNone(action)
        self.assertEqual(self.cf.current_mode, "None")

    def test_t6_none_fingers_vector(self):
        """T6: fist should trigger Drag mode in practical mapping"""
        mode, action = self.cf.classify([0, 0, 0, 0, 0], self.lm, self.dist_fn)
        self.assertEqual(mode, "Drag")
        self.assertEqual(action, "drag_start")

    # ── T7: Debounce ───────────────────────────────────────────────────
    def test_t7_debounce_no_flip_before_timeout(self):
        """T7: mode should NOT change before debounce time elapses"""
        # Start in Move
        self.call_classify([0, 1, 0, 0, 0])

        # Switch to Click - immediately check, should still show old stable_mode
        self.cf._now_ms = lambda: time.time() * 1000  # reset to now
        self.cf.classify([0, 1, 1, 0, 0], self.lm, self.dist_fn)
        # current_mode changed but stable_mode should still be "Move"
        self.assertEqual(self.cf.current_mode, "Click")
        self.assertEqual(self.cf.stable_mode, "Move")  # not yet debounced

        # After debounce, should flip
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        self.cf.classify(
            [0, 1, 1, 0, 0],
            self.lm,
            self.make_dist_fn_with_pinch(idx_mid=20),
        )
        self.assertEqual(self.cf.stable_mode, "Click")

    # ── T8: No Auto-repeat Click ───────────────────────────────────────
    def test_t8_no_click_repeat(self):
        """T8: holding click gesture should NOT fire click twice"""
        pinch_on_fn = self.make_dist_fn_with_pinch(idx_mid=20)
        pinch_off_fn = self.make_dist_fn_with_pinch(idx_mid=80)
        # First call: no action until hold-time satisfied
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertIsNone(action)
        # Debounce mode — action should be None (click_ready is False)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertEqual(mode, "Click")
        self.assertEqual(action, "click")
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertIsNone(action)  # no repeat

        # Second call without releasing — should not fire
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_on_fn)
        self.assertIsNone(action)  # no repeat

        # Now release by switching to a different gesture
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_off_fn)
        self.assertIsNone(action)
        mode, action = self.cf.classify([0, 1, 0, 0, 0], self.lm, self.dist_fn)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 0, 0, 0], self.lm, self.dist_fn)
        self.assertTrue(self.cf.click_ready)  # ready again

    def test_t8_click_freezes_movement_temporarily(self):
        """Click trigger should activate short movement freeze window"""
        pinch_fn = self.make_dist_fn_with_pinch(idx_mid=20)
        self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_fn)
        self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
        mode, action = self.cf.classify([0, 1, 1, 0, 0], self.lm, pinch_fn)
        self.assertEqual(action, "click")
        self.assertTrue(self.cf.is_movement_frozen())

    # ── Edge cases ─────────────────────────────────────────────────────
    def test_invalid_distance_fn_graceful(self):
        """Calling classify with None distance function should return None"""
        mode, action = self.cf.classify([0, 1, 0, 0, 0], self.lm, None)
        self.assertEqual(mode, "None")

    def test_reset_clears_state(self):
        """reset() should clear all internal state"""
        self.cf.current_mode = "Move"
        self.cf.stable_mode = "Move"
        self.cf.click_ready = False
        self.cf.drag_active = True
        self.cf.last_scroll_action_ms = 100
        self.cf.left_pinch_active = True
        self.cf.right_pinch_active = True
        self.cf.freeze_until_ms = 1234
        self.cf.reset()
        self.assertEqual(self.cf.current_mode, "None")
        self.assertEqual(self.cf.stable_mode, "None")
        self.assertTrue(self.cf.click_ready)
        self.assertFalse(self.cf.drag_active)
        self.assertEqual(self.cf.last_scroll_action_ms, 0)
        self.assertFalse(self.cf.left_pinch_active)
        self.assertFalse(self.cf.right_pinch_active)
        self.assertEqual(self.cf.freeze_until_ms, 0)

    def test_all_finger_combos_no_gesture(self):
        """Various unrecognized finger combos → None"""
        unrecognized = [
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0],
            [1, 0, 0, 1, 1],
        ]
        for fingers in unrecognized:
            self.cf.reset()
            mode, action = self.cf.classify(fingers, self.lm, self.dist_fn)
            self.cf._now_ms = lambda: time.time() * 1000 + DEBOUNCE_TIME_MS + 1
            mode, action = self.cf.classify(fingers, self.lm, self.dist_fn)
            with self.subTest(fingers=fingers):
                self.assertEqual(mode, "None", f"fingers={fingers}")


# ── CoordinateMapper Unit Tests ─────────────────────────────────────────────


class TestCoordinateMapper(unittest.TestCase):
    """Tests for coordinate mapping and exponential smoothing"""

    @classmethod
    def setUpClass(cls):
        """Mock autopy.screen.size before importing CoordinateMapper"""
        import autopy

        cls._orig_size = autopy.screen.size
        autopy.screen.size = lambda: (1920.0, 1080.0)

    @classmethod
    def tearDownClass(cls):
        import autopy

        autopy.screen.size = cls._orig_size

    def setUp(self):
        from src.coordinate_mapper import CoordinateMapper

        self.mapper = CoordinateMapper(
            frame_width=640,
            frame_height=480,
            frame_reduction=100,
            smoothing_factor=7.0,
        )

    def test_map_center_to_center(self):
        """Center of camera frame → center of screen"""
        x, y = self.mapper.map_to_screen(320, 240)
        self.assertAlmostEqual(x, 960.0, delta=5)
        self.assertAlmostEqual(y, 540.0, delta=5)

    def test_map_top_left_to_origin(self):
        """Top-left dead-zone edge → (0, 0)"""
        x, y = self.mapper.map_to_screen(100, 100)
        self.assertAlmostEqual(x, 0.0, delta=1)
        self.assertAlmostEqual(y, 0.0, delta=1)

    def test_map_bottom_right_to_max(self):
        """Bottom-right dead-zone edge → (1920, 1080)"""
        x, y = self.mapper.map_to_screen(540, 380)
        self.assertAlmostEqual(x, 1920.0, delta=5)
        self.assertAlmostEqual(y, 1080.0, delta=5)

    def test_map_clamps_at_far_left(self):
        """Coordinate at x=0 stays at 0 (below dead zone min)"""
        x, y = self.mapper.map_to_screen(0, 240)
        # numpy.interp extrapolates downward for below-left input
        self.assertTrue(x <= 0)

    def test_map_clamps_at_far_right(self):
        """Coordinate at x=640 stays at 1920 (above dead zone max)"""
        x, y = self.mapper.map_to_screen(640, 240)
        self.assertTrue(x >= 1920.0)

    def test_smoothing_initialized_on_first_call(self):
        """First smooth call initializes directly to raw value"""
        sx, sy = self.mapper.smooth(500.0, 300.0)
        self.assertEqual(sx, 500.0)
        self.assertEqual(sy, 300.0)
        self.assertTrue(self.mapper.initialized)

    def test_smoothing_converges(self):
        """After many frames, smoothed approaches raw"""
        self.mapper.smooth(500.0, 300.0)
        for _ in range(50):
            self.mapper.smooth(1000.0, 600.0)
        sx, sy = self.mapper.smooth_x, self.mapper.smooth_y
        self.assertAlmostEqual(sx, 1000.0, delta=10)
        self.assertAlmostEqual(sy, 600.0, delta=10)

    def test_smoothing_prevents_jumps(self):
        """Abrupt change is damped, not instantaneous"""
        self.mapper.smooth(500.0, 300.0)
        sx, sy = self.mapper.smooth(1000.0, 600.0)  # sudden jump
        delta = (1000.0 - 500.0) / 7.0  # expected step size
        self.assertAlmostEqual(sx, 500.0 + delta, delta=1)

    def test_reset_smoothing(self):
        """Reset → next smooth initializes fresh"""
        self.mapper.smooth(500.0, 300.0)
        self.mapper.reset_smoothing()
        self.assertFalse(self.mapper.initialized)
        sx, sy = self.mapper.smooth(800.0, 400.0)
        self.assertEqual(sx, 800.0)
        self.assertEqual(sy, 400.0)

    def test_process_full_pipeline(self):
        """process() chains map + smooth correctly"""
        sx, sy = self.mapper.process(320, 240)
        # Should be near screen center
        self.assertAlmostEqual(sx, 960.0, delta=50)
        self.assertAlmostEqual(sy, 540.0, delta=50)


# ── MouseController Unit Tests ──────────────────────────────────────────────


class TestMouseController(unittest.TestCase):
    """Tests for mouse controller (mock autopy to avoid actual mouse movement)"""

    @classmethod
    def setUpClass(cls):
        import autopy

        cls._orig_move = autopy.mouse.move
        cls._orig_click = autopy.mouse.click
        cls._orig_toggle = autopy.mouse.toggle
        cls._has_scroll = hasattr(autopy.mouse, "scroll")
        if cls._has_scroll:
            cls._orig_scroll = autopy.mouse.scroll
        cls._orig_size = autopy.screen.size

        cls.move_calls = []
        cls.click_calls = []
        cls.toggle_calls = []
        cls.scroll_calls = []

        def mock_move(x, y):
            cls.move_calls.append((x, y))

        def mock_click(button=None):
            cls.click_calls.append(button)

        def mock_toggle(down, button=None):
            cls.toggle_calls.append((down, button))

        def mock_scroll(amount):
            cls.scroll_calls.append(amount)

        autopy.mouse.move = mock_move
        autopy.mouse.click = mock_click
        autopy.mouse.toggle = mock_toggle
        if cls._has_scroll:
            autopy.mouse.scroll = mock_scroll
        autopy.screen.size = lambda: (1920.0, 1080.0)

    @classmethod
    def tearDownClass(cls):
        import autopy

        autopy.mouse.move = cls._orig_move
        autopy.mouse.click = cls._orig_click
        autopy.mouse.toggle = cls._orig_toggle
        if cls._has_scroll:
            autopy.mouse.scroll = cls._orig_scroll
        autopy.screen.size = cls._orig_size

    def setUp(self):
        self.move_calls.clear()
        self.click_calls.clear()
        self.toggle_calls.clear()
        self.scroll_calls.clear()

        from src.mouse_controller import MouseController

        self.mc = MouseController(click_delay=0.0)  # no delay in tests

    def test_move_executed(self):
        self.mc.execute("move", screen_x=500.0, screen_y=300.0)
        self.assertEqual(len(self.move_calls), 1)
        self.assertEqual(self.move_calls[0], (500, 300))

    def test_coordinate_clamped_to_zero(self):
        """Negative coordinates are clamped to 0"""
        self.mc.execute("move", screen_x=-100.0, screen_y=-50.0)
        self.assertEqual(self.move_calls[0], (0, 0))

    def test_coordinate_clamped_to_max(self):
        """Coordinates beyond screen are clamped"""
        self.mc.execute("move", screen_x=3000.0, screen_y=2000.0)
        self.assertEqual(self.move_calls[0], (1919, 1079))

    def test_click_executed(self):
        self.mc.execute("click")
        self.assertEqual(len(self.click_calls), 1)

    def test_right_click_executed(self):
        self.mc.execute("right_click")
        self.assertEqual(len(self.click_calls), 1)

    def test_drag_start_end(self):
        self.mc.execute("drag_start")
        self.assertEqual(len(self.toggle_calls), 1)
        self.assertTrue(self.toggle_calls[0][0])  # down=True

        self.mc.execute("drag_end")
        self.assertEqual(len(self.toggle_calls), 2)
        self.assertFalse(self.toggle_calls[1][0])  # down=False

    def test_scroll_executed(self):
        if not TestMouseController._has_scroll:
            self.skipTest("autopy.mouse.scroll not available")
        self.mc.execute(("scroll", 5))
        self.assertEqual(len(self.scroll_calls), 1)
        self.assertEqual(self.scroll_calls[0], 5)

    def test_cleanup_releases_drag(self):
        self.mc.drag_active = True
        self.mc.cleanup()
        self.assertEqual(len(self.toggle_calls), 1)
        self.assertFalse(self.toggle_calls[0][0])


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run tests verbosely
    unittest.main(verbosity=2)
