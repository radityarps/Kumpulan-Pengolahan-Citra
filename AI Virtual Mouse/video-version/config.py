"""
Configuration — Video Version

All tunable constants in one place. Gesture mapping matches the
main project (practical_no_thumb profile). Implementation style
stays simple — no hysteresis, no debounce, no hold-time gating.

To tune: change the value here and restart the program.
No need to edit any other file.

Gesture reference:
    Move:        [*,1,0,0,0]  index up
    Left Click:  [*,1,1,0,0]  index+middle pinch < LEFT_CLICK_PINCH_PX
    Right Click: [*,1,1,1,0]  index+ring pinch < RIGHT_CLICK_PINCH_PX
    Drag:        [*,0,0,0,0]  fist, anchor-based
    Scroll:      [*,1,1,1,1]  camera center boundary

* = thumb ignored via None wildcard.
"""

# =============================================================================
# Camera
# =============================================================================
# Width and height of the webcam capture frame.
# Higher = more precision but slower processing.
# Must match the webcam's supported resolutions.
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Webcam device ID. 0 = built-in camera, 1 = first external USB camera.
# Change if the wrong camera is selected.
CAMERA_ID = 0

# =============================================================================
# MediaPipe Hand Detection
# =============================================================================
# Minimum confidence (0.0–1.0) for MediaPipe to consider a detection valid.
# Lower = more detections but more false positives (objects mistaken for hands).
# Higher = fewer false positives but may miss hands in poor lighting.
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# Maximum number of hands to detect simultaneously.
# 1 = single hand (lighter, recommended for mouse control).
# 2 = both hands (heavier, useful for two-handed gestures).
MAX_NUM_HANDS = 1

# =============================================================================
# Coordinate Mapping
# =============================================================================
# Dead-zone margin at each edge of the camera frame (pixels).
# Hand movement within this margin won't move the cursor.
# Prevents cursor from getting stuck at screen edges.
# Larger value = more comfortable but less screen coverage.
FRAME_REDUCTION = 100

# Exponential Moving Average smoothing factor.
# Higher = smoother cursor movement but more input lag.
# Lower = more responsive but jittery.
#   SMOOTHING=1   → no smoothing (raw input, very jittery)
#   SMOOTHING=5   → light smoothing
#   SMOOTHING=7   → moderate smoothing (default, good balance)
#   SMOOTHING=10  → heavy smoothing (laggy but stable)
SMOOTHING = 7

# =============================================================================
# Gesture Thresholds
# =============================================================================
# Maximum distance (pixels) between index and middle fingertips
# to trigger a left click. Measured as Euclidean distance via findDistance().
# Lower = must pinch tighter to click.
LEFT_CLICK_PINCH_PX = 28

# Maximum distance (pixels) between index and ring fingertips
# to trigger a right click. Larger than left click threshold
# because index-ring pinch is physically wider.
RIGHT_CLICK_PINCH_PX = 34

# Not used in this simple version.
# In the main project, this gates whether fingers are "folded enough"
# for the fist gesture to count as Drag.
DRAG_THRESHOLD_PX = 30

# =============================================================================
# Scroll
# =============================================================================
# Half-height of the no-scroll zone around the camera center line (pixels).
# Hand within ±35px of center = no scroll.
# Hand above center+35px = scroll up.
# Hand below center-35px = scroll down.
SCROLL_CENTER_DEAD_ZONE_PX = 35

# Number of scroll "steps" per trigger. Each step = 1 notch of mouse wheel.
# Higher = faster scrolling.
SCROLL_STEP_AMOUNT = 2

# Minimum time between consecutive scroll actions (milliseconds).
# Prevents hyperspeed scrolling when hand is held in the scroll zone.
# Lower = more responsive but may scroll too fast.
SCROLL_REPEAT_MS = 120
