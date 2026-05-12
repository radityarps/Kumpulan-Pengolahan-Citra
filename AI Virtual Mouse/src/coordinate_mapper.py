"""
AI Virtual Mouse — Coordinate Mapper
Maps hand landmark coordinates from camera space (640×480) to screen space
using linear interpolation, then applies exponential smoothing to reduce jitter.

Screen resolution is auto-detected via Autopy.
"""

import numpy as np
import autopy
from src.config import (
    FRAME_WIDTH,
    FRAME_HEIGHT,
    FRAME_REDUCTION,
    SMOOTHING_FACTOR,
)


class CoordinateMapper:
    """
    Camera-to-screen coordinate mapping with exponential smoothing.

    Pipeline:
      1. Interpolate camera (x,y) → screen (x,y) with dead-zone margins
      2. Apply exponential smoothing to suppress jitter
    """

    def __init__(
        self,
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        frame_reduction=FRAME_REDUCTION,
        smoothing_factor=SMOOTHING_FACTOR,
    ):
        """
        Initialize mapper with frame dimensions and smoothing parameters.

        Args:
            frame_width (int): Camera frame width in pixels (default 640).
            frame_height (int): Camera frame height in pixels (default 480).
            frame_reduction (int): Dead-zone margin (px) at each frame edge.
                                   Hand near the frame border won't push cursor
                                   all the way to the screen edge.
            smoothing_factor (float): Exponential smoothing weight.
                                      Higher = smoother but more lag.
                                      Lower = responsive but jittery.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_reduction = frame_reduction
        self.smoothing_factor = smoothing_factor

        # Auto-detect screen dimensions
        self.screen_width, self.screen_height = autopy.screen.size()

        # Smoothing state — initialized on first valid input
        self.smooth_x = 0.0
        self.smooth_y = 0.0
        self.initialized = False

    def map_to_screen(self, cx, cy):
        """
        Map camera pixel coordinates to screen coordinates.

        Uses numpy.interp with frame_reduction margins to create a
        comfortable dead zone at the frame edges.

        Args:
            cx (int): Camera x-coordinate (pixels, 0..frame_width).
            cy (int): Camera y-coordinate (pixels, 0..frame_height).

        Returns:
            tuple[float, float]: (screen_x, screen_y) mapped coordinates.
        """
        x = np.interp(
            cx,
            [self.frame_reduction, self.frame_width - self.frame_reduction],
            [0, self.screen_width],
        )
        y = np.interp(
            cy,
            [self.frame_reduction, self.frame_height - self.frame_reduction],
            [0, self.screen_height],
        )
        return float(x), float(y)

    def smooth(self, raw_x, raw_y):
        """
        Apply exponential smoothing to raw screen coordinates.

        Formula:
          smooth[t] = smooth[t-1] + (raw - smooth[t-1]) / smoothing_factor

        On the first call after initialization or reset, the smoothed
        value is set directly to the raw value to avoid convergence lag.

        Args:
            raw_x (float): Raw mapped x-coordinate.
            raw_y (float): Raw mapped y-coordinate.

        Returns:
            tuple[float, float]: (smooth_x, smooth_y) smoothed coordinates.
        """
        if not self.initialized:
            self.smooth_x = raw_x
            self.smooth_y = raw_y
            self.initialized = True
        else:
            self.smooth_x += (raw_x - self.smooth_x) / self.smoothing_factor
            self.smooth_y += (raw_y - self.smooth_y) / self.smoothing_factor
        return self.smooth_x, self.smooth_y

    def reset_smoothing(self):
        """
        Reset smoothing state.

        Call this when the hand is lost from the frame so the cursor
        doesn't jump when the hand reappears. The next smooth() call
        will initialize directly to the raw value.
        """
        self.initialized = False

    def process(self, cx, cy):
        """
        Full pipeline: map camera coordinates → smooth → return screen coordinates.

        Convenience method that chains map_to_screen() and smooth().

        Args:
            cx (int): Camera x-coordinate (pixels).
            cy (int): Camera y-coordinate (pixels).

        Returns:
            tuple[float, float]: (screen_x, screen_y) final smoothed coordinates.
        """
        raw_x, raw_y = self.map_to_screen(cx, cy)
        return self.smooth(raw_x, raw_y)
