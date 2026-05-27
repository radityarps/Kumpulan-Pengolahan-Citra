# Architecture

## Overview

AI Virtual Mouse converts webcam hand gestures into mouse actions.

```text
Webcam frame
    ↓
OpenCV capture
    ↓
MediaPipe hand landmark detection
    ↓
HandTrackingModule landmark utilities
    ↓
Gesture rules
    ↓
Coordinate mapping + smoothing
    ↓
AutoPy mouse movement/click
```

## Runtime Components

### `video version/AiVirtualMouseProject.py`

Main application loop.

Responsibilities:

- Configure webcam resolution.
- Read frames from OpenCV.
- Call hand detection utilities.
- Determine active gesture state.
- Map finger coordinates to screen coordinates.
- Smooth pointer movement.
- Trigger mouse movement and click events.
- Render visual debugging feedback.

Key settings:

```python
wCam, hCam = 640, 480
frameR = 100
smoothening = 7
cap = cv2.VideoCapture(0)
```

### `video version/HandTrackingModule.py`

Wrapper around MediaPipe Hands.

Responsibilities:

- Initialize MediaPipe Hands.
- Detect hand landmarks.
- Convert normalized landmarks into pixel coordinates.
- Return landmark list and hand bounding box.
- Classify raised fingers.
- Calculate distance between two landmarks.

Important landmark IDs:

| Landmark ID | Meaning |
|---|---|
| 4 | Thumb tip |
| 8 | Index finger tip |
| 12 | Middle finger tip |
| 16 | Ring finger tip |
| 20 | Pinky finger tip |

## Gesture State Machine

```text
No hand detected
    → no mouse action

Index up + middle down
    → movement mode

Index up + middle up
    → click mode
        → if distance(index tip, middle tip) < threshold
            → left click
```

## Coordinate Mapping

The webcam coordinate space is smaller than the screen coordinate space. The application uses NumPy interpolation:

```python
x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
```

The x-axis is flipped so the cursor moves naturally from the user's perspective:

```python
autopy.mouse.move(wScr - clocX, clocY)
```

## Smoothing

Pointer movement is smoothed using a weighted step from previous location to target location:

```python
clocX = plocX + (x3 - plocX) / smoothening
clocY = plocY + (y3 - plocY) / smoothening
```

This reduces jitter from frame-to-frame landmark noise.

## External Dependencies

| Dependency | Purpose |
|---|---|
| `opencv-python` | Webcam capture and visualization |
| `mediapipe` | Hand landmark detection |
| `numpy` | Coordinate interpolation |
| `autopy` | Mouse control |

## Current Architectural Limitations

- Main application is script-based, not packaged as a reusable module.
- Configuration values are hardcoded.
- No automated tests are currently included for the `video version/` implementation.
- Gesture classification is heuristic and may vary by lighting, camera angle, and hand orientation.
