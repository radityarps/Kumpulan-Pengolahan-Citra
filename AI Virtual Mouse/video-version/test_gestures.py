"""Test gesture mapping logic for video-version (main project gestures)."""
import sys
sys.path.insert(0, 'video-version')
from AIVirtualMouse import _match_pattern
from HandTrackingModule import HandDetector

# Test pattern matching with None wildcard (thumb ignored)
assert _match_pattern([0, 1, 0, 0, 0], [None, 1, 0, 0, 0]) == True
assert _match_pattern([1, 1, 0, 0, 0], [None, 1, 0, 0, 0]) == True  # thumb doesn't matter
assert _match_pattern([0, 0, 0, 0, 0], [None, 1, 0, 0, 0]) == False
assert _match_pattern([1, 1, 1, 0, 0], [None, 1, 1, 0, 0]) == True
assert _match_pattern([0, 1, 1, 1, 0], [None, 1, 1, 1, 0]) == True
assert _match_pattern([1, 0, 0, 0, 0], [None, 0, 0, 0, 0]) == True  # fist
assert _match_pattern([0, 1, 1, 1, 1], [None, 1, 1, 1, 1]) == True  # scroll
print("Match pattern: OK")

# Test HandDetector import
d = HandDetector(max_hands=1)
assert d.tip_ids == [4, 8, 12, 16, 20]
print("HandDetector: OK")

print("\nAll gesture matching tests PASSED!")
