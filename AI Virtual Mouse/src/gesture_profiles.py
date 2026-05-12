"""
Gesture profile definitions.

This module centralizes finger-pattern mappings so gesture behavior can be
switched without rewriting the classifier core logic.
"""

GESTURE_PROFILES = {
    # Default project behavior
    "legacy": {
        "move_patterns": ([0, 1, 1, 0, 0],),
        "stop_pattern": [1, 1, 1, 0, 0],
        "click_pattern": [1, 0, 1, 0, 0],
        "right_click_pattern": [1, 1, 0, 0, 0],
        "drag_pattern": [0, 0, 0, 0, 0],
        "scroll_pattern": [1, 1, 1, 1, 1],
        "brightness_pattern": [1, 1, 1, 1, 0],
    },
}


def get_profile(style_name):
    """Return gesture profile by name, falling back to legacy."""
    return GESTURE_PROFILES.get(style_name, GESTURE_PROFILES["legacy"])
