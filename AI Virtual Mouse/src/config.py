"""
AI Virtual Mouse — Configuration Constants
All magic numbers, thresholds, and tunable parameters in one place.
Modify values here to tune system behavior without touching module code.
"""

import cv2

# =============================================================================
# Camera Settings
# =============================================================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAMERA_ID = 0  # Default webcam; change to 1 for external camera

# =============================================================================
# MediaPipe Hand Detection
# =============================================================================
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 1
STATIC_IMAGE_MODE = False  # False = tracking mode (faster, smoother)
HAND_LOST_GRACE_FRAMES = 4  # Keep last state for a few missed frames

# =============================================================================
# Gesture Classification Thresholds
# =============================================================================
# Gesture style profile
GESTURE_STYLE = "legacy"

# Optional advanced controls (GfG-style extensions)
ENABLE_VOLUME_CONTROL = False
ENABLE_BRIGHTNESS_CONTROL = False

CLICK_THRESHOLD_PX = 40  # Max distance between index(8) and middle(12) tips for click
DRAG_THRESHOLD_PX = 30  # Max distance between thumb(4) and index(8) tips for drag
DEBOUNCE_TIME_MS = 300  # Mode must be stable this long before activating
SCROLL_SENSITIVITY = 2  # Higher = less sensitive scrolling
SCROLL_DEAD_ZONE_PX = 5  # Minimum y-delta to trigger scroll
THUMB_SENSITIVITY = 1.80  # 1.0 = normal. Higher = stricter thumb detection (easier to fold close). Range: 0.5-2.0
PINCH_CONTROL_DEAD_ZONE = 6  # Minimum index movement to trigger brightness/volume
PINCH_CONTROL_SCALE = 2  # Lower = stronger brightness/volume effect

# =============================================================================
# Coordinate Mapping & Smoothing
# =============================================================================
FRAME_REDUCTION = 100  # Dead-zone margin at frame edges (pixels)
SMOOTHING_FACTOR = 5.0  # Higher = smoother but more lag; grid search optimal = 5
CLICK_DELAY = 0.1  # Seconds to sleep after click (prevents double-click)

# =============================================================================
# UI / Display
# =============================================================================
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_PLAIN = cv2.FONT_HERSHEY_PLAIN
FPS_POS = (20, 50)
MODE_POS = (20, 100)
LANDMARK_VISIBLE_DEFAULT = True
DEBUG_FINGERS = True  # Show finger state vector and raw mode on screen
DEBUG_ACTION = True  # Show latest action trigger on screen

# =============================================================================
# Colors (BGR format for OpenCV)
# =============================================================================
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_ORANGE = (0, 165, 255)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_PURPLE = (255, 0, 255)
COLOR_CYAN = (255, 255, 0)

# Map gesture mode to display color
MODE_COLORS = {
    "None": COLOR_WHITE,
    "Move": COLOR_GREEN,
    "Click": COLOR_BLUE,
    "RightClick": COLOR_ORANGE,
    "Drag": COLOR_RED,
    "Scroll": COLOR_YELLOW,
}
