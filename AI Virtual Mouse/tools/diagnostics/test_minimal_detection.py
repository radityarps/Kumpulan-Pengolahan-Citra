"""
Minimal test untuk check detection result dari MediaPipe.
"""
import cv2
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.hand_tracking_module import HandDetector
from src.config import FRAME_WIDTH, FRAME_HEIGHT, CAMERA_ID, MAX_NUM_HANDS, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE

cap = cv2.VideoCapture(CAMERA_ID)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

detector = HandDetector(
    max_hands=MAX_NUM_HANDS,
    detection_con=MIN_DETECTION_CONFIDENCE,
    track_con=MIN_TRACKING_CONFIDENCE,
)

print(f"Confidence threshold: {MIN_DETECTION_CONFIDENCE}")
print(f"Running 30 frames test...\n")

for i in range(30):
    success, img = cap.read()
    if not success:
        break
    
    img = cv2.flip(img, 1)
    img = detector.findHands(img, draw=True)
    
    # Check raw detection_result
    if detector.detection_result is not None:
        hand_count = len(detector.detection_result.hand_landmarks) if detector.detection_result.hand_landmarks else 0
        print(f"Frame {i}: detection_result exists, hands={hand_count}")
        
        if detector.detection_result.hand_landmarks:
            for j, hand_lm in enumerate(detector.detection_result.hand_landmarks):
                print(f"  Hand {j}: {len(hand_lm)} landmarks")
    else:
        print(f"Frame {i}: detection_result is None")
    
    lmList, bbox = detector.findPosition(img, draw=False)
    print(f"         lmList size: {len(lmList)}, bbox: {bbox}")
    
    cv2.imshow("Test", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    time.sleep(0.1)

cap.release()
cv2.destroyAllWindows()
print("\nTest complete")
