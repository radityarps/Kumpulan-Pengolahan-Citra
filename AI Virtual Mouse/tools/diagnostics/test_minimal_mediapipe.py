"""
Absolute minimal MediaPipe detection test - debug the actual issue
"""
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)
import os

# Model path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
model_path = os.path.join(PROJECT_ROOT, "src", "hand_landmarker.task")

print("Model file exists:", os.path.exists(model_path))
print("Model path:", model_path)

# Create detector with very low confidence
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.5,  # Very low
    min_tracking_confidence=0.5,
)
detector = HandLandmarker.create_from_options(options)

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\nTesting 10 frames...")
for frame_idx in range(10):
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    
    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    
    # Create image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    
    # Detect
    result = detector.detect(mp_image)
    
    print("Frame {}: hand_landmarks={}, hands={}".format(
        frame_idx + 1,
        result.hand_landmarks is not None,
        len(result.hand_landmarks) if result.hand_landmarks else 0
    ))
    
    if result.hand_landmarks and len(result.hand_landmarks) > 0:
        print("  Found {} landmarks in first hand".format(len(result.hand_landmarks[0])))

cap.release()
print("\nTest complete")
