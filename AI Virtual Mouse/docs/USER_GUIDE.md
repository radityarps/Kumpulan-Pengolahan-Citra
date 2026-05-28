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

## Real Mouse Runtime

The modern Real Mouse Runtime uses your webcam to control the actual OS cursor. It supports the **Simple Real Mouse Profile**: move, stable pinch click, and pause toggle. Drag and scroll are not enabled in the first real mouse program.

For detailed hand shapes, tuning values, and a smoke-test checklist, see [`REAL_MOUSE_GESTURE_GUIDE.md`](REAL_MOUSE_GESTURE_GUIDE.md).

Run the improved real mouse demo:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Run the frozen video baseline demo:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition baseline --allow-real-mouse
```

The runtime uses MediaPipe Tasks as the primary backend. If Tasks fails to initialize, it falls back to MediaPipe Solutions and displays a warning in the overlay.

### Real Mouse Gestures

- **Move**: raise only the index finger. The cursor follows the index fingertip.
- **Click**: raise index and middle fingers, then bring fingertips close together. One stable pinch emits one left click.
- **Pause**: hold an open palm for about 0.3 seconds to toggle paused/unpaused. While paused, cursor movement and clicks are ignored.

### Safety Controls

- Press `q` in the camera window to exit immediately.
- Hold open palm to toggle pause.
- Move the cursor to a screen corner and hold for about 0.8 seconds to trigger the corner failsafe, which pauses the runtime.

The overlay shows active gesture, pause state, backend used, and FPS.

### Real Mouse Smoke Test Checklist

Before trusting the real mouse runtime for a demo, verify each behavior manually:

1. **Startup**: run `PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse`. The camera window opens and the overlay appears.
2. **Move**: raise only the index finger. The OS cursor follows the index fingertip.
3. **Stable Pinch Click**: raise index and middle fingers, then bring fingertips close together. One left click happens. Releasing and re-pinching emits another click after the configured debounce frames.
4. **Pause Toggle**: hold an open palm steady for about 0.3 seconds. The overlay shows "Paused". Cursor movement and clicks stop. Hold open palm again to resume.
5. **Quit**: press `q` while the camera window is focused. The app exits cleanly.
6. **Corner Failsafe**: while unpaused, move the cursor to a screen corner and hold it there for about 0.8 seconds. The runtime should pause automatically.
7. **Backend Fallback**: if the Tasks model is missing, the overlay should show a fallback warning and the runtime should continue using the Solutions backend.

## Experimental Prototype Modes

Run from `AI Virtual Mouse/`:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --list
```

Available benchmark conditions:

- `baseline`: frozen tutorial behavior.
- `smoothing_only`: adaptive smoothing ablation.
- `debounce_only`: click debouncing ablation.
- `calibration_only`: calibrated mapping ablation.
- `improved`: full improved condition.

Run the same benchmark with a selected condition:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition improved
```

Benchmark mode uses a simulated cursor inside Pygame and does not move the OS mouse. Use arrow keys/WASD to move the placeholder cursor and Space/left click to click targets.

### Hand-Driven Benchmark

To use webcam hand gestures instead of keyboard controls:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline --hand-input
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition improved --hand-input
```

The simulated cursor follows your hand gestures. The OS mouse is never moved during benchmark evaluation. Keyboard controls remain available as fallback.

## Benchmark Outputs

Each benchmark session creates:

- `metadata.json`
- `trials.csv`
- `completion_times.svg`
- `report.md`

Compare saved sessions:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --compare-sessions outputs/sessions/session-a outputs/sessions/session-b
```

## Safety Notes

Because the tutorial demo controls the real system cursor, keep a physical mouse or touchpad available while testing. Benchmark mode is safer because it uses a simulated cursor. Use `q` or Escape to exit benchmark windows.
