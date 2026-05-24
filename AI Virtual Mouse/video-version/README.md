# AI Virtual Mouse — Video Version

Reference implementation with simple flat-structure code. Same gesture mapping as the main
project, simpler implementation (no hysteresis, no debounce, no hold-time gating).

## Purpose

Side-by-side comparison with the **main project** (`../src/`). Useful for understanding what
the main project's GestureClassifier, CoordinateMapper, and config.py add on top of a basic
single-loop implementation.

## Files

```
video-version/
├── AIVirtualMouse.py       # Main loop — all gesture logic + mouse control
├── HandTrackingModule.py   # HandDetector wrapping MediaPipe Tasks API
├── config.py               # All tunable constants
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── test_smoke.py           # HandDetector unit tests (fingersUp, findDistance)
├── test_gestures.py        # Pattern matching tests (all 5 gestures)
└── test_drag.py            # Fist detection reliability tests
```

## Requirements

MediaPipe Tasks API model file must exist at `../src/hand_landmarker.task` (already present in
main project). Same `pip install -r requirements.txt` as main project.

## Usage

```bash
# Run
python video-version/AIVirtualMouse.py

# Tests
python video-version/test_smoke.py      # HandDetector unit tests
python video-version/test_gestures.py   # Gesture pattern matching
python video-version/test_drag.py       # Fist detection edge cases
```

## Gesture Reference

| Gesture | Finger Pattern | Action | Threshold |
|---|---|---|---|
| Move | `[*,1,0,0,0]` | Cursor follows index finger | — |
| Left Click | `[*,1,1,0,0]` | Single left click (edge-triggered) | Index-middle < 28px |
| Right Click | `[*,1,1,1,0]` | Single right click (edge-triggered) | Index-ring < 34px |
| Drag | `[*,0,0,0,0]` fist | Hold left button, move cursor | — |
| Scroll | `[*,1,1,1,1]` | Scroll up (hand high) / down (hand low) | ±35px dead zone around center |

`*` = thumb value ignored. Drag releases on any other gesture or hand loss.

## Architecture

```
[Webcam] → cv2.flip → HandDetector.findHands() → findPosition()
    → fingersUp() → _match_pattern() → gesture block
    → np.interp / smoothing → autopy.mouse.move() / click() / toggle()
```

Single-loop, no state machine. Each gesture is an independent if-elif block. Drag uses
anchor-based relative movement. Scroll uses `ctypes.windll.user32.mouse_event` for the
mouse wheel (Windows only — autopy 4.0.1 lacks `mouse.scroll()`).

## Key Differences from Main Project

| Aspect | Video Version | Main Project |
|---|---|---|
| MediaPipe API | Tasks API | Tasks API |
| Thumb detection | x-coordinate (handedness-dependent) | Distance-based MCP→tip |
| Camera mirror | `cv2.flip(img, 1)` + direct coords | `cv2.flip(img, 1)` + direct coords |
| Click mechanism | Simple threshold + edge-trigger | Hysteresis ON/OFF + hold-time gating |
| Drag | Anchor-based, no debounce | Anchor + debounce + hand-lost grace |
| Scroll backend | ctypes `mouse_event` (Windows) | autopy.mouse.scroll (unavailable → skipped) |
| Debounce | None | 300ms per mode switch |
| Post-click freeze | None | 200ms cursor freeze |
| Gesture profiles | Hardcoded (practical_no_thumb) | Profile system with multiple styles |
| Structure | 1 main file + 1 module | 8 modules + tests + docs |
| Tests | 3 smoke/unit test files | 33 unit tests + benchmark |

## Known Limitations

1. **No debounce** — Single-frame gesture flickers trigger mode switches. Drag drops on the
   first frame a finger extends. Slightly relaxing a fist mid-drag = item dropped.

2. **Handedness-dependent thumb** — x-coordinate thumb detection only works for right hand
   facing the camera. Left hand or rotated hand gives unreliable thumb state. Mitigated by
   ignoring thumb (`*` wildcard) in all gesture patterns.

3. **Curled-finger tracking** — Drag tracks a curled index fingertip (landmark 8). MediaPipe
   tracks extended fingers more accurately than curled ones. Expect jitter during drag.

4. **Scroll Windows-only** — `ctypes.windll` fallback only works on Windows. On other OS,
   scroll is silently ignored unless autopy build exposes `mouse.scroll()`.

5. **No hand-lost tolerance** — One frame without hand detection immediately resets all state
   (drops drag, resets click lock, clears scroll timer).

6. **Tasks API not Solutions API** — The legacy `mp.solutions.hands` was removed from all
   available mediapipe versions (0.10.30+). Uses Tasks API internally with identical public
   interface.
