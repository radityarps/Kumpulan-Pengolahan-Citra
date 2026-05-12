"""
AI Virtual Mouse — Smoke Test
Runs a short real-world test without moving the physical mouse.
Uses a mock controller to log actions instead of executing them.
"""

import time

import cv2

from src.config import (
    CLICK_THRESHOLD_PX,
    DEBOUNCE_TIME_MS,
    DRAG_THRESHOLD_PX,
    FRAME_HEIGHT,
    FRAME_REDUCTION,
    FRAME_WIDTH,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    SCROLL_DEAD_ZONE_PX,
    SCROLL_SENSITIVITY,
    SMOOTHING_FACTOR,
)
from src.coordinate_mapper import CoordinateMapper
from src.gesture_classifier import GestureClassifier
from src.hand_tracking_module import HandDetector


class MockController:
    """Simulates mouse control by printing actions."""

    def execute(self, action, **kwargs):
        print(f"  [Action] {action}, args={kwargs}")

    def cleanup(self):
        pass


def main():
    print("=" * 50)
    print("  AI Virtual Mouse — Smoke Test")
    print("=" * 50)

    # 1. Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap.isOpened():
        print("FAIL: Cannot open webcam")
        return
    print("OK: Webcam opened")

    # 2. Instantiate modules
    try:
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
        )
        mapper = CoordinateMapper(
            frame_width=FRAME_WIDTH,
            frame_height=FRAME_HEIGHT,
            frame_reduction=FRAME_REDUCTION,
            smoothing_factor=SMOOTHING_FACTOR,
        )
        controller = MockController()
    except Exception as e:
        print(f"FAIL: Instantiation error: {e}")
        cap.release()
        return

    print("OK: All modules instantiated")

    # 3. Run loop for 5 seconds
    start_time = time.time()
    duration = 5.0
    frame_count = 0
    detection_count = 0

    print(f"Running for {duration}s...")

    while time.time() - start_time < duration:
        success, img = cap.read()
        if not success:
            print("ERROR: Failed to read frame")
            break

        img = cv2.flip(img, 1)
        img = detector.findHands(img, draw=True)
        lmList, bbox = detector.findPosition(img, hand_no=0, draw=False)

        if lmList:
            detection_count += 1
            if detection_count == 1:
                print(f"  First detection: {len(lmList)} landmarks")
            fingers = detector.fingersUp()
            if detection_count <= 3:
                print(f"  Fingers: {fingers}")

            def _get_distance(p1, p2, draw_flag=False):
                return detector.findDistance(p1, p2, draw=draw_flag)

            mode, action = classifier.classify(fingers, lmList, _get_distance)

            if detection_count <= 3:
                print(f"  Mode: {mode}, Action: {action}")

            if lmList and mode in ("Move", "Drag") and len(lmList) > 8:
                ix, iy = lmList[8][1], lmList[8][2]
                smooth_x, smooth_y = mapper.process(ix, iy)
                controller.execute("move", screen_x=smooth_x, screen_y=smooth_y)

            if action == "click":
                controller.execute("click")
            elif action == "right_click":
                controller.execute("right_click")
            elif action == "drag_start":
                controller.execute("drag_start")
            elif action == "drag_end":
                controller.execute("drag_end")
            elif isinstance(action, tuple) and action[0] == "scroll":
                controller.execute(("scroll", action[1]))
        else:
            classifier.reset()
            mapper.reset_smoothing()

        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("  User quit (q pressed)")
            break

    elapsed = time.time() - start_time
    print(f"OK: Processed {frame_count} frames in {elapsed:.1f}s")
    print(f"     Detections: {detection_count} frames")
    if frame_count > 0:
        print(f"     Average FPS: {frame_count / elapsed:.1f}")

    # 4. Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
