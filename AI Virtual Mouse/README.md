# AI Virtual Mouse

AI Virtual Mouse is a Python computer-vision project that controls the system mouse using hand gestures captured from a webcam. It uses OpenCV for video capture, MediaPipe Hands for hand landmark detection, NumPy for coordinate mapping, and AutoPy for operating-system mouse control.

> This repository currently contains the tutorial-compatible implementation in `video version/`.
> The first experimental research prototype skeleton lives in `src/` with configuration in `config/experimental.toml`.

## Features

- Real-time webcam hand tracking
- Cursor movement using the index finger
- Click detection using index-and-middle-finger pinch gesture
- Coordinate mapping from webcam frame to screen resolution
- Cursor smoothing to reduce jitter
- Visual feedback for tracking region, landmarks, and click state
- Safe handling for missing camera frames and no-hand frames
- Experimental benchmark modes with CSV logs, SVG plots, Markdown reports, and comparison reports

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
│   ├── BENCHMARK_METHODOLOGY.md
│   └── DEVELOPMENT.md
├── src/
│   └── ai_virtual_mouse_experimental/
├── config/
│   └── experimental.toml
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

### Two environments

The project uses **two virtual environments**:

- `.venv` — baseline/tutorial version (pinned `mediapipe==0.10.14`, older numpy)
- `.venv-improved` — modern improved version (`mediapipe>=0.10.30`, Tasks API, latest numpy)

Create both:

```bash
# Baseline
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# Improved
python -m venv .venv-improved
source .venv-improved/Scripts/activate
pip install -r requirements-improved.txt
```

## Experimental Prototype

Issue #3 adds a safe experimental app skeleton that validates configuration, selects modes and research conditions, and starts without controlling the real OS mouse by default.

Run from the project root:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --help
PYTHONPATH=src python -m ai_virtual_mouse_experimental --list
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode config --condition improved
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m ai_virtual_mouse_experimental --list
```

The default mode is `benchmark` with the `baseline` condition. Benchmark mode uses a simulated cursor and does not move the real OS mouse.

Run condition comparisons:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition improved
PYTHONPATH=src python -m ai_virtual_mouse_experimental --compare-sessions outputs/sessions/session-a outputs/sessions/session-b
```

### Real Mouse Runtime

The modern **Real Mouse Runtime** controls the actual OS cursor using your webcam and hand gestures. It uses MediaPipe Tasks as the primary backend and falls back to MediaPipe Solutions with a visible warning if Tasks cannot initialize.

Run the improved real mouse demo:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Run the frozen video baseline demo:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition baseline --allow-real-mouse
```

**Safety controls:**

- Press `q` in the camera window to exit.
- Hold open palm for ~0.3s to toggle pause/unpause.
- Move cursor to a screen corner and hold for ~0.8s to trigger pause.

The real mouse runtime includes an overlay showing active gesture, paused state, backend used, and FPS.

## Gesture Summary

| Gesture | Action |
|---|---|
| Index finger up only | Move cursor |
| Index + middle finger up | Click mode |
| Index + middle fingertips close together | Left click |
| Open palm hold | Toggle pause/unpause |
| Press `q` in the OpenCV window | Exit application |
| Hold cursor in corner | Pause failsafe |

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

Experimental runtime settings are defined in `config/experimental.toml`, including placeholders for backend, mode, condition, benchmark, gesture, and output settings.

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Benchmark Methodology](docs/BENCHMARK_METHODOLOGY.md)
- [Experimental Prototype PRD](docs/PRD_EXPERIMENTAL_RESEARCH_PROTOTYPE.md)

## Known Limitations

- Works best with one visible hand.
- Requires a working webcam and good lighting.
- AutoPy may require additional OS permissions on some systems.
- Tutorial implementation is not packaged as a Python module yet.

## License

No license file is currently included. Add a license before distributing this project publicly.
