"""
Debug script untuk test hand detection secara langsung.
Cek apakah MediaPipe bisa detect tangan dari webcam.
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

def main():
    print("=" * 60)
    print("  Hand Detection Debug Test")
    print("=" * 60)
    
    # Open webcam
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam")
        return
    
    print(f"[OK] Webcam opened")
    print(f"     Camera ID: {CAMERA_ID}")
    print(f"     Frame size: {FRAME_WIDTH}x{FRAME_HEIGHT}")
    
    # Create detector
    try:
        detector = HandDetector(
            max_hands=MAX_NUM_HANDS,
            detection_con=MIN_DETECTION_CONFIDENCE,
            track_con=MIN_TRACKING_CONFIDENCE,
        )
        print(f"[OK] HandDetector created")
        print(f"     Detection confidence: {MIN_DETECTION_CONFIDENCE}")
        print(f"     Tracking confidence: {MIN_TRACKING_CONFIDENCE}")
    except Exception as e:
        print(f"[ERROR] Failed to create detector: {e}")
        cap.release()
        return
    
    # Test loop
    print("\n[INFO] Running detection test for 10 seconds...")
    print("       Show your hand to the camera...\n")
    
    frame_count = 0
    detection_count = 0
    frame_with_detections = []
    
    import time
    start = time.time()
    while time.time() - start < 10:
        success, img = cap.read()
        if not success:
            print("[ERROR] Failed to read frame")
            break
        
        img = cv2.flip(img, 1)
        
        # Run detection
        try:
            img_with_landmarks = detector.findHands(img, draw=True)
            lmList, bbox = detector.findPosition(img_with_landmarks, draw=True)
            
            if lmList:
                detection_count += 1
                frame_with_detections.append({
                    'frame': frame_count,
                    'landmarks': len(lmList),
                    'bbox': bbox,
                    'fingers': detector.fingersUp()
                })
                
                # Print first few detections
                if detection_count <= 3:
                    fingers = detector.fingersUp()
                    print(f"[DETECT #{detection_count}] Frame {frame_count}: {len(lmList)} landmarks")
                    print(f"           Fingers: {fingers}")
                    print(f"           BBox: {bbox}")
        except Exception as e:
            print(f"[ERROR] Detection failed at frame {frame_count}: {e}")
        
        frame_count += 1
        
        # Display the frame with landmarks
        cv2.imshow("Hand Detection Debug", img_with_landmarks)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    elapsed = time.time() - start
    cap.release()
    cv2.destroyAllWindows()
    
    # Results
    print("\n" + "=" * 60)
    print("  DETECTION RESULTS")
    print("=" * 60)
    print(f"Total frames: {frame_count}")
    print(f"Frames with hand detections: {detection_count}")
    print(f"Detection rate: {100 * detection_count / frame_count if frame_count > 0 else 0:.1f}%")
    print(f"FPS: {frame_count / elapsed:.1f}")
    
    if detection_count == 0:
        print("\n[WARNING] No hands detected!")
        print("\nTroubleshooting:")
        print("1. Check lighting - move to well-lit area")
        print("2. Position hand fully in frame")
        print("3. Try lowering MIN_DETECTION_CONFIDENCE in config.py")
        print("4. Check that webcam is working (test with different app)")
    else:
        print(f"\n[OK] Detection working! Found hands in {detection_count} frames")
        if frame_with_detections:
            print(f"\nFirst detection stats:")
            first = frame_with_detections[0]
            print(f"  Landmarks: {first['landmarks']}")
            print(f"  Fingers detected: {first['fingers']}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
