# Real Mouse Gesture Guide

This guide covers the **modern improved Real Mouse Runtime** only. It uses the Simple Real Mouse Profile: move, stable pinch click, pause/resume, quit, and corner failsafe.

Drag and scroll are intentionally disabled in the real mouse runtime to reduce false positives while controlling the operating-system cursor.

## Start the Improved Runtime

From `AI Virtual Mouse/`:

```bash
source .venv-improved/Scripts/activate
PYTHONPATH=src python -m ai_virtual_mouse_experimental --download-model
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

If the backend fails before the camera opens, verify the model:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --smoke-backend
```

## Gesture Summary

| Gesture | Hand shape | Runtime action |
|---|---|---|
| Move | Index up only | Cursor follows index fingertip |
| Stable Pinch Click | Index + middle up, fingertips close together | Emits one left click after debounce |
| Pause Toggle | Open palm hold | Toggles paused/unpaused |
| Quit | Keyboard `q` | Exits runtime |
| Corner Failsafe | Cursor held near screen edge/corner | Pauses runtime automatically |

## Move Cursor

Raise only the index finger.

```text
Index:  up
Middle: down
Ring:   down
Pinky:  down
```

Expected behavior:

- Cursor follows the index fingertip.
- Overlay label shows `Move`.
- Cursor movement uses adaptive smoothing.
- If middle, ring, or pinky is also raised, the runtime should not treat it as move.

Tips:

- Keep palm facing the camera.
- Keep index fingertip inside the camera frame.
- Move slowly first, then speed up after tracking feels stable.

## Stable Pinch Click

Raise index and middle fingers, then bring the two fingertips close together.

```text
Index:  up
Middle: up
Ring:   down
Pinky:  down

Pinch target: index fingertip + middle fingertip
```

Expected behavior:

- One stable pinch emits one left click.
- Holding the pinch does not spam repeated clicks.
- Release the pinch for the configured release frames before clicking again.
- Overlay label shows `Click` when pinch is active.

Current defaults:

```toml
[gesture]
click_threshold_px = 40

[debounce]
stable_frames_required = 2
release_frames_required = 2
cooldown_seconds = 0.35
```

If click is too hard:

```toml
click_threshold_px = 55
stable_frames_required = 2
```

If false clicks happen:

```toml
click_threshold_px = 30
stable_frames_required = 3
cooldown_seconds = 0.45
```

## Pause and Resume

Hold an open palm steady for about 0.3 seconds.

```text
Index:  up
Middle: up
Ring:   up
Pinky:  up
Palm:   visible
```

Expected behavior:

- First hold toggles runtime to paused.
- Second hold toggles runtime back to unpaused.
- While paused, cursor movement and click actions are ignored.
- Overlay shows paused state.

Important:

- Keep palm steady until pause toggles.
- Release open palm before trying to toggle again.
- Thumb does not matter for pause detection.

## Quit Runtime

Press `q` while the camera window is focused.

Expected behavior:

- Camera window closes.
- Webcam is released.
- Runtime exits cleanly.

If `q` does not work, focus the OpenCV camera window first, then press `q` again. As last resort, return to terminal and press `Ctrl+C`.

## Corner Failsafe

Move the cursor to a screen edge or corner and hold it there for about 0.8 seconds.

Expected behavior:

- Runtime auto-pauses.
- Cursor movement and clicks stop.
- Use open-palm pause toggle to resume.

This is a safety control for unstable cursor movement.

## Disabled Gestures

These are implemented in the general improved gesture engine but intentionally not active in the real mouse runtime:

| Gesture | Status | Reason |
|---|---|---|
| Drag | Disabled | Reduces accidental drag while controlling OS cursor |
| Scroll | Disabled | Reduces false positive scrolling |

## Manual Smoke Test Checklist

Run this checklist before demo or benchmark recording:

1. Start improved runtime.
2. Confirm camera window opens and overlay appears.
3. Raise index only; cursor moves.
4. Raise index + middle; no click until fingertips pinch together.
5. Pinch index + middle fingertips; one left click fires.
6. Hold pinch; repeated clicks do not spam.
7. Release pinch, then pinch again; second click fires.
8. Hold open palm; runtime pauses.
9. Move hand while paused; cursor does not move.
10. Hold open palm again; runtime resumes.
11. Move cursor to screen edge/corner; runtime auto-pauses.
12. Press `q`; runtime exits cleanly.

## Troubleshooting

### Cursor does not move

Check:

- Only index finger is raised.
- Camera sees one hand clearly.
- Overlay shows `Move`.
- Runtime is not paused.

### Click does not fire

Check:

- Index and middle fingers are raised.
- Ring and pinky are down.
- Pinch is index fingertip to middle fingertip.
- Fingertips are closer than `click_threshold_px`.

### Click fires too often

Use stricter debounce:

```toml
click_threshold_px = 30
stable_frames_required = 3
cooldown_seconds = 0.45
```

### Pause does not toggle

Check:

- Index, middle, ring, and pinky are all raised.
- Palm is facing camera.
- Open palm is held steady for about 0.3 seconds.
- Hand is released before trying second toggle.

### Backend fails before camera opens

Download and smoke-test the Tasks model:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --download-model
PYTHONPATH=src python -m ai_virtual_mouse_experimental --smoke-backend
```
