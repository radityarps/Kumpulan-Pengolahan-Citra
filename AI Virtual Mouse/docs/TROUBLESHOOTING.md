# Troubleshooting

## `bash: py: command not found`

You are likely using Git Bash and the Windows Python launcher is unavailable.

Use one of these instead:

```bash
python3.11 -m venv .venv
```

or use `uv`:

```bash
uv python install 3.11
uv venv .venv --python 3.11
```

## `Unknown option: -3`

This command is invalid:

```bash
python -3.11 -m venv .venv
```

Use:

```bash
python3.11 -m venv .venv
```

or:

```bash
uv venv .venv --python 3.11
```

## `AttributeError: module 'mediapipe' has no attribute 'solutions'`

Cause: incompatible MediaPipe package/API for the current Python environment.

Recommended fix:

```bash
uv venv .venv --python 3.11
source .venv/Scripts/activate
uv pip install -r requirements.txt
```

The project expects tutorial-compatible MediaPipe behavior.

## `TypeError: create_int(): incompatible function arguments ... Invoked with: 0.5`

Cause: old tutorial code passed `Hands()` arguments positionally. Modern MediaPipe interprets the arguments differently.

Fix: use named parameters in `HandTrackingModule.py`:

```python
self.hands = self.mpHands.Hands(
    static_image_mode=self.mode,
    max_num_hands=self.maxHands,
    min_detection_confidence=self.detectionCon,
    min_tracking_confidence=self.trackCon,
)
```

## Camera window opens but no frame appears

Try changing camera index in `video version/AiVirtualMouseProject.py`:

```python
cap = cv2.VideoCapture(0)
```

to:

```python
cap = cv2.VideoCapture(1)
```

Also check that no other app is currently using the webcam.

## `Camera frame could not be read. Check your camera index.`

Cause: OpenCV could not read from the selected camera.

Fixes:

1. Try camera index `0`, `1`, or `2`.
2. Close Zoom, Teams, browser camera tabs, or other camera apps.
3. Check Windows camera privacy settings.
4. Reconnect external webcam.

## Cursor is too shaky

Increase smoothing:

```python
smoothening = 10
```

If it becomes too slow, reduce it to `5` or `7`.

## Click happens accidentally

Reduce click threshold:

```python
if length < 30:
```

## Click is difficult to trigger

Increase click threshold:

```python
if length < 50:
```

## Hand is not detected reliably

Improve input conditions:

- Use brighter lighting.
- Place hand against a plain background.
- Keep palm facing the camera.
- Keep only one hand visible.
- Avoid motion blur from fast movements.

## How to stop the app

Press `q` while the OpenCV window is focused. If that does not work, return to the terminal and press `Ctrl+C`.
