"""
AI Virtual Mouse — Main Application

Real-time hand gesture-based cursor control using OpenCV, MediaPipe, and
Autopy. This is the orchestrator that integrates all modules in a
single main loop.

╔══════════════════════════════════════════════════════════════════════╗
║  MASALAH #7 / Slide 12-13: Monolithic → Modular Rewrite
╠══════════════════════════════════════════════════════════════════════╣
║  BEFORE (Video Version / Tutorial):
║    Semua logic — deteksi tangan, klasifikasi gestur, mapping
║    koordinat, kontrol mouse, FPS counter, UI overlay — dalam
║    SATU main loop, SATU file (AIVirtualMouse.py, ~200 baris).
║
║    Konsekuensi:
║    1. Nggak bisa unit test. Harus tes manual dengan webcam.
║    2. Ubah satu threshold → bisa ngerusak logic lain.
║    3. Tambah gesture → takut ngerusak yang existing.
║    4. Nggak ada jaminan correctness.
║
║  AFTER (Rewrite Modular):
║    8 modul, masing-masing 1 tanggung jawab:
║    - HandDetector: hanya MediaPipe (nggak tahu gesture)
║    - GestureClassifier: hanya klasifikasi (nggak tahu layar)
║    - CoordinateMapper: hanya mapping (nggak tahu gesture)
║    - MouseController: hanya eksekusi (nggak tahu asal perintah)
║    - config, gesture_profiles, utils: support modules
║
║    Hasil: 33 unit tests. Ubah threshold → run test, 2 detik.
║    GestureClassifier salah? → run test_gesture_classifier.py.
║    Nggak perlu webcam. Ini perbedaan antara kode yang
║    "jalan" dan kode yang "benar dan terverifikasi".
║
║  SEBAB: Separation of concerns. Setiap modul bisa di-test
║    secara terisolasi dan di-replace tanpa mempengaruhi
║    modul lain.
╚══════════════════════════════════════════════════════════════════════╝

Architecture:
    Webcam → HandDetector → GestureClassifier → CoordinateMapper
           → MouseController → Screen

Pipeline per frame:
    1. Capture frame from webcam
    2. Mirror horizontally (cv2.flip) for natural movement feel
    3. Detect hands and extract 21 landmarks (HandDetector)
    4. Get finger states [thumb, idx, mid, ring, pinky] (fingersUp)
    5. Classify gesture mode + action (GestureClassifier with debounce)
    6. Map finger coords to screen coords + apply smoothing (CoordinateMapper)
    7. Execute mouse actions: move, click, drag, scroll (MouseController)
    8. Overlay FPS, mode, finger debug info (utils)
    9. Display frame and check keyboard input

Modules:
    - hand_tracking_module.py: MediaPipe Tasks API wrapper
    - gesture_classifier.py: State machine with hysteresis + debounce
    - coordinate_mapper.py: Interpolation + EMA smoothing
    - mouse_controller.py: Autopy wrapper with Windows scroll fallback
    - config.py: All tunable constants
    - gesture_profiles.py: Switchable gesture pattern definitions
    - utils.py: FPS counter, mode overlay, status text

Usage:
    python src/ai_virtual_mouse.py

Controls:
    q — quit
    l — toggle landmark visualization (hide/show hand skeleton)
"""

import os
import sys
import time

# Enable running as `python src/ai_virtual_mouse.py` from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2  # noqa: E402
import autopy  # noqa: E402
from src.hand_tracking_module import HandDetector  # noqa: E402
from src.gesture_classifier import GestureClassifier  # noqa: E402
from src.coordinate_mapper import CoordinateMapper  # noqa: E402
from src.mouse_controller import MouseController  # noqa: E402
from src.config import (  # noqa: E402
    FRAME_WIDTH,
    FRAME_HEIGHT,
    CAMERA_ID,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    CLICK_THRESHOLD_PX,
    DRAG_THRESHOLD_PX,
    DEBOUNCE_TIME_MS,
    GESTURE_STYLE,
    SCROLL_SENSITIVITY,
    SCROLL_DEAD_ZONE_PX,
    FRAME_REDUCTION,
    SMOOTHING_FACTOR,
    CLICK_DELAY,
    LANDMARK_VISIBLE_DEFAULT,
    DEBUG_ACTION,
    DEBUG_FINGERS,
    COLOR_GREEN,
    HAND_LOST_GRACE_FRAMES,
)
from src.utils import put_fps, put_mode_text  # noqa: E402


def main():
    """
    Main loop: capture → detect → classify → map → control.

    Initializes all modules (HandDetector, GestureClassifier,
    CoordinateMapper, MouseController) and enters the processing
    loop. Each iteration processes one webcam frame through the
    full pipeline.

    State managed at this level:
        - hand_lost_frames: counter for hand-lost grace period.
          Resets state only after HAND_LOST_GRACE_FRAMES consecutive
          missed detections.
        - show_landmarks: toggle for landmark overlay (key 'l').
        - last_action_text: debug display of most recent action.
        - prev_time: timestamp for FPS calculation.

    Drag anchor: managed by CoordinateMapper, not here.
    Gesture state: managed by GestureClassifier, not here.
    Drag button state: managed by MouseController, not here.

    Cleanup: releases held mouse buttons, closes webcam, destroys
    all OpenCV windows on exit.
    """
    # ---- Initialize webcam ----
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam. Check CAMERA_ID in config.py.")
        return

    # ---- Initialize modules ----
    detector = HandDetector(
        max_hands=MAX_NUM_HANDS,
        detection_con=MIN_DETECTION_CONFIDENCE,
        track_con=MIN_TRACKING_CONFIDENCE,
    )
    classifier = GestureClassifier(
        click_threshold=CLICK_THRESHOLD_PX,
        drag_threshold=DRAG_THRESHOLD_PX,
        debounce_ms=DEBOUNCE_TIME_MS,
        scroll_sensitivity=SCROLL_SENSITIVITY,
        scroll_dead_zone=SCROLL_DEAD_ZONE_PX,
        gesture_style=GESTURE_STYLE,
    )
    mapper = CoordinateMapper(
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        frame_reduction=FRAME_REDUCTION,
        smoothing_factor=SMOOTHING_FACTOR,
    )
    controller = MouseController(click_delay=CLICK_DELAY)

    # ---- State ----
    prev_time = time.time()
    show_landmarks = LANDMARK_VISIBLE_DEFAULT
    hand_lost_frames = 0
    last_action_text = "None"

    print("=" * 50)
    print("  AI Virtual Mouse")
    print("  Controls: q=quit, l=toggle landmarks")
    print(f"  Gesture style: {GESTURE_STYLE}")
    print(f"  Screen: {mapper.screen_width}x{mapper.screen_height}")
    print("=" * 50)

    # ---- Main loop ----
    while True:
        # ================================================================
        # PHASE 1: Capture frame
        # ================================================================
        # Read one frame from the webcam. If reading fails (e.g., webcam
        # disconnected), break out of the loop and clean up.
        success, img = cap.read()
        if not success:
            print("[ERROR] Failed to read frame from webcam.")
            break

        # ╔══════════════════════════════════════════════════════════╗
        # ║  MASALAH #2 / Slide 6: Kursor Kebalik
        # ╠══════════════════════════════════════════════════════════╣
        # ║  BEFORE (Tutorial):
        # ║    # Tutorial tidak flip gambar, tapi invert x-coord:
        # ║    # x_screen = wScr - clocX
        # ║    # Di setup tertentu, rumus ini bikin double-inversion.
        # ║
        # ║  AFTER (Fix):
        # ║    cv2.flip(img, 1)  # mirror SEKALI di awal
        # ║    Setelah flip, koordinat langsung dipakai apa adanya.
        # ║    Hasil: tangan kiri = sisi kiri layar. Natural.
        # ║
        # ║  SEBAB: cv2.flip lebih deterministik daripada
        # ║    rumus manual wScr - clocX.
        # ╚══════════════════════════════════════════════════════════╝
        # Mirror the image horizontally for natural hand movement.
        # Without this, moving hand left makes cursor go right
        # (webcam image is mirrored by default in most drivers).
        img = cv2.flip(img, 1)

        # ================================================================
        # PHASE 2: Hand detection
        # ================================================================
        # findHands: runs MediaPipe detection, optionally draws skeleton.
        # findPosition: converts normalized landmarks to pixel coords.
        img = detector.findHands(img, draw=show_landmarks)
        lmList, bbox = detector.findPosition(img, draw=False)

        # ================================================================
        # PHASE 3: Gesture classification
        # ================================================================
        # Only classify when a hand is detected. Otherwise, increment
        # the hand_lost counter and apply grace period before resetting.
        #
        # Initialize mode/action to safe defaults before classification.
        # When no hand is detected, these fall through to the else block
        # and remain None so downstream phases are no-ops.
        mode = "None"
        action = None

        if lmList:
            hand_lost_frames = 0
            fingers = detector.fingersUp()

            # Build distance callable bound to the detector.
            # Wraps detector.findDistance so the classifier doesn't
            # need a direct reference to the detector object.
            def _get_distance(p1, p2, draw=False):
                return detector.findDistance(p1, p2, draw=draw)

            # Run the full classifier: pattern match → hysteresis →
            # hold-time → debounce. Returns (mode, action) for downstream.
            mode, action = classifier.classify(fingers, lmList, _get_distance)
            if action is not None:
                last_action_text = str(action)

            # Debug overlay: show finger states and pattern match status.
            # Controlled by DEBUG_FINGERS in config.py.
            if DEBUG_FINGERS:
                finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
                move_patterns = tuple(classifier.profile["move_patterns"])
                match_move = any(
                    classifier._match_pattern(fingers, pattern)
                    for pattern in move_patterns
                )
                status = "MATCH!" if match_move else f"need one of {move_patterns}"
                dbg_text = f"Fingers: {fingers}  ({'/'.join(f'{n}={v}' for n, v in zip(finger_names, fingers, strict=False))})"
                cv2.putText(
                    img,
                    dbg_text,
                    (20, 130),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.0,
                    COLOR_GREEN if match_move else (0, 165, 255),
                    1,
                )
                cv2.putText(
                    img,
                    f"Style: {GESTURE_STYLE} | Move: {status} | Mode: {mode}",
                    (20, 155),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.0,
                    COLOR_GREEN if mode == "Move" else (0, 165, 255),
                    1,
                )
        else:
            hand_lost_frames += 1
            if hand_lost_frames >= HAND_LOST_GRACE_FRAMES:
                classifier.reset()
                mapper.reset_smoothing()
                # Release drag if hand was lost during active drag
                if controller.drag_active:
                    controller.execute("drag_end")

        # ================================================================
        # PHASE 4: Drag anchor management
        # ================================================================
        # Must happen BEFORE coordinate processing so that the current
        # frame uses relative (not absolute) positioning during drag.
        #
        # drag_start: record finger camera position + cursor screen
        #   position. Prevents cursor from teleporting to the finger
        #   when switching from Move to Drag.
        # drag_end / hand loss: clear anchor for clean absolute coords.
        if action == "drag_start":
            if lmList and len(lmList) > 8:
                # Anchor cursor at its current screen position, not finger position.
                # This prevents the cursor from teleporting to the finger when
                # the user switches from Move to Drag gesture.
                cur_x, cur_y = autopy.mouse.location()
                mapper.set_drag_anchor(lmList[8][1], lmList[8][2], cur_x, cur_y)
        elif action == "drag_end":
            mapper.clear_drag_anchor()

        # Also clear drag anchor if hand was lost (prevents stuck drag state)
        if not lmList and mapper.drag_anchor_cam is not None:
            mapper.clear_drag_anchor()

        # ================================================================
        # PHASE 5: Coordinate mapping + mouse control
        # ================================================================
        # Update smoothing state even for non-movement modes to prevent
        # large cursor jumps when transitioning back to Move/Drag.
        smooth_x, smooth_y = None, None
        if lmList and len(lmList) > 8:
            ix, iy = lmList[8][1], lmList[8][2]
            if mode == "Drag" and mapper.drag_anchor_cam is not None:
                # Anchor-relative movement: cursor moves by delta from
                # where drag started, not from absolute finger position.
                smooth_x, smooth_y = mapper.process_drag(ix, iy)
            else:
                # Absolute movement: map fingertip directly to screen coords.
                smooth_x, smooth_y = mapper.process(ix, iy)

        # Only move cursor in movement modes (Move, Drag) and only
        # when movement is not frozen (post-click freeze is active).
        if (
            smooth_x is not None
            and smooth_y is not None
            and mode in ("Move", "Drag")
            and not classifier.is_movement_frozen()
        ):
            # Cursor follows index fingertip (landmark 8) only in movement modes.
            controller.execute("move", screen_x=smooth_x, screen_y=smooth_y)

        # Dispatch all action types to the mouse controller.
        # Actions are mutually exclusive — only one fires per frame.
        if action == "click":
            controller.execute("click")

        if action == "double_click":
            controller.execute("double_click")

        if action == "right_click":
            controller.execute("right_click")

        if action == "drag_start":
            controller.execute("drag_start")

        if action == "drag_end":
            controller.execute("drag_end")

        # Scroll action is a tuple: ("scroll", amount). Unwrap and dispatch.
        if isinstance(action, tuple) and action[0] == "scroll":
            _scroll_type, scroll_amount = action
            controller.execute(("scroll", scroll_amount))

        # ================================================================
        # PHASE 6: UI overlay
        # ================================================================
        # FPS counter (top-left), mode text (below FPS), action debug
        # text (below mode), and index finger coordinate overlay.
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time) if prev_time else 0.0
        prev_time = curr_time

        put_fps(img, int(fps))
        put_mode_text(img, mode)

        if DEBUG_ACTION:
            cv2.putText(
                img,
                f"Action: {last_action_text}",
                (20, 180),
                cv2.FONT_HERSHEY_PLAIN,
                1.1,
                COLOR_GREEN,
                1,
            )

        # Optional: show smoothed coordinates in debug
        if lmList and mode != "None" and len(lmList) > 8:
            cv2.putText(
                img,
                f"({lmList[8][1]}, {lmList[8][2]})",
                (20, 150),
                cv2.FONT_HERSHEY_PLAIN,
                1.2,
                COLOR_GREEN,
                1,
            )

        # Display the processed frame in the OpenCV window.
        cv2.imshow("AI Virtual Mouse", img)

        # ================================================================
        # PHASE 7: Keyboard input
        # ================================================================
        # q = quit the application.
        # l = toggle landmark skeleton overlay on/off.
        # 1ms waitKey required for OpenCV to update the display window.
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("l"):
            show_landmarks = not show_landmarks

    # ================================================================
    # CLEANUP
    # ================================================================
    # Release any held mouse button (prevents stuck drag after exit),
    # close the webcam, and destroy all OpenCV windows.
    controller.cleanup()
    cap.release()
    cv2.destroyAllWindows()
    print("[AI Virtual Mouse] Shutdown complete.")


if __name__ == "__main__":
    main()
