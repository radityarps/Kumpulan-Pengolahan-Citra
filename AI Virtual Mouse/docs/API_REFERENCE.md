# API Reference

This document describes the public functions/classes in the current tutorial implementation.

## `HandTrackingModule.handDetector`

Wrapper around MediaPipe Hands.

### Constructor

```python
handDetector(mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5)
```

Parameters:

| Parameter | Type | Description |
|---|---:|---|
| `mode` | `bool` | Static image mode. `False` is recommended for webcam video. |
| `maxHands` | `int` | Maximum number of hands to detect. Main app uses `1`. |
| `detectionCon` | `float` | Minimum hand detection confidence. |
| `trackCon` | `float` | Minimum hand tracking confidence. |

### `findHands(img, draw=True)`

Detects hands in a BGR OpenCV frame.

Returns:

- `img`: the same frame, optionally annotated with hand landmarks.

Side effects:

- Stores MediaPipe results on `self.results` for later use by `findPosition()`.

### `findPosition(img, handNo=0, draw=True)`

Converts detected hand landmarks into pixel coordinates.

Returns:

```python
lmList, bbox
```

Where:

- `lmList` is a list of `[id, x, y]` landmarks.
- `bbox` is `(xmin, ymin, xmax, ymax)` when a hand is detected, otherwise an empty list.

### `fingersUp()`

Classifies whether each finger is raised.

Returns:

```python
[thumb, index, middle, ring, pinky]
```

Each value is either:

- `1`: finger is up,
- `0`: finger is down.

Precondition:

- `findPosition()` must have detected a hand before this method is called.

### `findDistance(p1, p2, img, draw=True, r=15, t=3)`

Calculates Euclidean distance between two landmarks.

Parameters:

| Parameter | Description |
|---|---|
| `p1` | First landmark ID |
| `p2` | Second landmark ID |
| `img` | OpenCV frame |
| `draw` | Whether to draw line/circles |
| `r` | Circle radius |
| `t` | Line thickness |

Returns:

```python
length, img, lineInfo
```

Where `lineInfo` is:

```python
[x1, y1, x2, y2, cx, cy]
```

## Landmark IDs Used by the App

| ID | Landmark |
|---:|---|
| 8 | Index fingertip |
| 12 | Middle fingertip |

## Main Script Runtime Variables

Defined in `AiVirtualMouseProject.py`:

| Variable | Purpose |
|---|---|
| `wCam`, `hCam` | Webcam capture size |
| `frameR` | Reduced tracking region margin |
| `smoothening` | Cursor smoothing factor |
| `pTime` | Previous frame timestamp |
| `plocX`, `plocY` | Previous cursor location |
| `clocX`, `clocY` | Current smoothed cursor location |
| `wScr`, `hScr` | Screen width and height |
