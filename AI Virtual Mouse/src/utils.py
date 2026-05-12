"""
AI Virtual Mouse — Utility Functions
FPS counter, mode overlay text, and frame decoration helpers.
"""

import cv2

from src.config import (
    FONT,
    FONT_PLAIN,
    FPS_POS,
    MODE_POS,
    COLOR_GREEN,
    COLOR_WHITE,
    MODE_COLORS,
)


def put_fps(
    img, fps, pos=FPS_POS, font=FONT, scale=1.0, color=COLOR_GREEN, thickness=2
):
    """
    Overlay FPS counter on the frame.

    Args:
        img (numpy.ndarray): Frame to draw on.
        fps (int): Current frames per second value.
        pos (tuple[int, int]): (x, y) top-left corner of text.
        font (int): OpenCV font face.
        scale (float): Font scale factor.
        color (tuple[int, int, int]): BGR color tuple.
        thickness (int): Line thickness.
    """
    cv2.putText(img, f"FPS: {int(fps)}", pos, font, scale, color, thickness)


def put_mode_text(img, mode, pos=MODE_POS, font=FONT_PLAIN, scale=2.0, thickness=2):
    """
    Overlay current gesture mode on the frame with mode-specific color.

    Args:
        img (numpy.ndarray): Frame to draw on.
        mode (str): One of 'None', 'Move', 'Click', 'RightClick', 'Drag', 'Scroll'.
        pos (tuple[int, int]): (x, y) top-left corner of text.
        font (int): OpenCV font face.
        scale (float): Font scale factor.
        thickness (int): Line thickness.
    """
    color = MODE_COLORS.get(mode, COLOR_WHITE)
    cv2.putText(img, f"Mode: {mode}", pos, font, scale, color, thickness)


def put_bounding_box(img, bbox, color=COLOR_GREEN, thickness=2):
    """
    Draw a bounding box rectangle on the frame.

    Args:
        img (numpy.ndarray): Frame to draw on.
        bbox (tuple[int, int, int, int]): (x_min, y_min, x_max, y_max).
        color (tuple[int, int, int]): BGR color tuple.
        thickness (int): Line thickness.
    """
    x_min, y_min, x_max, y_max = bbox
    if x_max > 0 and y_max > 0:
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, thickness)


def put_status_text(
    img, text, pos, font=FONT, scale=0.6, color=COLOR_WHITE, thickness=1
):
    """
    Generic text overlay helper for debug info.

    Args:
        img (numpy.ndarray): Frame to draw on.
        text (str): Text to display.
        pos (tuple[int, int]): (x, y) top-left corner.
        font (int): OpenCV font face.
        scale (float): Font scale factor.
        color (tuple[int, int, int]): BGR color tuple.
        thickness (int): Line thickness.
    """
    cv2.putText(img, text, pos, font, scale, color, thickness)
