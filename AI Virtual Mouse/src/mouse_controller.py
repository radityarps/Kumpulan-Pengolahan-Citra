"""
AI Virtual Mouse — Mouse Controller
Thin wrapper around Autopy for programmatic mouse control.

Translates action strings from GestureClassifier into Autopy API calls.
Handles coordinate clamping, drag state tracking, and cleanup.
"""

import time
import ctypes
import autopy
from src.config import CLICK_DELAY


class MouseController:
    """
    Wraps Autopy mouse functions and translates abstract actions
    ("move", "click", "drag_start", etc.) into concrete OS-level calls.

    Tracks drag state internally to ensure clean release on exit.
    """

    def __init__(self, click_delay=CLICK_DELAY):
        """
        Initialize mouse controller.

        Args:
            click_delay (float): Seconds to sleep after click to prevent
                                 accidental double-clicks.
        """
        self.click_delay = click_delay
        self.drag_active = False

        # Scroll may not be available in some Autopy versions (e.g., 4.0.1)
        self._scroll_available = hasattr(autopy.mouse, "scroll")
        self._windows_scroll_fallback = hasattr(ctypes, "windll") and hasattr(
            ctypes.windll, "user32"
        )
        if not self._scroll_available:
            if self._windows_scroll_fallback:
                print(
                    "[MouseController] INFO: autopy.mouse.scroll unavailable. "
                    "Using Windows mouse wheel fallback."
                )
            else:
                print(
                    "[MouseController] WARNING: autopy.mouse.scroll not available. "
                    "Scroll mode will be ignored."
                )

    def execute(self, action, screen_x=None, screen_y=None, **kwargs):
        """
        Execute a mouse action.

        Translates abstract action strings into concrete Autopy calls.
        Clamps screen coordinates to prevent out-of-bounds errors.

        Args:
            action: Action to perform. One of:
                - "move"          → move cursor to (screen_x, screen_y)
                - "click"         → left click with CLICK_DELAY sleep
                - "double_click"  → two rapid left clicks
                - "right_click"   → right click
                - "drag_start"    → press and hold left button
                - "drag_end"      → release left button
                - ("scroll", N)   → scroll N units (positive=up, negative=down)
            screen_x (float | None): Target x-coordinate for "move" action.
            screen_y (float | None): Target y-coordinate for "move" action.
            **kwargs: Additional arguments (reserved for future use).

        Side effects:
            Updates self.drag_active for drag_start/drag_end tracking.
        """
        # Clamp coordinates to screen bounds
        if screen_x is not None and screen_y is not None:
            max_x, max_y = autopy.screen.size()
            screen_x = max(0.0, min(float(screen_x), max_x - 1))
            screen_y = max(0.0, min(float(screen_y), max_y - 1))

        if action == "move":
            autopy.mouse.move(int(screen_x), int(screen_y))

        elif action == "click":
            autopy.mouse.click()
            time.sleep(self.click_delay)

        elif action == "double_click":
            autopy.mouse.click()
            time.sleep(max(0.01, self.click_delay / 2))
            autopy.mouse.click()
            time.sleep(self.click_delay)

        elif action == "right_click":
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
            time.sleep(self.click_delay)

        elif action == "drag_start":
            autopy.mouse.toggle(button=autopy.mouse.Button.LEFT, down=True)
            self.drag_active = True

        elif action == "drag_end":
            autopy.mouse.toggle(button=autopy.mouse.Button.LEFT, down=False)
            self.drag_active = False

        elif isinstance(action, tuple) and action[0] == "scroll":
            _scroll_type, amount = action
            self._scroll(int(amount))

    def cleanup(self):
        """
        Release any held mouse buttons.

        MUST be called on program exit. Without this, if the program
        exits during an active drag, the mouse left button stays
        "pressed" until the system is restarted or the user manually
        clicks.
        """
        if self.drag_active:
            autopy.mouse.toggle(button=autopy.mouse.Button.LEFT, down=False)
            self.drag_active = False

    def _scroll(self, amount):
        """
        Scroll the mouse wheel.

        ╔══════════════════════════════════════════════════════════════╗
        ║  MASALAH #1 / Slide 5: Scroll Nggak Jalan
        ╠══════════════════════════════════════════════════════════════╣
        ║  BEFORE (Tutorial — Murtaza's Workshop):
        ║    autopy.mouse.toggle(down=True)   // tahan tombol kiri
        ║    autopy.mouse.toggle(down=False)  // lepas tombol kiri
        ║    Fungsi toggle() untuk press/release tombol — BUKAN
        ║    scroll wheel. Akibat: kursor gerak, halaman tidak.
        ║
        ║  AFTER (Fix):
        ║    autopy.mouse.scroll(amount)                   # jalur utama
        ║    ctypes.windll.user32.mouse_event(0x0800, ...)  # fallback
        ║    Kirim MOUSEEVENTF_WHEEL ke Windows API — scroll wheel
        ║    beneran, beda fundamental dengan toggle().
        ║
        ║  SEBAB: autopy 4.0.1 tidak punya mouse.scroll().
        ║    Fallback ctypes = Windows-only.
        ╚══════════════════════════════════════════════════════════════╝

        Prefers autopy.mouse.scroll() when available. Falls back to
        Windows API mouse_event(MOUSEEVENTF_WHEEL) on Windows when
        autopy lacks scroll support (e.g., version 4.0.1).

        Silently ignored on non-Windows systems without autopy scroll.

        Args:
            amount (int): Scroll direction and magnitude.
                Positive = up (away from user).
                Negative = down (toward user).
                0 = no action.

        Note:
            Windows wheel delta is in multiples of 120 (WHEEL_DELTA).
            Each unit = one "notch" of mouse wheel rotation.
        """
        if amount == 0:
            return
        if self._scroll_available:
            autopy.mouse.scroll(int(amount))
            return
        if self._windows_scroll_fallback:
            # Windows wheel delta is multiples of 120.
            wheel_delta = int(amount) * 120
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, wheel_delta, 0)
