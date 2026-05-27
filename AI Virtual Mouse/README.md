# AI Virtual Mouse

AI Virtual Mouse is a Python computer-vision project that controls the system mouse using hand gestures captured from a webcam. It uses OpenCV for video capture, MediaPipe Hands for hand landmark detection, NumPy for coordinate mapping, and AutoPy for operating-system mouse control.

> This repository currently contains the tutorial-compatible implementation in `video version/`.

## Features

- Real-time webcam hand tracking
- Cursor movement using the index finger
- Click detection using index-and-middle-finger pinch gesture
- Coordinate mapping from webcam frame to screen resolution
- Cursor smoothing to reduce jitter
- Visual feedback for tracking region, landmarks, and click state
- Safe handling for missing camera frames and no-hand frames

## Project Structure

```text
AI Virtual Mouse/
├── README.md
├── requirements.txt
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPMENT.md
└── video version/
    ├── AiVirtualMouseProject.py
    └── HandTrackingModule.py
```

## Technology Stack

| Area | Tool |
|---|---|
| Language | Python 3.11 recommended |
| Computer vision | OpenCV |
| Hand tracking | MediaPipe Hands |
| Coordinate mapping | NumPy |
| Mouse automation | AutoPy |

## Quick Start

From the `AI Virtual Mouse/` directory:

```bash
source .venv/Scripts/activate
python "video version/AiVirtualMouseProject.py"
```

If you have not created the virtual environment yet, follow [`docs/INSTALLATION.md`](docs/INSTALLATION.md).

## Gesture Summary

| Gesture | Action |
|---|---|
| Index finger up only | Move cursor |
| Index + middle finger up | Click mode |
| Index + middle fingertips close together | Left click |
| Press `q` in the OpenCV window | Exit application |

See [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for full operating instructions.

## Configuration

Main runtime constants are defined in `video version/AiVirtualMouseProject.py`:

```python
wCam, hCam = 640, 480
frameR = 100
smoothening = 7
cap = cv2.VideoCapture(0)
```

Common changes:

- Change camera index from `0` to `1` if the webcam does not open.
- Increase `smoothening` for smoother but slower cursor movement.
- Decrease click threshold `if length < 40:` if accidental clicks happen.

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Development Guide](docs/DEVELOPMENT.md)

## Known Limitations

- Works best with one visible hand.
- Requires a working webcam and good lighting.
- AutoPy may require additional OS permissions on some systems.
- Tutorial implementation is not packaged as a Python module yet.

## License

No license file is currently included. Add a license before distributing this project publicly.
