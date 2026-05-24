"""
AI Virtual Mouse — Main Application (Video Version)

Reference implementation based on Murtaza's Workshop tutorial.
Single-loop monolithic architecture — all gesture logic and mouse control
in one file. Uses the same gesture mapping as the main project
(practical_no_thumb profile) without hysteresis, debounce, or hold-time.

Flow:
    Webcam → cv2.flip → HandDetector → fingersUp → pattern match
    → np.interp + EMA smoothing → autopy mouse control

Gestures (thumb ignored via None wildcard):
    [*,1,0,0,0]  Move         — cursor follows index finger
    [*,1,1,0,0]  Left Click   — index+middle pinch < 28px
    [*,1,1,1,0]  Right Click  — index+ring pinch < 34px
    [*,0,0,0,0]  Drag         — fist, anchor-based relative movement
    [*,1,1,1,1]  Scroll       — camera center boundary (±35px dead zone)

Controls:
    q — quit

Known limitations: no debounce, handedness-dependent thumb detection,
scroll is Windows-only (ctypes fallback), drag drops on flicker.
"""

import time
import ctypes
import numpy as np
import cv2
import autopy
from HandTrackingModule import HandDetector
from config import (
    FRAME_WIDTH,
    FRAME_HEIGHT,
    CAMERA_ID,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MAX_NUM_HANDS,
    FRAME_REDUCTION,
    SMOOTHING,
    LEFT_CLICK_PINCH_PX,
    RIGHT_CLICK_PINCH_PX,
    SCROLL_CENTER_DEAD_ZONE_PX,
    SCROLL_STEP_AMOUNT,
    SCROLL_REPEAT_MS,
)

# Windows scroll constants (ctypes fallback — autopy lacks scroll)
_MOUSEEVENTF_WHEEL = 0x0800
_WHEEL_DELTA = 120


# ╔═════════════════════════════════════════════════════════════════════╗
# ║  MASALAH #1 / Slide 5: Scroll Nggak Jalan
# ╠═════════════════════════════════════════════════════════════════════╣
# ║  BEFORE (Tutorial — Murtaza's Workshop):
# ║    autopy.mouse.toggle(down=True)     # tahan tombol kiri
# ║    autopy.mouse.toggle(down=False)    # lepas tombol kiri
# ║
# ║    Fungsi toggle() itu untuk "tahan tombol mouse" (press/release),
# ║    BUKAN scroll wheel. Akibatnya: halaman browser nggak gerak.
# ║    Kursor doang yang jalan — bukan scroll beneran.
# ║
# ║  AFTER (Fix):
# ║    autopy.mouse.scroll(amount)                    # preferred
# ║    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, ...)  # fallback
# ║
# ║    Kirim event MOUSEEVENTF_WHEEL langsung ke Windows API.
# ║    Ini scroll wheel beneran — beda dengan toggle().
# ║
# ║  SEBAB: autopy 4.0.1 tidak punya mouse.scroll().
# ║    Versi Autopy yang dipakai tutorial (lebih lama) mungkin berbeda.
# ║    Fallback ctypes = Windows-only, cukup untuk development.
# ╚═════════════════════════════════════════════════════════════════════╝
def _scroll(amount):
    """
    Scroll the mouse wheel.

    Tries autopy.mouse.scroll() first. Falls back to Windows API
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL) because
    autopy 4.0.1 lacks the scroll method.

    Args:
        amount (int): Scroll direction and magnitude.
            Positive = scroll up (away from user).
            Negative = scroll down (toward user).

    Notes:
        Windows wheel delta is in multiples of 120 (WHEEL_DELTA).
        Each unit of amount produces 120 delta = 1 "notch" of scroll.
        This function is Windows-only in fallback mode.
    """
    try:
        autopy.mouse.scroll(amount)
    except AttributeError:
        ctypes.windll.user32.mouse_event(
            _MOUSEEVENTF_WHEEL, 0, 0, amount * _WHEEL_DELTA, 0
        )


def _match_pattern(fingers, pattern):
    """
    Match finger state against a gesture pattern.

    Compares each finger value element-by-element. A pattern value
    of None acts as a wildcard — that position is always considered
    matching regardless of the actual finger state. This is used to
    ignore the unreliable thumb detection.

    Args:
        fingers (list[int]): Actual finger states [thumb, idx, mid, ring, pinky].
            Each element is 0 (folded) or 1 (extended).
        pattern (list[int | None]): Expected pattern of same length.
            None means "ignore this position."

    Returns:
        bool: True if all non-None positions match, False otherwise.
            Also returns False if pattern is None or lengths differ.

    Example:
        >>> _match_pattern([1,1,0,0,0], [None,1,0,0,0])
        True  # Thumb ignored, all other fingers match
        >>> _match_pattern([0,1,0,0,0], [None,1,1,0,0])
        False  # Middle finger doesn't match
    """
    if pattern is None or len(fingers) != len(pattern):
        return False
    for fv, ev in zip(fingers, pattern):
        if ev is None:
            continue
        if int(fv) != int(ev):
            return False
    return True


def main():
    """
    Main application loop: capture → detect → classify → control.

    Initializes webcam, HandDetector, and screen dimensions. Enters
    an infinite loop that processes each frame through gesture detection
    and mouse control. Press 'q' to exit.

    State variables track: drag (active + anchor coordinates),
    click (edge-triggered via click_ready flag),
    scroll (rate-limited via last_scroll_ms),
    smoothing (EMA via ploc/cloc).

    Cleanup on exit: releases any held mouse button, closes webcam,
    destroys all OpenCV windows.
    """
    # ---- Initialize webcam ----
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)

    # ---- Initialize detector ----
    detector = HandDetector(
        max_hands=MAX_NUM_HANDS,
        detection_con=MIN_DETECTION_CONFIDENCE,
        track_con=MIN_TRACKING_CONFIDENCE,
    )

    # ---- Screen size ----
    w_scr, h_scr = autopy.screen.size()
    scroll_center_y = FRAME_HEIGHT // 2

    # ---- Smoothing state ----
    prev_time = 0
    ploc_x, ploc_y = 0, 0
    cloc_x, cloc_y = 0, 0

    # ---- Gesture state ----
    drag_active = False
    drag_anchor_cam_x = 0
    drag_anchor_cam_y = 0
    drag_anchor_scr_x = 0
    drag_anchor_scr_y = 0
    click_ready = True        # edge-triggered click (no auto-repeat)
    last_scroll_ms = 0

    print("=" * 50)
    print("  AI Virtual Mouse — Video Version")
    print("  Gestures: matches main project (practical_no_thumb)")
    print("  Press 'q' to quit")
    print(f"  Screen: {w_scr}x{h_scr}")
    print("=" * 50)

    while True:
        # ---- Step 1: Capture and mirror the frame ----
        # ╔═════════════════════════════════════════════════════════════╗
        # ║  MASALAH #2 / Slide 6: Kursor Kebalik
        # ╠═════════════════════════════════════════════════════════════╣
        # ║  BEFORE (Tutorial):
        # ║    # Webcam menghasilkan gambar mirror, tapi tutorial
        # ║    # tidak melakukan cv2.flip. Sebagai gantinya, tutorial
        # ║    # menggunakan rumus: x_screen = wScr - clocX
        # ║    # (invert x-coordinate di mapping ke layar).
        # ║
        # ║    Masalah: di setup tertentu, rumus ini malah bikin
        # ║    double-inversion — tangan kiri = kursor kiri, tapi
        # ║    harusnya tangan kiri = kursor kanan (atau sebaliknya).
        # ║
        # ║  AFTER (Fix):
        # ║    cv2.flip(img, 1)  # mirror horizontal
        # ║
        # ║    Mirror gambar SEKALI di awal. Setelah itu, koordinat
        # ║    langsung dipakai apa adanya — nggak perlu invert lagi.
        # ║    Hasil: tangan kiri = sisi kiri layar. Natural.
        # ║
        # ║  SEBAB: cv2.flip lebih deterministik dibanding rumus
        # ║    manual wScr - clocX yang sensitif terhadap setup.
        # ╚═════════════════════════════════════════════════════════════╝
        # cv2.flip(img, 1) mirrors horizontally so hand movement
        # feels natural: moving hand left moves cursor left.
        # Without this, the webcam's mirrored image makes movement
        # feel inverted (hand left → cursor right).
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)  # mirror for natural movement
        img = detector.findHands(img)
        lm_list, _bbox = detector.findPosition(img)

        # Draw the frame reduction boundary (purple rectangle).
        # Area inside this rectangle is mapped to the screen;
        # area outside is a dead zone where cursor won't reach
        # the screen edge. Makes control feel more comfortable.
        cv2.rectangle(
            img,
            (FRAME_REDUCTION, FRAME_REDUCTION),
            (FRAME_WIDTH - FRAME_REDUCTION, FRAME_HEIGHT - FRAME_REDUCTION),
            (255, 0, 255),
            2,
        )

        # Draw the horizontal center line (yellow).
        # Used as scroll reference: hand above = scroll up,
        # hand below = scroll down, within ±35px dead zone = no scroll.
        cv2.line(
            img,
            (0, scroll_center_y),
            (FRAME_WIDTH, scroll_center_y),
            (255, 255, 0),
            1,
        )

        mode = "None"
        action = None

        # ---- Step 2: Gesture classification ----
        # Each gesture block checks:
        #   1. Finger pattern match (via _match_pattern with None wildcard)
        #   2. Additional conditions (pinch distance, dead zone position)
        #   3. Creates action string for execution phase
        #
        # Gesture blocks are mutually exclusive (if-elif chain).
        # Priority order: Move > Click > RightClick > Drag > Scroll
        # Move is highest priority because it's the default/resting state.

        if len(lm_list) != 0:
            fingers = detector.fingersUp()

            # ---- MOVE: [*, 1, 0, 0, 0] ----
            # Index finger extended, all others folded.
            # Thumb ignored (None wildcard).
            # Maps index fingertip (landmark 8) to screen coordinates
            # using np.interp with frame_reduction margins, then applies
            # exponential moving average (EMA) smoothing.
            if _match_pattern(fingers, [None, 1, 0, 0, 0]):
                # Release drag on mode switch
                if drag_active:
                    drag_active = False
                    action = "drag_end"

                mode = "Move"

                x1, y1 = lm_list[8][1], lm_list[8][2]
                # np.interp: linear interpolation from camera coords
                # (frame_reduction → width-reduction) to screen coords (0 → w_scr).
                # Frame reduction creates a dead zone at edges — hand near
                # the frame border won't push cursor to screen edge.
                x3 = np.interp(
                    x1,
                    (FRAME_REDUCTION, FRAME_WIDTH - FRAME_REDUCTION),
                    (0, w_scr),
                )
                y3 = np.interp(
                    y1,
                    (FRAME_REDUCTION, FRAME_HEIGHT - FRAME_REDUCTION),
                    (0, h_scr),
                )
                # EMA smoothing: new_position = old + (raw - old) / SMOOTHING
                # Higher SMOOTHING value = smoother cursor but more lag.
                # SMOOTHING=1 = no smoothing (instant, jittery).
                # SMOOTHING=7 = moderate smoothing (default).
                cloc_x = ploc_x + (x3 - ploc_x) / SMOOTHING
                cloc_y = ploc_y + (y3 - ploc_y) / SMOOTHING
                ploc_x, ploc_y = cloc_x, cloc_y

                autopy.mouse.move(cloc_x, cloc_y)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            # ---- LEFT CLICK: [*, 1, 1, 0, 0] + index-middle pinch ----
            # ╔═════════════════════════════════════════════════════════╗
            # ║  MASALAH #5 / Slide 10: Spam Click
            # ╠═════════════════════════════════════════════════════════╣
            # ║  BEFORE (Tutorial):
            # ║    if length < threshold:
            # ║        autopy.mouse.click()  # click SETIAP frame!
            # ║
            # ║    Selama pinch < threshold, setiap frame (30 fps)
            # ║    akan trigger click. Hasil: spam click.
            # ║    Satu gestur pinch 2 detik = 60 click.
            # ║
            # ║  AFTER (Fix):
            # ║    click_ready flag: hanya click saat transisi dari
            # ║    "tidak pinch" ke "pinch". Harus lepas dulu sebelum
            # ║    bisa click lagi (edge-triggered).
            # ║
            # ║  SEBAB: Tanpa edge-triggering, gesture yang
            # ║    dipertahankan beberapa detik akan spam click.
            # ╚═════════════════════════════════════════════════════════╝
            # Index and middle fingers extended, ring and pinky folded.
            # Triggers left click when distance between index tip (8)
            # and middle tip (12) falls below LEFT_CLICK_PINCH_PX (28px).
            #
            # Edge-triggered: click_ready flag ensures only ONE click
            # per pinch gesture. Click fires on first frame where
            # distance < threshold. Must release (distance > threshold)
            # before next click can fire.
            elif _match_pattern(fingers, [None, 1, 1, 0, 0]):
                mode = "Click"
                length, img, line_info = detector.findDistance(8, 12, img)

                if length < LEFT_CLICK_PINCH_PX:
                    cv2.circle(
                        img,
                        (line_info[4], line_info[5]),
                        15,
                        (0, 255, 0),
                        cv2.FILLED,
                    )
                    if click_ready:
                        action = "click"
                        click_ready = False
                else:
                    click_ready = True

            # ---- RIGHT CLICK: [*, 1, 1, 1, 0] + index-ring pinch ----
            # ╔═════════════════════════════════════════════════════════╗
            # ║  MASALAH #4 / Slide 8: Right Click — 5 Jari → 3 Jari
            # ╠═════════════════════════════════════════════════════════╣
            # ║  BEFORE (Tutorial):
            # ║    [1, 1, 1, 1, 1]  # 5 jari naik = right click
            # ║    Mengangkat semua jari bersamaan sangat sulit.
            # ║    Sering gagal terdeteksi atau misinterpret.
            # ║
            # ║  AFTER (Fix):
            # ║    [*, 1, 1, 1, 0]  # telunjuk+tengah+manis, kelingking turun
            # ║    + pinch telunjuk-manis (id 8→16) < 34px
            # ║    Gesture 3 jari jauh lebih natural.
            # ║    Threshold 34px (vs 28px left click) karena
            # ║    jarak telunjuk-manis lebih lebar.
            # ╚═════════════════════════════════════════════════════════╝
            # Index, middle, and ring fingers extended, pinky folded.
            # Triggers right click when distance between index tip (8)
            # and ring tip (16) falls below RIGHT_CLICK_PINCH_PX (34px).
            #
            # Uses larger threshold than left click (34px vs 28px)
            # because index-ring pinch is physically wider.
            elif _match_pattern(fingers, [None, 1, 1, 1, 0]):
                mode = "RightClick"
                length, img, line_info = detector.findDistance(8, 16, img)

                if length < RIGHT_CLICK_PINCH_PX:
                    cv2.circle(
                        img,
                        (line_info[4], line_info[5]),
                        15,
                        (0, 255, 255),
                        cv2.FILLED,
                    )
                    if click_ready:
                        action = "right_click"
                        click_ready = False
                else:
                    click_ready = True

            # ---- DRAG: [*, 0, 0, 0, 0] fist ----
            # ╔═════════════════════════════════════════════════════════╗
            # ║  MASALAH #4 / Slide 8: Drag — Gesture Baru
            # ╠═════════════════════════════════════════════════════════╣
            # ║  BEFORE (Tutorial):
            # ║    Tidak ada gesture Drag. Tutorial hanya:
            # ║    Move, Left Click, Right Click (5 jari), Scroll (broken).
            # ║    Tanpa Drag → tidak bisa drag-and-drop, seleksi teks,
            # ║    resize window.
            # ║
            # ║  AFTER (Fix):
            # ║    [*, 0, 0, 0, 0]  # kepalan (fist) = Drag
            # ║    Anchor-based: cursor bergerak relatif dari posisi
            # ║    awal drag, bukan absolute dari posisi jari.
            # ║    Ini mencegah cursor "teleport" ke jari saat
            # ║    transisi Move → Drag.
            # ║
            # ║  Catatan (video version): tanpa hold-time gate,
            # ║    drag bisa aktif saat transisi gesture.
            # ║    Main version punya hold-time 100ms untuk mencegah ini.
            # ╚═════════════════════════════════════════════════════════╝
            # All four fingers folded (fist). Thumb ignored.
            #
            # On first frame: records anchor = (finger camera position,
            # cursor screen position). Presses and holds left button.
            #
            # Subsequent frames: cursor moves by delta from anchor.
            # new_cursor = anchor_cursor + (current_finger - anchor_finger) * scale.
            # This prevents cursor from teleporting to finger position
            # when entering Drag mode — cursor stays where it was.
            #
            # Releases on any other gesture or hand loss.
            elif _match_pattern(fingers, [None, 0, 0, 0, 0]):
                mode = "Drag"
                click_ready = True

                if not drag_active:
                    # Start drag: store anchor at current cursor position
                    drag_active = True
                    if len(lm_list) > 8:
                        drag_anchor_cam_x = lm_list[8][1]
                        drag_anchor_cam_y = lm_list[8][2]
                        drag_anchor_scr_x, drag_anchor_scr_y = autopy.mouse.location()
                    action = "drag_start"
                else:
                    # Drag active: move cursor relative to anchor
                    if len(lm_list) > 8:
                        dx = lm_list[8][1] - drag_anchor_cam_x
                        dy = lm_list[8][2] - drag_anchor_cam_y
                        scale_x = w_scr / (FRAME_WIDTH - 2 * FRAME_REDUCTION)
                        scale_y = h_scr / (FRAME_HEIGHT - 2 * FRAME_REDUCTION)
                        new_x = drag_anchor_scr_x + dx * scale_x
                        new_y = drag_anchor_scr_y + dy * scale_y
                        autopy.mouse.move(new_x, new_y)
                        cv2.circle(img, (lm_list[8][1], lm_list[8][2]), 15, (0, 0, 255), cv2.FILLED)

            # ---- SCROLL: [*, 1, 1, 1, 1] camera center boundary ----
            # ╔═════════════════════════════════════════════════════════╗
            # ║  MASALAH #4 (lanjutan) / Slide 8: Scroll Fix
            # ╠═════════════════════════════════════════════════════════╣
            # ║  BEFORE (Tutorial):
            # ║    Scroll pakai toggle() — bukan scroll wheel.
            # ║    Efek: kursor gerak, halaman tidak.
            # ║
            # ║  AFTER (Fix × 2):
            # ║    1. _scroll() pakai ctypes Windows API (Masalah #1).
            # ║    2. Camera center boundary: tangan di atas center →
            # ║       scroll up, di bawah → scroll down.
            # ║    3. Dead zone ±35px di tengah → stabilitas.
            # ║    4. Rate-limited 120ms → cegah hyper-scroll.
            # ╚═════════════════════════════════════════════════════════╝
            # All four fingers extended. Thumb ignored.
            #
            # Camera frame divided into 3 horizontal zones:
            #   TOP:    index_y < center - dead_zone  →  scroll UP
            #   MIDDLE: within ±dead_zone of center    →  no scroll
            #   BOTTOM: index_y > center + dead_zone  →  scroll DOWN
            #
            # Rate-limited: minimum SCROLL_REPEAT_MS (120ms) between
            # scroll actions to prevent hyper-fast scrolling.
            elif _match_pattern(fingers, [None, 1, 1, 1, 1]):
                mode = "Scroll"
                click_ready = True  # release click lock
                if drag_active:
                    drag_active = False
                    action = "drag_end"

                now_ms = time.time() * 1000
                if now_ms - last_scroll_ms >= SCROLL_REPEAT_MS:
                    index_y = lm_list[8][2]
                    top_zone = scroll_center_y - SCROLL_CENTER_DEAD_ZONE_PX
                    bottom_zone = scroll_center_y + SCROLL_CENTER_DEAD_ZONE_PX

                    if index_y < top_zone:
                        action = ("scroll", SCROLL_STEP_AMOUNT)
                        last_scroll_ms = now_ms
                    elif index_y > bottom_zone:
                        action = ("scroll", -SCROLL_STEP_AMOUNT)
                        last_scroll_ms = now_ms
                    cv2.circle(img, (lm_list[8][1], lm_list[8][2]), 15, (0, 255, 255), cv2.FILLED)

            # ---- No recognized gesture: reset all active states ----
            # Unrecognized finger pattern → release click lock,
            # end drag if active, no mouse action.
            else:
                mode = "None"
                click_ready = True
                if drag_active:
                    drag_active = False
                    action = "drag_end"

        else:
            # Hand lost
            mode = "None"
            click_ready = True
            if drag_active:
                drag_active = False
                action = "drag_end"

        # ---- Step 3: Execute pending mouse actions ----
        # Actions are deferred until after all gesture processing
        # so that the execution happens once per frame (not per gesture block).
        # This prevents double-execution when mode switch triggers
        # both a drag_end and a click in the same frame.
        if action == "click":
            autopy.mouse.click()
        elif action == "right_click":
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
        elif action == "drag_start":
            autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
        elif action == "drag_end":
            autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
        elif isinstance(action, tuple) and action[0] == "scroll":
            _, amount = action
            _scroll(int(amount))

        # ---- Step 4: FPS counter ----
        # Calculates frames per second from time delta between iterations.
        # prev_time is initialized to 0, so first frame shows fps=0.
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        cv2.putText(
            img,
            str(int(fps)),
            (28, 58),
            cv2.FONT_HERSHEY_PLAIN,
            3,
            (255, 8, 8),
            3,
        )

        # ---- Step 5: Mode overlay ----
        # Displays current gesture mode with color coding:
        #   Move=green, Click=blue, RightClick=orange,
        #   Drag=red, Scroll=yellow, None=white.
        # Helps with visual debugging during development.
        mode_colors = {
            "Move": (0, 255, 0),
            "Click": (255, 0, 0),
            "RightClick": (0, 165, 255),
            "Drag": (0, 0, 255),
            "Scroll": (0, 255, 255),
            "None": (255, 255, 255),
        }
        color = mode_colors.get(mode, (255, 255, 255))
        cv2.putText(
            img,
            f"Mode: {mode}",
            (20, 110),
            cv2.FONT_HERSHEY_PLAIN,
            2,
            color,
            2,
        )

        # ---- Display ----
        cv2.imshow("AI Virtual Mouse — Video Version", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Cleanup
    if drag_active:
        autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
    cap.release()
    cv2.destroyAllWindows()
    print("[AI Virtual Mouse — Video Version] Shutdown complete.")


if __name__ == "__main__":
    main()
