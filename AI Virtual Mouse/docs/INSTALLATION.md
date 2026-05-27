# Installation Guide

This guide sets up the project without downgrading your system Python. Use a project-specific virtual environment with Python 3.11.

## Requirements

- Windows 10/11
- Webcam
- Git Bash, PowerShell, or Command Prompt
- Python 3.11 available through either:
  - normal side-by-side Python installation, or
  - `uv` managed Python installation

## Recommended Setup with `uv`

`uv` can download Python 3.11 without replacing your existing Python installation.

### 1. Install `uv`

In PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart Git Bash or your terminal after installation.

### 2. Install Python 3.11 for this project

From the `AI Virtual Mouse/` directory:

```bash
uv python install 3.11
uv venv .venv --python 3.11
source .venv/Scripts/activate
python --version
```

Expected output should be Python 3.11.x.

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Run the tutorial baseline

```bash
python "video version/AiVirtualMouseProject.py"
```

### 5. Run the experimental prototype

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --help
PYTHONPATH=src python -m ai_virtual_mouse_experimental --list
```

The experimental benchmark uses Pygame. If benchmark mode reports that Pygame is missing, reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Alternative Setup with Installed Python 3.11

If Python 3.11 is already installed and available as `python3.11`:

```bash
python3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python "video version/AiVirtualMouseProject.py"
```

## Verify Installation

Run:

```bash
python - <<'PY'
import cv2
import mediapipe
import numpy
import autopy
import pygame
print('OpenCV:', cv2.__version__)
print('MediaPipe:', mediapipe.__version__)
print('NumPy:', numpy.__version__)
print('AutoPy: OK')
print('Pygame:', pygame.version.ver)
PY
```

## MediaPipe Tasks Model Download

The improved backend uses MediaPipe Tasks HandLandmarker metadata. Download the model with:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --download-model
```

Verify backend initialization with:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --smoke-backend
```

## Notes

- Python 3.13 is not recommended for this tutorial implementation because MediaPipe compatibility differs.
- The project virtual environment does not affect your system Python.
- Keep `.venv/` out of version control.
