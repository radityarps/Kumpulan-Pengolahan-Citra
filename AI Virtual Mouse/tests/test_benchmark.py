"""
AI Virtual Mouse — Fase 6 Performance Benchmark
Measures FPS over 10 seconds using a mock controller (no mouse movement).
Reports min, max, mean, median, and 95th percentile FPS.

Run: python tests/test_benchmark.py
"""

import statistics
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


class BenchmarkController:
    """Does nothing — records calls for verification only."""

    def execute(self, action, **kwargs):
        pass

    def cleanup(self):
        pass


def run_benchmark(duration=10.0):
    """Run pipeline for `duration` seconds and return FPS statistics."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("FAIL: Cannot open webcam")
        return None

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
    controller = BenchmarkController()

    fps_values = []
    start_time = time.time()
    prev_time = start_time
    frame_count = 0

    print(f"Benchmarking for {duration}s...")

    while time.time() - start_time < duration:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.findHands(img, draw=True)
        lmList, _bbox = detector.findPosition(img, draw=False)

        if lmList:
            fingers = detector.fingersUp()

            def _get_distance(p1, p2, draw_flag=False):
                return detector.findDistance(p1, p2, draw=draw_flag)

            mode, action = classifier.classify(fingers, lmList, _get_distance)

            if mode in ("Move", "Drag") and len(lmList) > 8:
                ix, iy = lmList[8][1], lmList[8][2]
                sx, sy = mapper.process(ix, iy)
                controller.execute("move", screen_x=sx, screen_y=sy)

        # FPS measurement
        curr_time = time.time()
        elapsed = curr_time - prev_time
        if elapsed > 0:
            fps_values.append(1.0 / elapsed)
        prev_time = curr_time
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not fps_values:
        print("FAIL: No frames captured")
        return None

    total_time = time.time() - start_time
    mean_fps = sum(fps_values) / len(fps_values)
    min_fps = min(fps_values)
    max_fps = max(fps_values)
    median_fps = statistics.median(fps_values)
    p95_fps = sorted(fps_values)[int(len(fps_values) * 0.95)]

    print("\n" + "=" * 50)
    print("  PERFORMANCE BENCHMARK RESULTS")
    print("=" * 50)
    print(f"  Duration:         {total_time:.1f}s")
    print(f"  Frames captured:  {frame_count}")
    print(f"  FPS samples:      {len(fps_values)}")
    print(f"  Mean FPS:         {mean_fps:.1f}")
    print(f"  Median FPS:       {median_fps:.1f}")
    print(f"  Min FPS:          {min_fps:.1f}")
    print(f"  Max FPS:          {max_fps:.1f}")
    print(f"  95th %ile FPS:    {p95_fps:.1f}")
    print(f"{'=' * 50}")

    return {
        "total_time": total_time,
        "frame_count": frame_count,
        "mean_fps": mean_fps,
        "median_fps": median_fps,
        "min_fps": min_fps,
        "max_fps": max_fps,
        "p95_fps": p95_fps,
    }


if __name__ == "__main__":
    run_benchmark(10.0)
