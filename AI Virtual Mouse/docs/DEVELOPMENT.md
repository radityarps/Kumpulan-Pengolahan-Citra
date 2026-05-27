# Development Guide

## Development Goals

This project is a learning-oriented computer vision application. Development should prioritize:

- clear code structure,
- reproducible setup,
- safe mouse-control behavior,
- explicit configuration,
- maintainable documentation.

## Local Environment

Use the project virtual environment:

```bash
source .venv/Scripts/activate
python --version
```

Recommended Python version: 3.11.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

```bash
python "video version/AiVirtualMouseProject.py"
```

Press `q` to exit.

## Code Overview

### Main Script

`video version/AiVirtualMouseProject.py`

Contains the runtime loop and gesture action logic.

### Hand Tracking Module

`video version/HandTrackingModule.py`

Contains MediaPipe integration and utility methods.

## Coding Standards

Recommended standards for future improvements:

- Keep camera, gesture, and mouse-control logic separated.
- Avoid hardcoded constants in the main loop.
- Use named parameters for third-party APIs.
- Validate camera frames before processing.
- Avoid triggering OS mouse events without a clear user gesture.
- Keep documentation updated when changing gestures or configuration.

## Suggested Refactor Roadmap

### Phase 1: Configuration Extraction

Move constants into a config file:

```python
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_REDUCTION = 100
SMOOTHING = 7
CLICK_THRESHOLD = 40
```

### Phase 2: Modular Runtime

Separate the current script into modules:

```text
src/
├── app.py
├── config.py
├── hand_tracking.py
├── gesture_classifier.py
├── coordinate_mapper.py
└── mouse_controller.py
```

### Phase 3: Testability

Add tests for pure logic:

- finger-state classification,
- coordinate interpolation,
- smoothing formula,
- click threshold behavior.

Avoid testing webcam and OS cursor movement directly in unit tests. Use mocks for those boundaries.

### Phase 4: Packaging

Add standard Python project files:

- `pyproject.toml`
- `src/` package layout
- CLI entry point
- automated linting and formatting

## Manual Test Checklist

Before considering a change stable, verify:

- [ ] App starts without import errors.
- [ ] Webcam window opens.
- [ ] No crash when no hand is visible.
- [ ] Index-only gesture moves cursor.
- [ ] Index + middle gesture enters click mode.
- [ ] Pinch gesture performs click.
- [ ] Pressing `q` exits cleanly.
- [ ] Camera resources are released after exit.

## Version Control Hygiene

Do not commit generated or local files:

- `.venv/`
- `__pycache__/`
- `.ruff_cache/`
- camera screenshots or recordings unless intentionally documented
- local IDE settings

## Documentation Maintenance

When changing behavior, update:

- `README.md` for high-level usage changes,
- `docs/USER_GUIDE.md` for gesture or operation changes,
- `docs/ARCHITECTURE.md` for design changes,
- `docs/TROUBLESHOOTING.md` for new common errors.
