"""
Hand Tracking Module — Video Version
Wraps MediaPipe Tasks API (HandLandmarker) to replicate the tutorial's interface.
Public API is identical to the video's HandTrackingModule — callers see no difference.

Differences from the video:
- Tasks API instead of legacy Solutions API (Solutions API removed from mediapipe>=0.10.30)
- Custom landmark drawing instead of mp.solutions.drawing_utils
- Uses external hand_landmarker.task model file

Behavior (gesture logic, thumb detection, return values): EXACTLY matches the video.
"""

import math
import os

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

# Model file path (relative to project root)
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src",
    "hand_landmarker.task",
)

# Hand connections for custom drawing (same as mp.solutions.hands.HAND_CONNECTIONS)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17),
]


class HandDetector:
    """Wrapper for MediaPipe Hands — same API as the video's HandTrackingModule."""

    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mode = mode                # unused; kept for API compatibility
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        self.tip_ids = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky

        # Tasks API: HandLandmarker
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_tracking_confidence=track_con,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

        # Internal state (matches video's self.results)
        self.detection_result = None
        self.lmList = []

    def findHands(self, img, draw=True):
        """
        Detect hands in a BGR frame. Draw landmarks if requested.
        Same signature and behavior as the video's HandTrackingModule.
        """
        # Convert BGR to RGB with contiguous array (Tasks API requirement)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb = np.ascontiguousarray(img_rgb, dtype=np.uint8)

        # Create MediaPipe Image and run detection
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        self.detection_result = self.landmarker.detect(mp_image)

        # Draw landmarks
        if draw and self.detection_result.hand_landmarks:
            for hand_landmarks in self.detection_result.hand_landmarks:
                self._draw_landmarks(img, hand_landmarks)

        return img

    def findPosition(self, img, hand_no=0, draw=True):
        """
        Extract landmark pixel coords and bounding box.
        Returns (lmList, bbox) — EXACTLY same format as the video.
        lmList: [[id, cx, cy], ...]
        bbox: (xmin, ymin, xmax, ymax) or (0, 0, 0, 0) if no hand
        """
        self.lmList = []
        x_list = []
        y_list = []

        if (
            self.detection_result is None
            or not self.detection_result.hand_landmarks
            or hand_no >= len(self.detection_result.hand_landmarks)
        ):
            return [], (0, 0, 0, 0)

        hand_landmarks = self.detection_result.hand_landmarks[hand_no]
        h, w, _c = img.shape

        for idx, lm in enumerate(hand_landmarks):
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            x_list.append(cx)
            y_list.append(cy)
            self.lmList.append([idx, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        xmin, xmax = min(x_list), max(x_list)
        ymin, ymax = min(y_list), max(y_list)
        bbox = xmin, ymin, xmax, ymax

        if draw:
            cv2.rectangle(
                img,
                (xmin - 20, ymin - 20),
                (xmax + 20, ymax + 20),
                (0, 255, 0),
                2,
            )

        return self.lmList, bbox

    def fingersUp(self):
        """
        Return binary vector [thumb, index, middle, ring, pinky].
        Thumb: x-coordinate comparison (tip[4] vs IP[3]) — handedness-dependent.
        Other fingers: y-coordinate comparison (tip vs PIP).

        EXACTLY matches the video's algorithm.
        """
        fingers = []

        if len(self.lmList) == 0:
            return [0, 0, 0, 0, 0]

        # Thumb: x-coordinate comparison
        # Works for right hand with palm facing camera (mirrored image)
        if self.lmList[self.tip_ids[0]][1] > self.lmList[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Four fingers: tip y < PIP y → extended (finger pointing up)
        for tip_id in self.tip_ids[1:]:
            if self.lmList[tip_id][2] < self.lmList[tip_id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def findDistance(self, p1, p2, img=None, draw=True, r=15, t=3):
        """
        Compute Euclidean distance between two landmarks.
        Returns (length, img, [x1, y1, x2, y2, cx, cy]) — same as video.
        """
        if len(self.lmList) == 0:
            return 0, img, [0, 0, 0, 0, 0, 0]

        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw and img is not None:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

    def _draw_landmarks(self, img, hand_landmarks):
        """Draw landmark connections — replaces mp.solutions.drawing_utils."""
        h, w, _c = img.shape
        points = {}
        for i, lm in enumerate(hand_landmarks):
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            points[i] = (cx, cy)

        # Draw connections (cyan lines)
        for start_idx, end_idx in HAND_CONNECTIONS:
            if start_idx in points and end_idx in points:
                cv2.line(img, points[start_idx], points[end_idx], (255, 255, 0), 2)
