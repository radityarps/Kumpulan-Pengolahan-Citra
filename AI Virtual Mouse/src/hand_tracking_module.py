"""
AI Virtual Mouse — Hand Tracking Module
Wraps MediaPipe Tasks Vision HandLandmarker for detection, landmark extraction,
and finger state analysis.

Uses MediaPipe Tasks API (mediapipe>=0.10) instead of the deprecated solutions API.
Model file (hand_landmarker.task) expected in same directory as this module.

Provides:
  - findHands(): detect hands in a BGR frame
  - findPosition(): extract 21 landmark pixel coordinates + bounding box
  - fingersUp(): determine which fingers are extended (binary vector)
  - findDistance(): Euclidean distance between two landmarks
"""

import math
import os
import time

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

from src.config import (
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    COLOR_PURPLE,
    COLOR_GREEN,
    COLOR_CYAN,
    THUMB_SENSITIVITY,
)

# Path to the hand landmarker model file (downloaded separately)
_MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH = os.path.join(_MODEL_DIR, "hand_landmarker.task")

# Hand connections for drawing (MediaPipe HAND_CONNECTIONS)
_HAND_CONNECTIONS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (5, 9),
    (9, 13),
    (13, 17),
]


class HandDetector:
    """
    Wrapper for MediaPipe HandLandmarker (Tasks API).
    """

    def __init__(
        self,
        mode=False,  # Unused; kept for interface compatibility
        max_hands=MAX_NUM_HANDS,
        detection_con=MIN_DETECTION_CONFIDENCE,
        track_con=MIN_TRACKING_CONFIDENCE,
    ):
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # Configure HandLandmarker
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_tracking_confidence=track_con,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

        # Landmark indices for finger tips
        self.tip_ids = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky

        # Internal state
        self.detection_result = None
        self.lmList = []  # [[id, cx, cy], ...]

    def findHands(self, img, draw=True):
        """
        Detect hands in a BGR image.

        Args:
            img (numpy.ndarray): BGR image from webcam.
            draw (bool): If True, draw landmark connections on the image.

        Returns:
            numpy.ndarray: Image with or without landmark overlay.
        """
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Ensure proper format - copy if needed
        img_rgb = np.ascontiguousarray(img_rgb, dtype=np.uint8)

        # Create MediaPipe Image from numpy array
        # Using SRGB format which is standard for uint8 RGB images
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=img_rgb,
        )

        # Detect hands
        self.detection_result = self.landmarker.detect(mp_image)

        # Draw landmarks if requested
        if draw and self.detection_result.hand_landmarks:
            for hand_landmarks in self.detection_result.hand_landmarks:
                self._draw_landmarks(img, hand_landmarks)

        return img

    def findPosition(self, img, hand_no=0, draw=True):
        """
        Extract landmark pixel coordinates and bounding box for a specific hand.

        Args:
            img (numpy.ndarray): BGR image (for dimension reference and drawing).
            hand_no (int): Index of hand (0 when max_hands=1).
            draw (bool): If True, draw landmark circles on the image.

        Returns:
            tuple: (lmList, bbox)
        """
        self.lmList = []

        if (
            self.detection_result is None
            or not self.detection_result.hand_landmarks
            or hand_no >= len(self.detection_result.hand_landmarks)
        ):
            return [], (0, 0, 0, 0)

        h, w, _c = img.shape
        hand_landmarks = self.detection_result.hand_landmarks[hand_no]

        # Convert normalized coordinates to pixel coordinates
        for i, lm in enumerate(hand_landmarks):
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            self.lmList.append([i, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, COLOR_PURPLE, cv2.FILLED)

        # Compute bounding box
        if self.lmList:
            x_list = [pt[1] for pt in self.lmList]
            y_list = [pt[2] for pt in self.lmList]
            bbox = (min(x_list), min(y_list), max(x_list), max(y_list))
        else:
            bbox = (0, 0, 0, 0)

        return self.lmList, bbox

    def fingersUp(self):
        """
        Determine which fingers are extended.

        Returns:
            list[int]: [thumb, index, middle, ring, pinky]
        """
        if len(self.lmList) == 0:
            return [0, 0, 0, 0, 0]

        fingers = []

        # Thumb: Use distance-based detection for better accuracy
        # Landmarks: 2=MCP (base), 4=tip
        # Extended thumb has large distance; folded thumb has small distance
        # Threshold ~35px adjusted by THUMB_SENSITIVITY (1.0 = normal)
        thumb_tip_idx = 4
        thumb_mcp_idx = 2
        
        thumb_tip = self.lmList[thumb_tip_idx]
        thumb_mcp = self.lmList[thumb_mcp_idx]
        
        # Distance from MCP to tip
        thumb_dist = math.sqrt(
            (thumb_tip[1] - thumb_mcp[1]) ** 2 +
            (thumb_tip[2] - thumb_mcp[2]) ** 2
        )
        
        # Threshold: 35px * THUMB_SENSITIVITY
        # Higher THUMB_SENSITIVITY = stricter = easier to fold close
        thumb_threshold = 35.0 * THUMB_SENSITIVITY
        
        if thumb_dist > thumb_threshold:
            fingers.append(1)  # Extended
        else:
            fingers.append(0)  # Folded

        # Other fingers: vertical extension (y-coordinate of tip < PIP joint)
        for tip_id in self.tip_ids[1:]:
            if self.lmList[tip_id][2] < self.lmList[tip_id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def findDistance(self, p1, p2, img=None, draw=True):
        """
        Compute Euclidean distance between two landmarks.

        Args:
            p1 (int): Index of first landmark.
            p2 (int): Index of second landmark.
            img (numpy.ndarray|None): Image to draw on (optional).
            draw (bool): If True and img provided, draw line + midpoint circle.

        Returns:
            tuple: (distance, mid_point, line_info)
        """
        if len(self.lmList) == 0:
            return 0, (0, 0), (0, 0, 0, 0)

        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        distance = math.hypot(x2 - x1, y2 - y1)

        if draw and img is not None:
            cv2.line(img, (x1, y1), (x2, y2), COLOR_PURPLE, 2)
            cv2.circle(img, (cx, cy), 5, COLOR_GREEN, cv2.FILLED)

        return distance, (cx, cy), (x1, y1, x2, y2)

    def _draw_landmarks(self, img, hand_landmarks):
        """
        Draw hand landmark points and connections on the image.

        Args:
            img (numpy.ndarray): BGR image.
            hand_landmarks: NormalizedLandmark list from HandLandmarkerResult.
        """
        h, w, _c = img.shape
        points = {}
        for i, lm in enumerate(hand_landmarks):
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            points[i] = (cx, cy)

        # Draw connections
        for start_idx, end_idx in _HAND_CONNECTIONS:
            if start_idx in points and end_idx in points:
                cv2.line(img, points[start_idx], points[end_idx], COLOR_CYAN, 2)
