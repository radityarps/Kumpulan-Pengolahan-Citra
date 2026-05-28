from __future__ import annotations

import math
from dataclasses import dataclass
from importlib import import_module
from typing import Any

import numpy as np

from .config import ExperimentalConfig
from .cursor_mapping import Point
from .tasks_backend import resolve_model_path


@dataclass(frozen=True)
class HandTrackingResult:
    landmarks: list[Point] | None = None
    fingers_up: list[int] | None = None
    pinch_distance_px: float | None = None
    index_middle_vertical_delta_px: float | None = None
    success: bool = False
    backend_used: str = "unknown"
    fallback_reason: str | None = None


class HandTracker:
    """Unified hand tracker: Tasks primary, Solutions fallback."""

    def __init__(
        self,
        config: ExperimentalConfig,
        prefer_tasks: bool = True,
    ):
        self.config = config
        self.prefer_tasks = prefer_tasks
        self._tasks_backend: Any | None = None
        self._solutions_backend: Any | None = None
        self._drawing_utils: Any | None = None
        self._backend_used = "unknown"
        self._fallback_reason: str | None = None
        self._setup_backend()

    def _setup_backend(self) -> None:
        if self.prefer_tasks:
            try:
                self._setup_tasks_backend()
                self._backend_used = "mediapipe_tasks"
                return
            except Exception as exc:
                self._fallback_reason = str(exc)
                print(f"[WARN] Tasks backend failed ({exc}).")
                try:
                    self._setup_solutions_backend()
                except Exception as fallback_exc:
                    raise RuntimeError(
                        "MediaPipe Tasks backend could not start and MediaPipe "
                        "Solutions fallback is unavailable in this environment. "
                        "Run `PYTHONPATH=src python -m ai_virtual_mouse_experimental "
                        "--download-model`, then retry improved demo. "
                        f"Tasks error: {exc}. Fallback error: {fallback_exc}"
                    ) from fallback_exc
                print("[WARN] Falling back to MediaPipe Solutions.")
                self._backend_used = "mediapipe_solutions"
                return
        self._setup_solutions_backend()
        self._backend_used = "mediapipe_solutions"

    def _setup_tasks_backend(self) -> None:
        mp = import_module("mediapipe")
        vision = mp.tasks.vision
        base_options = mp.tasks.BaseOptions
        model_path = resolve_model_path(self.config.backend.model_path)
        if not model_path.exists():
            raise RuntimeError(
                f"HandLandmarker model not found: {model_path}. "
                "Run `PYTHONPATH=src python -m ai_virtual_mouse_experimental "
                "--download-model` before improved demo."
            )
        opts = vision.HandLandmarkerOptions(
            base_options=base_options(model_asset_path=str(model_path)),
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._tasks_backend = vision.HandLandmarker.create_from_options(opts)
        print(f"[INFO] MediaPipe Tasks backend initialized: {model_path}")

    def _setup_solutions_backend(self) -> None:
        hands = _import_mediapipe_hands()
        self._solutions_backend = hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._drawing_utils = _import_mediapipe_drawing_utils()
        print("[INFO] MediaPipe Solutions backend initialized")

    def process(self, frame: np.ndarray) -> HandTrackingResult:
        if self._backend_used == "mediapipe_tasks":
            return self._process_tasks(frame)
        return self._process_solutions(frame)

    def _process_tasks(self, frame: np.ndarray) -> HandTrackingResult:
        import cv2

        mp = import_module("mediapipe")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        assert self._tasks_backend is not None
        result = self._tasks_backend.detect(image)
        if not result.hand_landmarks:
            return HandTrackingResult(
                success=False,
                backend_used=self._backend_used,
                fallback_reason=self._fallback_reason,
            )
        landmarks = result.hand_landmarks[0]
        h, w = frame.shape[:2]
        points = [Point(lm.x * w, lm.y * h) for lm in landmarks]
        fingers = _fingers_up(landmarks)
        pinch = _index_middle_distance(points)
        delta = points[8].y - points[12].y if len(points) > 12 else 0.0
        return HandTrackingResult(
            landmarks=points,
            fingers_up=fingers,
            pinch_distance_px=pinch,
            index_middle_vertical_delta_px=delta,
            success=True,
            backend_used=self._backend_used,
        )

    def _process_solutions(self, frame: np.ndarray) -> HandTrackingResult:
        import cv2

        assert self._solutions_backend is not None
        results = self._solutions_backend.process(
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        if not results.multi_hand_landmarks:
            return HandTrackingResult(
                success=False,
                backend_used=self._backend_used,
                fallback_reason=self._fallback_reason,
            )
        h, w = frame.shape[:2]
        hand_landmarks = results.multi_hand_landmarks[0]
        points = [Point(lm.x * w, lm.y * h) for lm in hand_landmarks.landmark]
        fingers = _fingers_up_solutions(hand_landmarks)
        pinch = _index_middle_distance(points)
        delta = points[8].y - points[12].y if len(points) > 12 else 0.0
        return HandTrackingResult(
            landmarks=points,
            fingers_up=fingers,
            pinch_distance_px=pinch,
            index_middle_vertical_delta_px=delta,
            success=True,
            backend_used=self._backend_used,
        )

    def draw_landmarks(
        self, image: np.ndarray, result: HandTrackingResult
    ) -> np.ndarray:
        if not result.success or result.landmarks is None:
            return image
        if self._backend_used == "mediapipe_tasks":
            return self._draw_tasks_landmarks(image, result)
        return self._draw_solutions_landmarks(image, result)

    def _draw_tasks_landmarks(
        self, image: np.ndarray, result: HandTrackingResult
    ) -> np.ndarray:
        import cv2

        assert result.landmarks is not None
        for point in result.landmarks:
            cv2.circle(image, (int(point.x), int(point.y)), 3, (0, 255, 0), -1)
        return image

    def _draw_solutions_landmarks(
        self, image: np.ndarray, result: HandTrackingResult
    ) -> np.ndarray:
        import cv2

        mp_hands = _import_mediapipe_hands()
        h, w = image.shape[:2]
        connections = mp_hands.HAND_CONNECTIONS
        assert result.landmarks is not None
        landmarks = result.landmarks
        for connection in connections:
            start = landmarks[connection[0]]
            end = landmarks[connection[1]]
            cv2.line(
                image,
                (int(start.x), int(start.y)),
                (int(end.x), int(end.y)),
                (0, 255, 0),
                2,
            )
        for point in result.landmarks:
            cv2.circle(image, (int(point.x), int(point.y)), 3, (0, 0, 255), -1)
        return image

    def close(self) -> None:
        if self._tasks_backend is not None:
            self._tasks_backend.close()
        if self._solutions_backend is not None:
            self._solutions_backend.close()


def _index_middle_distance(points: list[Point]) -> float | None:
    if len(points) <= 12:
        return None
    return math.hypot(points[8].x - points[12].x, points[8].y - points[12].y)


def _fingers_up(landmarks) -> list[int]:
    """Return [thumb, index, middle, ring, pinky] extended state from Tasks landmarks."""
    tips = [4, 8, 12, 16, 20]
    # Thumb: compare tip x vs IP joint x
    fingers = [1 if landmarks[tips[0]].x > landmarks[3].x else 0]
    # Other fingers: compare tip y vs PIP joint y (y increases downward)
    for tip, pip in zip(tips[1:], [6, 10, 14, 18], strict=True):
        fingers.append(1 if landmarks[tip].y < landmarks[pip].y else 0)
    return fingers


def _fingers_up_solutions(hand_landmarks) -> list[int]:
    """Return [thumb, index, middle, ring, pinky] extended state from Solutions landmarks."""
    lm = hand_landmarks.landmark
    tips = [4, 8, 12, 16, 20]
    fingers = [1 if lm[tips[0]].x > lm[3].x else 0]
    for tip, pip in zip(tips[1:], [6, 10, 14, 18], strict=True):
        fingers.append(1 if lm[tip].y < lm[pip].y else 0)
    return fingers


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
