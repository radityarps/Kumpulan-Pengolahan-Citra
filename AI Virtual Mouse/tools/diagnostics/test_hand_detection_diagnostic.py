"""
Comprehensive detection diagnostic - identify where hand detection fails
"""
import cv2
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.hand_tracking_module import HandDetector
from src.config import (
    FRAME_WIDTH, FRAME_HEIGHT, CAMERA_ID,
    MAX_NUM_HANDS, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE
)

def diagnose():
    print("=" * 70)
    print("  AI Virtual Mouse - Hand Detection Diagnostic")
    print("=" * 70)
    
    # Step 1: Webcam check
    print("\n[STEP 1] Checking webcam...")
    cap = cv2.VideoCapture(CAMERA_ID)
    
    if not cap.isOpened():
        print("[FAIL] Cannot open webcam at device ID:", CAMERA_ID)
        print("       → Try different camera ID in config.py")
        return
    
    print(f"[OK] Webcam opened (device ID: {CAMERA_ID})")
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    # Step 2: Read sample frame
    print("\n[STEP 2] Reading sample frame...")
    success, img = cap.read()
    if not success:
        print("[FAIL] Cannot read frame from webcam")
        cap.release()
        return
    
    print(f"[OK] Read frame: {img.shape}")
    
    # Step 3: Create detector
    print(f"\n[STEP 3] Creating HandDetector...")
    print(f"         Detection threshold: {MIN_DETECTION_CONFIDENCE}")
    print(f"         Tracking threshold: {MIN_TRACKING_CONFIDENCE}")
    
    try:
        detector = HandDetector(
            max_hands=MAX_NUM_HANDS,
            detection_con=MIN_DETECTION_CONFIDENCE,
            track_con=MIN_TRACKING_CONFIDENCE,
        )
        print(f"[OK] HandDetector created")
    except Exception as e:
        print(f"[FAIL] Cannot create detector: {e}")
        cap.release()
        return
    
    # Step 4: Run detection on sample frame
    print(f"\n[STEP 4] Running detection on sample frame...")
    try:
        result_img = detector.findHands(img, draw=True)
        print(f"[OK] findHands() executed")
        
        # Check detection_result
        if detector.detection_result is None:
            print("[WARN] detection_result is None")
        elif detector.detection_result.hand_landmarks is None:
            print("[WARN] detection_result.hand_landmarks is None")
        else:
            hand_count = len(detector.detection_result.hand_landmarks)
            print(f"[OK] Hand landmarks found: {hand_count} hands")
            if hand_count > 0:
                first_hand = detector.detection_result.hand_landmarks[0]
                print(f"     First hand has {len(first_hand)} landmarks")
        
    except Exception as e:
        print(f"[FAIL] Detection failed: {e}")
        import traceback
        traceback.print_exc()
        cap.release()
        return
    
    # Step 5: Extract landmarks
    print(f"\n[STEP 5] Extracting landmark coordinates...")
    try:
        lmList, bbox = detector.findPosition(img, draw=False)
        print(f"[OK] Landmarks extracted: {len(lmList)} points")
        print(f"     BBox: {bbox}")
        
        if len(lmList) > 0:
            print(f"     First 3 landmarks: {lmList[:3]}")
        
    except Exception as e:
        print(f"[FAIL] findPosition() failed: {e}")
        cap.release()
        return
    
    # Step 6: Get finger states
    print(f"\n[STEP 6] Getting finger states...")
    try:
        fingers = detector.fingersUp()
        print(f"[OK] Fingers: {fingers}")
        print(f"     Type: {type(fingers)}")
        
    except Exception as e:
        print(f"[FAIL] fingersUp() failed: {e}")
        cap.release()
        return
    
    # Step 7: Test on 30 frames
    print(f"\n[STEP 7] Running 30-frame detection test...")
    print("         Position hand in view, try different hand poses...\n")
    
    detection_count = 0
    landmarks_counts = []
    
    for i in range(30):
        success, img = cap.read()
        if not success:
            break
        
        img = cv2.flip(img, 1)
        
        try:
            img = detector.findHands(img, draw=True)
            lmList, bbox = detector.findPosition(img, draw=False)
            fingers = detector.fingersUp()
            
            if len(lmList) > 0:
                detection_count += 1
                landmarks_counts.append(len(lmList))
                status = f"OK {len(lmList)} landmarks - fingers: {fingers}"
            else:
                status = "NO landmarks"
            
            print(f"  Frame {i+1:2d}: {status}")
            
            cv2.imshow("Diagnostic", img)
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break
                
        except Exception as e:
            print(f"  Frame {i+1:2d}: ERROR - {e}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Final report
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if detection_count == 0:
        print("[FAIL] No hand detected in 30 frames")
        print("\nRECOMMENDATIONS:")
        print("1. Ensure webcam is working (test with other app)")
        print("2. Move hand fully into frame, try different poses")
        print("3. Improve lighting conditions")
        print("4. Try lowering MIN_DETECTION_CONFIDENCE in config.py (0.7 -> 0.6)")
        print("5. Check if MediaPipe model file exists:")
        print(f"   {os.path.join(PROJECT_ROOT, 'src', 'hand_landmarker.task')}")
    else:
        print(f"[OK] Hand detected in {detection_count}/30 frames ({100*detection_count/30:.1f}%)")
        if landmarks_counts:
            print(f"     Landmarks per detection: avg={sum(landmarks_counts)/len(landmarks_counts):.0f}")
            print(f"     This is expected (21 landmarks for a full hand)")
        
        print("\nProject is ready for integration testing!")
        print("Run: python src/ai_virtual_mouse.py")
    
    print("=" * 70)

if __name__ == "__main__":
    diagnose()
