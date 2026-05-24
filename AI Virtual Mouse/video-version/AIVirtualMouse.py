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


def _scroll(amount):
    """Scroll mouse wheel. Positive = up, negative = down."""
    try:
        autopy.mouse.scroll(amount)
    except AttributeError:
        ctypes.windll.user32.mouse_event(
            _MOUSEEVENTF_WHEEL, 0, 0, amount * _WHEEL_DELTA, 0
        )


def _match_pattern(fingers, pattern):
    """Pattern match with None = wildcard (thumb ignored)."""
    if pattern is None or len(fingers) != len(pattern):
        return False
    for fv, ev in zip(fingers, pattern):
        if ev is None:
            continue
        if int(fv) != int(ev):
            return False
    return True


def main():
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
        # Step 1: Capture and mirror
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)  # mirror for natural movement
        img = detector.findHands(img)
        lm_list, _bbox = detector.findPosition(img)

        # Draw frame reduction zone
        cv2.rectangle(
            img,
            (FRAME_REDUCTION, FRAME_REDUCTION),
            (FRAME_WIDTH - FRAME_REDUCTION, FRAME_HEIGHT - FRAME_REDUCTION),
            (255, 0, 255),
            2,
        )

        # Draw scroll center zone
        cv2.line(
            img,
            (0, scroll_center_y),
            (FRAME_WIDTH, scroll_center_y),
            (255, 255, 0),
            1,
        )

        mode = "None"
        action = None

        if len(lm_list) != 0:
            fingers = detector.fingersUp()

            # ---- MOVE: [*, 1, 0, 0, 0] ----
            if _match_pattern(fingers, [None, 1, 0, 0, 0]):
                # Release drag on mode switch
                if drag_active:
                    drag_active = False
                    action = "drag_end"

                mode = "Move"

                x1, y1 = lm_list[8][1], lm_list[8][2]
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
                cloc_x = ploc_x + (x3 - ploc_x) / SMOOTHING
                cloc_y = ploc_y + (y3 - ploc_y) / SMOOTHING
                ploc_x, ploc_y = cloc_x, cloc_y

                autopy.mouse.move(cloc_x, cloc_y)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            # ---- LEFT CLICK: [*, 1, 1, 0, 0] + pinch ----
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

            # ---- No recognized gesture ----
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

        # ---- Execute actions ----
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

        # ---- FPS ----
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

        # ---- Mode overlay ----
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
