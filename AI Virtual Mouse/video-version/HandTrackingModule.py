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
        Detect hands in a BGR frame and optionally draw landmarks.

        Converts BGR to contiguous RGB (Tasks API requirement), runs
        HandLandmarker.detect(), and draws landmark connections if draw=True.

        Args:
            img (numpy.ndarray): BGR image from webcam (shape: H×W×3).
            draw (bool): If True, overlay hand skeleton on the image.

        Returns:
            numpy.ndarray: Input image with or without landmark overlay.

        Side effects:
            Sets self.detection_result for later use by findPosition().
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
        Extract landmark pixel coordinates and bounding box.

        Converts MediaPipe normalized coordinates (0.0–1.0) to pixel
        coordinates using image dimensions. Computes bounding box that
        encloses all 21 landmarks with a 20px margin.

        Args:
            img (numpy.ndarray): BGR image (used for dimensions and drawing).
            hand_no (int): Index of the hand to extract (0 = first hand).
                Only used when max_hands > 1.
            draw (bool): If True, draw landmark circles and bounding box.

        Returns:
            tuple:
                - lmList (list): [[id, cx, cy], ...] for all 21 landmarks.
                  id: 0–20 (0=wrist, 4=thumb tip, 8=index tip, etc.).
                  cx, cy: pixel coordinates.
                - bbox (tuple): (xmin, ymin, xmax, ymax) or (0,0,0,0) if
                  no hand detected.

        Side effects:
            Sets self.lmList for use by fingersUp() and findDistance().
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
        Determine which fingers are extended (pointing up).

        Detection algorithm (matches tutorial exactly):
        - Thumb: Compare x-coordinates of tip (landmark 4) and IP joint
          (landmark 3). If tip.x > IP.x, thumb is "up". This only works
          reliably for the right hand facing the camera.
        - Other 4 fingers: Compare y-coordinates of tip and PIP joint
          (landmark 2 levels below tip). If tip.y < PIP.y, finger is "up"
          (because y=0 is at the top of the image).

        Requires findPosition() to be called first (populates self.lmList).

        Returns:
            list[int]: [thumb, index, middle, ring, pinky]
                1 = extended (up), 0 = folded (down).
                Returns [0,0,0,0,0] if no landmarks available.

        Note:
            Thumb detection is handedness-dependent. In gesture pattern
            matching, thumb is typically ignored (None wildcard) to avoid
            this limitation.
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

        Uses math.hypot(dx, dy) for numerical stability. Optionally draws
        a line between the two points and circles at endpoints + midpoint.

        Args:
            p1 (int): Landmark ID of first point (e.g., 8 = index tip).
            p2 (int): Landmark ID of second point (e.g., 12 = middle tip).
            img (numpy.ndarray | None): Image to draw on (can be None).
            draw (bool): If True and img is provided, draw line and circles.
            r (int): Radius of endpoint circles in pixels.
            t (int): Thickness of the connecting line in pixels.

        Returns:
            tuple:
                - length (float): Euclidean distance in pixels.
                - img (numpy.ndarray): Image with or without overlay.
                - line_info (list): [x1, y1, x2, y2, cx, cy] midpoint info.
                  Returns all zeros if no landmarks available.
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
        """
        Draw hand skeleton (connections between landmarks).

        Replaces the deprecated mp.solutions.drawing_utils.draw_landmarks().
        Draws 21 cyan lines between connected landmarks using the standard
        MediaPipe HAND_CONNECTIONS topology.

        Args:
            img (numpy.ndarray): BGR image to draw on (modified in-place).
            hand_landmarks (list): NormalizedLandmark objects from
                HandLandmarkerResult. Each has .x and .y in [0.0, 1.0].
        """
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
