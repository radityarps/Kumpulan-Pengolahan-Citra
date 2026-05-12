"""
Thumb Detection Tuning Tool
Test dan calibrate THUMB_SENSITIVITY untuk anatomis tangan anda
"""
import cv2
import sys
import os
import math

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.hand_tracking_module import HandDetector
from src.config import (
    FRAME_WIDTH, FRAME_HEIGHT, CAMERA_ID,
    MAX_NUM_HANDS, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE,
    THUMB_SENSITIVITY
)

def calculate_thumb_distance(lmList):
    """Calculate thumb tip-to-MCP distance"""
    if len(lmList) < 5:
        return None
    
    thumb_tip = lmList[4]  # tip
    thumb_mcp = lmList[2]  # MCP (base)
    
    dist = math.sqrt(
        (thumb_tip[1] - thumb_mcp[1]) ** 2 +
        (thumb_tip[2] - thumb_mcp[2]) ** 2
    )
    return dist

def main():
    print("=" * 70)
    print("  Thumb Detection Tuning Tool")
    print("=" * 70)
    print("\nCurrent THUMB_SENSITIVITY: {}".format(THUMB_SENSITIVITY))
    print("Current threshold: {} px (35.0 * {})".format(35.0 * THUMB_SENSITIVITY, THUMB_SENSITIVITY))
    print("\nInstructions:")
    print("1. Press 'e' to sample EXTENDED thumb (full open)")
    print("2. Press 'f' to sample FOLDED thumb (fully closed)")
    print("3. Press 'q' to quit and show calibration")
    print("\nCollect at least 3 samples of each for best results.\n")
    
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    detector = HandDetector(
        max_hands=MAX_NUM_HANDS,
        detection_con=MIN_DETECTION_CONFIDENCE,
        track_con=MIN_TRACKING_CONFIDENCE,
    )
    
    extended_samples = []
    folded_samples = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame = detector.findHands(frame, draw=True)
        lmList, _ = detector.findPosition(frame, draw=False)
        
        if lmList:
            thumb_dist = calculate_thumb_distance(lmList)
            fingers = detector.fingersUp()
            
            # Display info
            cv2.putText(frame, "Thumb Distance: {:.1f} px".format(thumb_dist), (20, 50),
                       cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
            cv2.putText(frame, "Thumb State: {}".format("OPEN" if fingers[0] else "CLOSED"), (20, 80),
                       cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0) if fingers[0] else (0, 0, 255), 2)
            cv2.putText(frame, "Samples - Extended: {} | Folded: {}".format(
                len(extended_samples), len(folded_samples)), (20, 110),
                       cv2.FONT_HERSHEY_PLAIN, 1.2, (200, 200, 0), 1)
            cv2.putText(frame, "Press 'e'=extend, 'f'=fold, 'q'=quit", (20, 130),
                       cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "No hand detected", (20, 50),
                       cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
        
        cv2.imshow("Thumb Tuning", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e') and lmList:
            thumb_dist = calculate_thumb_distance(lmList)
            extended_samples.append(thumb_dist)
            print("[EXTENDED] Distance: {:.1f} px".format(thumb_dist))
        elif key == ord('f') and lmList:
            thumb_dist = calculate_thumb_distance(lmList)
            folded_samples.append(thumb_dist)
            print("[FOLDED] Distance: {:.1f} px".format(thumb_dist))
    
    cap.release()
    cv2.destroyAllWindows()
    
    if not extended_samples or not folded_samples:
        print("\n[ERROR] Not enough samples. Collect at least one of each.")
        return
    
    # Analysis
    print("\n" + "=" * 70)
    print("  CALIBRATION RESULTS")
    print("=" * 70)
    
    ext_avg = sum(extended_samples) / len(extended_samples)
    ext_min = min(extended_samples)
    ext_max = max(extended_samples)
    
    fold_avg = sum(folded_samples) / len(folded_samples)
    fold_min = min(folded_samples)
    fold_max = max(folded_samples)
    
    print("\nEXTENDED THUMB:")
    print("  Samples: {}".format(len(extended_samples)))
    print("  Range: {:.1f} - {:.1f} px".format(ext_min, ext_max))
    print("  Average: {:.1f} px".format(ext_avg))
    
    print("\nFOLDED THUMB:")
    print("  Samples: {}".format(len(folded_samples)))
    print("  Range: {:.1f} - {:.1f} px".format(fold_min, fold_max))
    print("  Average: {:.1f} px".format(fold_avg))
    
    print("\n" + "-" * 70)
    
    # Calculate optimal threshold
    gap = ext_min - fold_max
    if gap > 0:
        optimal_threshold = (ext_min + fold_max) / 2.0
        print("Optimal threshold: {:.1f} px (gap: {:.1f} px)".format(optimal_threshold, gap))
        
        # Calculate THUMB_SENSITIVITY needed
        optimal_sensitivity = optimal_threshold / 35.0
        print("Recommended THUMB_SENSITIVITY: {:.2f}".format(optimal_sensitivity))
        
        print("\nTo apply: Edit src/config.py and set:")
        print("  THUMB_SENSITIVITY = {:.2f}".format(optimal_sensitivity))
    else:
        print("[WARNING] Threshold overlap detected!")
        print("Ranges may be too close or sampling was inconsistent.")
        print("Try again with more extreme poses (fully open/fully closed)")
    
    print("\n" + "=" * 70)
    print("Tips for better detection:")
    print("- Ensure good lighting")
    print("- Keep hand fully in frame")
    print("- For EXTENDED: fully open thumb, spread away from other fingers")
    print("- For FOLDED: fully close thumb, tuck into palm")
    print("=" * 70)

if __name__ == "__main__":
    main()
