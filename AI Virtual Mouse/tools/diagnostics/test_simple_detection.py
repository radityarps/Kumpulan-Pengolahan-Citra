"""
Simpler detection test - no unicode characters
"""
import cv2
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.hand_tracking_module import HandDetector
from src.config import (
    FRAME_WIDTH, FRAME_HEIGHT, CAMERA_ID,
    MAX_NUM_HANDS, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE
)

print("=" * 60)
print("Detection Test (Confidence={})".format(MIN_DETECTION_CONFIDENCE))
print("=" * 60)

cap = cv2.VideoCapture(CAMERA_ID)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

detector = HandDetector(
    max_hands=MAX_NUM_HANDS,
    detection_con=MIN_DETECTION_CONFIDENCE,
    track_con=MIN_TRACKING_CONFIDENCE,
)

print("Camera: OK")
print("Detector: OK")
print("Running 30 frames...\n")

detection_count = 0
for i in range(30):
    success, img = cap.read()
    if not success:
        break
    
    img = cv2.flip(img, 1)
    img = detector.findHands(img, draw=True)
    lmList, bbox = detector.findPosition(img, draw=False)
    
    if len(lmList) > 0:
        detection_count += 1
        print("Frame {}: {} landmarks".format(i+1, len(lmList)))
    else:
        print("Frame {}: No detection".format(i+1))
    
    cv2.imshow("Test", img)
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\nResult: {} / 30 frames detected".format(detection_count))
print("=" * 60)
