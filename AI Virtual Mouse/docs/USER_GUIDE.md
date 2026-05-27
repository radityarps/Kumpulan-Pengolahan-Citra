# User Guide

This guide explains how to operate the AI Virtual Mouse application.

## Start the Application

From the `AI Virtual Mouse/` directory:

```bash
source .venv/Scripts/activate
python "video version/AiVirtualMouseProject.py"
```

An OpenCV window named `Image` should appear and show the webcam feed.

## Hand Positioning

For best results:

- Face your palm toward the webcam.
- Keep one hand visible.
- Use good lighting.
- Keep your fingers inside the purple rectangle.
- Move slowly until tracking feels stable.

## Gestures

### Move Cursor

Raise only the index finger.

```text
Index finger: up
Middle finger: down
```

The cursor follows the index fingertip. The purple circle indicates movement mode.

### Click

Raise the index and middle fingers together.

```text
Index finger: up
Middle finger: up
```

Then bring both fingertips close together. When the distance is below the configured threshold, the application performs a left click.

### Stop Moving

Lower the index finger or move your hand out of the camera frame.

### Exit

Press `q` while the OpenCV window is focused.

## Tuning Behavior

Edit `video version/AiVirtualMouseProject.py`.

### Camera Resolution

```python
wCam, hCam = 640, 480
```

Higher resolution may improve precision but can reduce performance.

### Tracking Region

```python
frameR = 100
```

This creates a margin around the camera frame. The cursor maps only from inside the purple rectangle to the full screen.

### Cursor Smoothing

```python
smoothening = 7
```

- Higher value: smoother but slower cursor.
- Lower value: faster but more jittery cursor.

### Click Sensitivity

```python
if length < 40:
```

- Lower value: click requires fingertips to be closer.
- Higher value: click triggers more easily.

## Safety Notes

Because the script controls the real system cursor, keep a physical mouse or touchpad available while testing. Use `q` to exit, or close the terminal if the pointer becomes difficult to control.
