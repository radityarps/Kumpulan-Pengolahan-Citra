"""Test fist and drag gesture detection reliability."""
import sys
sys.path.insert(0, 'video-version')
from HandTrackingModule import HandDetector  # noqa: E402
from AIVirtualMouse import _match_pattern  # noqa: E402

# Simulate realistic fist: all fingers curled
# Index tip (8) is BELOW index PIP (6) — finger curled down
d = HandDetector()
d.lmList = [
    [0, 300, 400],   # wrist
    [1, 310, 380],   # thumb CMC
    [2, 320, 350],   # thumb MCP
    [3, 330, 330],   # thumb IP
    [4, 280, 310],   # thumb TIP — x < IP x (280 < 330) → thumb 0 ✓
    [5, 280, 350],   # index MCP
    [6, 270, 300],   # index PIP
    [7, 260, 280],   # index DIP
    [8, 250, 340],   # index TIP — y > PIP y (340 > 300) → finger down (0) ✓
    [9, 300, 340],   # middle MCP
    [10, 300, 300],  # middle PIP
    [11, 310, 310],  # middle DIP
    [12, 320, 350],  # middle TIP — y > PIP y → down (0) ✓
    [13, 320, 340],  # ring MCP
    [14, 330, 300],  # ring PIP
    [15, 340, 310],  # ring DIP
    [16, 350, 360],  # ring TIP — y > PIP y → down (0) ✓
    [17, 340, 350],  # pinky MCP
    [18, 350, 310],  # pinky PIP
    [19, 360, 320],  # pinky DIP
    [20, 370, 370],  # pinky TIP — y > PIP y → down (0) ✓
]

fingers = d.fingersUp()
print(f"Realistic fist: {fingers}")
match = _match_pattern(fingers, [None, 0, 0, 0, 0])
print(f"Matches [*,0,0,0,0]: {match}")

# Edge case: thumb flipped
d.lmList[4][1] = 350  # thumb tip x > IP x (350 > 330) → thumb 1
fingers2 = d.fingersUp()
print(f"\nFist (thumb flipped): {fingers2}")
match2 = _match_pattern(fingers2, [None, 0, 0, 0, 0])
print(f"Still matches [*,0,0,0,0]: {match2} — should be True (thumb wildcard)")

# Semi-fist: index slightly up
d.lmList[4][1] = 280
d.lmList[8][2] = 290  # index tip y < PIP y → finger up (1)
fingers3 = d.fingersUp()
print(f"\nSemi-fist (index up): {fingers3}")
match3 = _match_pattern(fingers3, [None, 0, 0, 0, 0])
print(f"Matches [*,0,0,0,0]: {match3} — should be False")
