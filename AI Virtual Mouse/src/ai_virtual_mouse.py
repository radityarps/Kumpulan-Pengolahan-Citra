"""
AI Virtual Mouse — Main Application
Real-time hand gesture-based cursor control using OpenCV and MediaPipe.

Usage:
    python src/ai_virtual_mouse.py

Controls:
    q — quit
    l — toggle landmark visualization
"""

import os
import sys
import time

# Enable running as `python src/ai_virtual_mouse.py` from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from src.hand_tracking_module import HandDetector
from src.gesture_classifier import GestureClassifier
from src.coordinate_mapper import CoordinateMapper
from src.mouse_controller import MouseController
from src.config import (
    FRAME_WIDTH,
    FRAME_HEIGHT,
    CAMERA_ID,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    CLICK_THRESHOLD_PX,
    DRAG_THRESHOLD_PX,
    DEBOUNCE_TIME_MS,
    GESTURE_STYLE,
    SCROLL_SENSITIVITY,
    SCROLL_DEAD_ZONE_PX,
    FRAME_REDUCTION,
    SMOOTHING_FACTOR,
    CLICK_DELAY,
    LANDMARK_VISIBLE_DEFAULT,
    DEBUG_ACTION,
    DEBUG_FINGERS,
    COLOR_GREEN,
    HAND_LOST_GRACE_FRAMES,
)
from src.utils import put_fps, put_mode_text


def main():
    """Main loop: capture → detect → classify → map → control."""
    # ---- Initialize webcam ----
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam. Check CAMERA_ID in config.py.")
        return

    # ---- Initialize modules ----
    detector = HandDetector(
        max_hands=MAX_NUM_HANDS,
        detection_con=MIN_DETECTION_CONFIDENCE,
        track_con=MIN_TRACKING_CONFIDENCE,
    )
    classifier = GestureClassifier(
        click_threshold=CLICK_THRESHOLD_PX,
        drag_threshold=DRAG_THRESHOLD_PX,
        debounce_ms=DEBOUNCE_TIME_MS,
        scroll_sensitivity=SCROLL_SENSITIVITY,
        scroll_dead_zone=SCROLL_DEAD_ZONE_PX,
        gesture_style=GESTURE_STYLE,
    )
    mapper = CoordinateMapper(
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        frame_reduction=FRAME_REDUCTION,
        smoothing_factor=SMOOTHING_FACTOR,
    )
    controller = MouseController(click_delay=CLICK_DELAY)

    # ---- State ----
    prev_time = time.time()
    show_landmarks = LANDMARK_VISIBLE_DEFAULT
    hand_lost_frames = 0
    last_action_text = "None"

    print("=" * 50)
    print("  AI Virtual Mouse")
    print("  Controls: q=quit, l=toggle landmarks")
    print(f"  Gesture style: {GESTURE_STYLE}")
    print(f"  Screen: {mapper.screen_width}x{mapper.screen_height}")
    print("=" * 50)

    # ---- Main loop ----
    while True:
        # 1. Capture frame
        success, img = cap.read()
        if not success:
            print("[ERROR] Failed to read frame from webcam.")
            break

        # Mirror for natural hand movement
        img = cv2.flip(img, 1)

        # 2. Hand detection
        img = detector.findHands(img, draw=show_landmarks)
        lmList, bbox = detector.findPosition(img, draw=False)

        # 3. Gesture classification
        mode = "None"
        action = None

        if lmList:
            hand_lost_frames = 0
            fingers = detector.fingersUp()

            # Build distance callable bound to the detector
            def _get_distance(p1, p2, draw=False):
                return detector.findDistance(p1, p2, draw=draw)

            mode, action = classifier.classify(fingers, lmList, _get_distance)
            if action is not None:
                last_action_text = str(action)

            # Debug: show finger states and expected patterns on screen
            if DEBUG_FINGERS:
                finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
                move_patterns = tuple(classifier.profile["move_patterns"])
                match_move = any(
                    classifier._match_pattern(fingers, pattern)
                    for pattern in move_patterns
                )
                status = "MATCH!" if match_move else f"need one of {move_patterns}"
                dbg_text = f"Fingers: {fingers}  ({'/'.join(f'{n}={v}' for n, v in zip(finger_names, fingers, strict=False))})"
                cv2.putText(
                    img,
                    dbg_text,
                    (20, 130),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.0,
                    COLOR_GREEN if match_move else (0, 165, 255),
                    1,
                )
                cv2.putText(
                    img,
                    f"Style: {GESTURE_STYLE} | Move: {status} | Mode: {mode}",
                    (20, 155),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.0,
                    COLOR_GREEN if mode == "Move" else (0, 165, 255),
                    1,
                )
        else:
            hand_lost_frames += 1
            if hand_lost_frames >= HAND_LOST_GRACE_FRAMES:
                classifier.reset()
                mapper.reset_smoothing()

        # 4. Coordinate mapping + mouse control
        # Keep smoothing state updated for all detected-hand modes to prevent
        # large cursor jumps when transitioning back to Move/Drag.
        smooth_x, smooth_y = None, None
        if lmList and len(lmList) > 8:
            ix, iy = lmList[8][1], lmList[8][2]
            smooth_x, smooth_y = mapper.process(ix, iy)

        if (
            smooth_x is not None
            and smooth_y is not None
            and mode in ("Move", "Drag")
            and not classifier.is_movement_frozen()
        ):
            # Cursor follows index fingertip (landmark 8) only in movement modes.
            controller.execute("move", screen_x=smooth_x, screen_y=smooth_y)

        if action == "click":
            controller.execute("click")

        if action == "double_click":
            controller.execute("double_click")

        if action == "right_click":
            controller.execute("right_click")

        if action == "drag_start":
            controller.execute("drag_start")

        if action == "drag_end":
            controller.execute("drag_end")

        if isinstance(action, tuple) and action[0] == "scroll":
            _scroll_type, scroll_amount = action
            controller.execute(("scroll", scroll_amount))

        # 5. UI overlay
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time) if prev_time else 0.0
        prev_time = curr_time

        put_fps(img, int(fps))
        put_mode_text(img, mode)

        if DEBUG_ACTION:
            cv2.putText(
                img,
                f"Action: {last_action_text}",
                (20, 180),
                cv2.FONT_HERSHEY_PLAIN,
                1.1,
                COLOR_GREEN,
                1,
            )

        # Optional: show smoothed coordinates in debug
        if lmList and mode != "None" and len(lmList) > 8:
            cv2.putText(
                img,
                f"({lmList[8][1]}, {lmList[8][2]})",
                (20, 150),
                cv2.FONT_HERSHEY_PLAIN,
                1.2,
                COLOR_GREEN,
                1,
            )

        # Display
        cv2.imshow("AI Virtual Mouse", img)

        # 6. Keyboard input (1ms wait for responsiveness)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("l"):
            show_landmarks = not show_landmarks

    # ---- Cleanup ----
    controller.cleanup()
    cap.release()
    cv2.destroyAllWindows()
    print("[AI Virtual Mouse] Shutdown complete.")


if __name__ == "__main__":
    main()
