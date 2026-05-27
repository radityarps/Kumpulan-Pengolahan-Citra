from __future__ import annotations

import math
import time
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

from .app import RuntimePlan
from .config import ExperimentalConfig


BaselineAction = Literal["idle", "move", "click_ready", "click"]


@dataclass(frozen=True)
class BaselineGestureResult:
    """Pure gesture decision for the frozen video baseline."""

    action: BaselineAction
    reason: str


@dataclass(frozen=True)
class BaselineRunMetadata:
    """Metadata exposed for logs/reports without starting the camera loop."""

    condition: str
    backend: str
    gesture_profile: str
    smoothing_strategy: str
    debounce_enabled: bool
    calibration_enabled: bool
    tutorial_behavior: str = "index_move_index_middle_pinch_click"
    compatibility_fixes: tuple[str, ...] = (
        "named_mediapipe_hands_arguments",
        "camera_read_guard",
        "no_hand_guard",
        "safe_real_mouse_opt_in",
    )


def build_baseline_metadata(config: ExperimentalConfig, plan: RuntimePlan) -> BaselineRunMetadata:
    condition = config.get_condition(plan.condition)
    return BaselineRunMetadata(
        condition=plan.condition,
        backend=condition.backend,
        gesture_profile=condition.gesture_profile,
        smoothing_strategy=condition.smoothing_strategy,
        debounce_enabled=condition.debounce_enabled,
        calibration_enabled=condition.calibration_enabled,
    )


def classify_baseline_gesture(
    fingers: list[int] | tuple[int, ...],
    pinch_distance: float | None = None,
    click_threshold_px: int = 40,
) -> BaselineGestureResult:
    """Return the tutorial baseline action from finger state and pinch distance.

    The frozen baseline intentionally supports only the video tutorial gestures:
    index-only movement and index+middle pinch left-click.
    """

    if len(fingers) < 3:
        return BaselineGestureResult("idle", "not_enough_finger_state")

    index_up = fingers[1] == 1
    middle_up = fingers[2] == 1

    if index_up and not middle_up:
        return BaselineGestureResult("move", "index_only")

    if index_up and middle_up:
        if pinch_distance is not None and pinch_distance < click_threshold_px:
            return BaselineGestureResult("click", "index_middle_pinch_below_threshold")
        return BaselineGestureResult("click_ready", "index_middle_up")

    return BaselineGestureResult("idle", "unsupported_tutorial_gesture")


class FrozenVideoHandDetector:
    """MediaPipe Solutions hand detector compatible with the tutorial baseline."""

    tip_ids = [4, 8, 12, 16, 20]

    def __init__(self, max_hands: int = 1, detection_confidence: float = 0.5, tracking_confidence: float = 0.5):
        self.cv2 = import_module("cv2")
        self.mp_hands = _import_mediapipe_hands()
        self.mp_draw = _import_mediapipe_drawing_utils()
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.results: Any | None = None
        self.lm_list: list[list[int]] = []

    def find_hands(self, image, draw: bool = True):
        image_rgb = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)
        multi_hand_landmarks = getattr(self.results, "multi_hand_landmarks", None)

        if multi_hand_landmarks:
            for hand_landmarks in multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
        return image

    def find_position(self, image, hand_no: int = 0, draw: bool = True):
        x_list: list[int] = []
        y_list: list[int] = []
        bbox: tuple[int, int, int, int] | tuple[()] = ()
        self.lm_list = []

        multi_hand_landmarks = getattr(self.results, "multi_hand_landmarks", None)
        if not multi_hand_landmarks:
            return self.lm_list, bbox

        if hand_no >= len(multi_hand_landmarks):
            return self.lm_list, bbox

        hand = multi_hand_landmarks[hand_no]
        height, width, _ = image.shape
        for landmark_id, landmark in enumerate(hand.landmark):
            cx, cy = int(landmark.x * width), int(landmark.y * height)
            x_list.append(cx)
            y_list.append(cy)
            self.lm_list.append([landmark_id, cx, cy])
            if draw:
                self.cv2.circle(image, (cx, cy), 5, (255, 0, 255), self.cv2.FILLED)

        xmin, xmax = min(x_list), max(x_list)
        ymin, ymax = min(y_list), max(y_list)
        bbox = (xmin, ymin, xmax, ymax)
        if draw:
            self.cv2.rectangle(image, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)
        return self.lm_list, bbox

    def fingers_up(self) -> list[int]:
        if len(self.lm_list) <= self.tip_ids[-1]:
            return [0, 0, 0, 0, 0]

        fingers: list[int] = []
        fingers.append(1 if self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1] else 0)
        for finger_id in range(1, 5):
            tip = self.tip_ids[finger_id]
            fingers.append(1 if self.lm_list[tip][2] < self.lm_list[tip - 2][2] else 0)
        return fingers

    def find_distance(self, p1: int, p2: int, image, draw: bool = True, radius: int = 15, thickness: int = 3):
        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            self.cv2.line(image, (x1, y1), (x2, y2), (255, 0, 255), thickness)
            self.cv2.circle(image, (x1, y1), radius, (255, 0, 255), self.cv2.FILLED)
            self.cv2.circle(image, (x2, y2), radius, (255, 0, 255), self.cv2.FILLED)
            self.cv2.circle(image, (cx, cy), radius, (0, 0, 255), self.cv2.FILLED)

        return math.hypot(x2 - x1, y2 - y1), image, [x1, y1, x2, y2, cx, cy]


def run_frozen_video_baseline(config: ExperimentalConfig, plan: RuntimePlan) -> int:
    """Run the compatibility-fixed frozen video baseline demo."""

    cv2 = import_module("cv2")
    np = import_module("numpy")
    autopy = import_module("autopy")

    detector = FrozenVideoHandDetector(max_hands=1)
    cap = cv2.VideoCapture(config.backend.camera_index)
    cap.set(3, config.backend.camera_width)
    cap.set(4, config.backend.camera_height)

    w_screen, h_screen = autopy.screen.size()
    frame_reduction = 100
    smoothening = 7
    previous_time = 0.0
    previous_x = previous_y = 0.0

    print("Running frozen video baseline. Press 'q' in the camera window to exit.")
    while True:
        success, image = cap.read()
        if not success:
            print("Camera frame could not be read. Check your camera index.")
            break

        image = detector.find_hands(image)
        lm_list, _bbox = detector.find_position(image)
        cv2.rectangle(
            image,
            (frame_reduction, frame_reduction),
            (config.backend.camera_width - frame_reduction, config.backend.camera_height - frame_reduction),
            (255, 0, 255),
            2,
        )

        if lm_list:
            x1, y1 = lm_list[8][1:]
            fingers = detector.fingers_up()
            gesture = classify_baseline_gesture(fingers, click_threshold_px=config.gesture.click_threshold_px)

            if gesture.action == "move":
                x3 = np.interp(x1, (frame_reduction, config.backend.camera_width - frame_reduction), (0, w_screen))
                y3 = np.interp(y1, (frame_reduction, config.backend.camera_height - frame_reduction), (0, h_screen))
                current_x = previous_x + (x3 - previous_x) / smoothening
                current_y = previous_y + (y3 - previous_y) / smoothening
                autopy.mouse.move(w_screen - current_x, current_y)
                cv2.circle(image, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                previous_x, previous_y = current_x, current_y

            elif gesture.action == "click_ready":
                length, image, line_info = detector.find_distance(8, 12, image)
                gesture = classify_baseline_gesture(
                    fingers,
                    pinch_distance=length,
                    click_threshold_px=config.gesture.click_threshold_px,
                )
                if gesture.action == "click":
                    cv2.circle(image, (line_info[4], line_info[5]), 15, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()

        current_time = time.time()
        fps = 0 if previous_time == 0 else 1 / (current_time - previous_time)
        previous_time = current_time
        cv2.putText(image, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        cv2.imshow("Frozen Video Baseline", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return 0


def _import_mediapipe_hands():
    try:
        mediapipe = import_module("mediapipe")
        return mediapipe.solutions.hands
    except (AttributeError, ModuleNotFoundError):
        return import_module("mediapipe.python.solutions.hands")


def _import_mediapipe_drawing_utils():
    try:
        mediapipe = import_module("mediapipe")
        return mediapipe.solutions.drawing_utils
    except (AttributeError, ModuleNotFoundError):
        return import_module("mediapipe.python.solutions.drawing_utils")
