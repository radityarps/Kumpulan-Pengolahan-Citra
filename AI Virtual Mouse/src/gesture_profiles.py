"""
Gesture profile definitions.

This module centralizes finger-pattern mappings so gesture behavior can be
switched without rewriting the classifier core logic.

╔══════════════════════════════════════════════════════════════════════╗
║  MASALAH #3 / Slide 7: Jempol Diabaikan (None Wildcard)
╠══════════════════════════════════════════════════════════════════════╣
║  Setiap profile menggunakan None sebagai wildcard untuk jempol.
║  Contoh: [None, 1, 1, 0, 0] artinya "jempol diabaikan, telunjuk
║  dan tengah naik, manis dan kelingking turun".
║
║  Ini MITIGASI, bukan solusi sempurna. Deteksi jempol secara
║  akurat butuh handedness detection (tangan kiri vs kanan) yang
║  memerlukan model tambahan. Untuk 6 gesture yang diimplementasi,
║  mengabaikan jempol = trade-off yang acceptable.
║
║  Profile "practical_no_thumb": semua pattern pakai None di jempol.
║  Profile "legacy": jempol disertakan (0 atau 1) — untuk referensi
║    kompatibilitas dengan tutorial asli.
╚══════════════════════════════════════════════════════════════════════╝

Each profile defines the finger patterns for Move, Click, Right Click,
Drag, Scroll, and Stop. Patterns use None as wildcard to ignore
unreliable finger detections (typically the thumb).

Available profiles:
    - "legacy": Original tutorial patterns (thumb included).
    - "practical_no_thumb": Thumb ignored in all patterns.
      Better reliability because thumb detection is handedness-dependent.

Usage:
    Set GESTURE_STYLE in config.py to choose a profile.
    Classifier reads the profile via get_profile() at init time.

To add a new profile:
    1. Add an entry to GESTURE_PROFILES dict below.
    2. Set GESTURE_STYLE = "your_profile_name" in config.py.
    3. No changes needed in gesture_classifier.py.
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
    },
    # Practical profile for noisy/low-light webcams:
    # thumb is ignored (None wildcard) to avoid unstable thumb detection.
    "practical_no_thumb": {
        "move_patterns": ([None, 1, 0, 0, 0],),
        "stop_pattern": None,
        "click_pattern": [None, 1, 1, 0, 0],  # index+middle pinch
        "right_click_pattern": [None, 1, 1, 1, 0],  # index+ring pinch
        "drag_pattern": [None, 0, 0, 0, 0],  # fist drag mode
        "scroll_pattern": [None, 1, 1, 1, 1],
    },
}


def get_profile(style_name):
    """
    Return gesture profile dictionary by name.

    Falls back to "legacy" profile if the requested style_name
    is not found in GESTURE_PROFILES.

    Args:
        style_name (str): Profile name key in GESTURE_PROFILES.
            Expected: "legacy" or "practical_no_thumb".

    Returns:
        dict: Gesture profile with keys:
            - move_patterns: tuple of acceptable finger patterns for Move.
            - stop_pattern: pattern that forces None mode (or None).
            - click_pattern: pattern for Left Click mode.
            - right_click_pattern: pattern for Right Click mode.
            - drag_pattern: pattern for Drag mode.
            - scroll_pattern: pattern for Scroll mode.
    """
    return GESTURE_PROFILES.get(style_name, GESTURE_PROFILES["legacy"])
