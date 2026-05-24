"""
Configuration — Video Version
Gesture mapping matches the main project (practical_no_thumb profile).
Implementation style stays simple (no hysteresis, no debounce).
"""

# Camera
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAMERA_ID = 0

# MediaPipe
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 1

# Coordinate mapping
FRAME_REDUCTION = 100        # dead-zone margin at frame edges (px)
SMOOTHING = 7                # exponential smoothing factor

# Gesture thresholds (matching main project values)
LEFT_CLICK_PINCH_PX = 28     # index-middle distance to trigger left click
RIGHT_CLICK_PINCH_PX = 34    # index-ring distance to trigger right click
DRAG_THRESHOLD_PX = 30       # not used in simple version (fist = drag)

# Scroll (camera center boundary — matches main project)
SCROLL_CENTER_DEAD_ZONE_PX = 35  # no-scroll zone around camera center
SCROLL_STEP_AMOUNT = 2           # scroll step per trigger
SCROLL_REPEAT_MS = 120           # minimum interval between scroll triggers
