"""Quick smoke test for video-version HandTrackingModule."""
import sys
sys.path.insert(0, 'video-version')
from HandTrackingModule import HandDetector  # noqa: E402

d = HandDetector()

# Mock hand: palm facing camera, fingers up
# Format: [id, x, y]
# Thumb extended (tip x > IP x), index up (tip y < PIP y), others down
d.lmList = [
    [0, 300, 400],   # wrist
    [1, 320, 380],   # thumb CMC
    [2, 340, 350],   # thumb MCP
    [3, 350, 330],   # thumb IP
    [4, 400, 310],   # thumb TIP — x > IP x → thumb up
    [5, 280, 350],   # index MCP
    [6, 270, 300],   # index PIP  (tip_id - 2 = lmList[6])
    [7, 260, 260],   # index DIP
    [8, 250, 220],   # index TIP — y < PIP y → up
    [9, 300, 340],   # middle MCP
    [10, 300, 300],  # middle PIP
    [11, 300, 280],  # middle DIP
    [12, 300, 320],  # middle TIP — y > PIP y → down
    [13, 320, 340],  # ring MCP
    [14, 330, 300],  # ring PIP
    [15, 340, 320],  # ring DIP
    [16, 350, 350],  # ring TIP — y > PIP y → down
    [17, 340, 350],  # pinky MCP
    [18, 350, 310],  # pinky PIP
    [19, 360, 300],  # pinky DIP
    [20, 370, 320],  # pinky TIP — y > PIP y → down
]

result = d.fingersUp()
print(f"fingersUp: {result}")
print("Expected:  [1, 1, 0, 0, 0]  (thumb up, index up, others down)")
assert result == [1, 1, 0, 0, 0], f"FAIL: got {result}"

# Test findDistance
length, _, info = d.findDistance(8, 12, draw=False)
print(f"index-middle distance: {length:.1f}")

# Test thumb-folded: tip x < IP x → thumb down
d.lmList[4][1] = 300  # thumb tip x < IP (350) → thumb down
result2 = d.fingersUp()
print(f"fingersUp (thumb folded): {result2}")
print("Expected:                 [0, 1, 0, 0, 0]")
assert result2 == [0, 1, 0, 0, 0], f"FAIL: got {result2}"

# Test all fingers down
d.lmList[8][2] = 400   # index tip y > PIP y → down
d.lmList[12][2] = 300  # middle stays down
result3 = d.fingersUp()
print(f"fingersUp (all down): {result3}")
print("Expected:            [0, 0, 0, 0, 0]")
assert result3 == [0, 0, 0, 0, 0], f"FAIL: got {result3}"

# Test all fingers up
d.lmList[4][1] = 400   # thumb up
d.lmList[8][2] = 220   # index up
d.lmList[12][2] = 240  # middle up
d.lmList[16][2] = 250  # ring up
d.lmList[20][2] = 260  # pinky up
result4 = d.fingersUp()
print(f"fingersUp (all up): {result4}")
print("Expected:          [1, 1, 1, 1, 1]")

print("\nAll tests PASSED!")
