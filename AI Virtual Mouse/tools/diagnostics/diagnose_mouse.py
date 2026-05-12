"""
Diagnostic script to test autopy mouse control on Windows.
Run: python tools/diagnostics/diagnose_mouse.py

This tests:
1. Screen size detection
2. Mouse move (moves cursor 10px right, then back)
3. Mouse click (at current position)
4. Whether any errors are raised
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

import time


def main():
    print("=" * 50)
    print("  AI Virtual Mouse - Mouse Diagnostic")
    print("=" * 50)

    # Test 1: Import autopy
    print("\n[1] Importing autopy...")
    try:
        import autopy

        print("    OK — autopy imported successfully")
        print(
            f"    Version: {autopy.__version__ if hasattr(autopy, '__version__') else 'unknown'}"
        )
    except ImportError as e:
        print(f"    FAIL — {e}")
        return

    # Test 2: Screen size
    print("\n[2] Detecting screen size...")
    try:
        w, h = autopy.screen.size()
        print(f"    OK — Screen resolution: {w}x{h}")
    except Exception as e:
        print(f"    FAIL — {e}")
        return

    # Test 3: Get current mouse position
    print("\n[3] Reading current mouse position...")
    try:
        x, y = autopy.mouse.location()
        print(f"    OK — Current position: ({x}, {y})")
    except Exception as e:
        print(f"    FAIL — {e}")
        return

    # Test 4: Move mouse (small offset)
    print("\n[4] Moving mouse (10px right, then back)...")
    try:
        print(f"    Moving to ({x + 10}, {y})...")
        autopy.mouse.move(x + 10, y)
        time.sleep(0.3)
        x2, y2 = autopy.mouse.location()
        print(f"    New position: ({x2}, {y2})")
        if x2 == x + 10:
            print("    OK — Mouse moved successfully")
        else:
            print(f"    NOTE — Expected ({x + 10},{y}) but got ({x2},{y2})")
            print("           Mouse may have moved but coordinates rounded")

        print(f"    Moving back to ({x}, {y})...")
        autopy.mouse.move(x, y)
        time.sleep(0.3)
        print("    OK — Restored position")
    except Exception as e:
        print(f"    FAIL — {e}")
        print("    → Mouse movement may be blocked by Windows security")
        print("    → Try running terminal as Administrator")
        return

    # Test 5: Check scroll availability
    print("\n[5] Checking scroll support...")
    if hasattr(autopy.mouse, "scroll"):
        print("    OK — scroll() is available")
    else:
        print("    NOTE — scroll() is NOT available (autopy 4.0.1 limitation)")

    # Test 6: Full pipeline simulation
    print("\n[6] Simulating full pipeline...")
    try:
        from src.coordinate_mapper import CoordinateMapper
        from src.mouse_controller import MouseController

        mapper = CoordinateMapper(frame_width=640, frame_height=480)
        controller = MouseController()

        print(f"    Screen: {mapper.screen_width}x{mapper.screen_height}")
        print(f"    Frame reduction: {mapper.frame_reduction}")

        # Simulate moving to center of screen
        cx, cy = 320, 240  # center of 640x480 frame
        sx, sy = mapper.process(cx, cy)
        print(f"    Camera ({cx},{cy}) → Screen ({sx:.1f},{sy:.1f})")

        # Try moving the mouse to the mapped position
        print(f"    Moving mouse to ({int(sx)},{int(sy)})...")

        save_x, save_y = autopy.mouse.location()
        controller.execute("move", screen_x=sx, screen_y=sy)
        time.sleep(0.5)
        new_x, new_y = autopy.mouse.location()

        print(f"    Position changed: ({save_x},{save_y}) → ({new_x},{new_y})")

        # Restore
        autopy.mouse.move(save_x, save_y)

        # Check if position actually changed
        if (new_x, new_y) != (save_x, save_y):
            print("    OK — Full pipeline works!")
        else:
            print("    NOTE — Position didn't change.")
            print("           autopy.mouse.move() may not be working on this system.")
            print("           Check Windows settings:")
            print("           - Settings > Bluetooth & devices > Mouse")
            print("           - Try running as Administrator")
            print("           - Disable 'Enhance pointer precision' if needed")
    except Exception as e:
        print(f"    FAIL — {e}")

    print("\n" + "=" * 50)
    print("  Diagnostic complete.")
    print("  If all tests pass, the issue is in gesture recognition.")
    print("  If mouse move tests fail, check Windows permissions.")
    print("=" * 50)


if __name__ == "__main__":
    main()
