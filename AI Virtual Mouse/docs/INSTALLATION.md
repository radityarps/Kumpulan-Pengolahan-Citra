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

### 3. Install baseline dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Run the tutorial baseline

```bash
python "video version/AiVirtualMouseProject.py"
```

### 5. Create separate environment for improved version (modern API)

The improved version uses the latest MediaPipe with the Tasks API and newer dependencies. It should run in a separate virtual environment to avoid conflicts with the pinned baseline packages.

```bash
uv venv .venv-improved --python 3.11
source .venv-improved/Scripts/activate
uv pip install -r requirements-improved.txt
```

### 6. Run the experimental prototype

From the baseline environment (`.venv`):

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --help
PYTHONPATH=src python -m ai_virtual_mouse_experimental --list
```

From the improved environment (`.venv-improved`):

```bash
source .venv-improved/Scripts/activate
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
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

For the improved version:

```bash
python3.11 -m venv .venv-improved
source .venv-improved/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements-improved.txt
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
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

## Run the Modern Real Mouse Demo

After installing dependencies and optionally downloading the Tasks model:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Use `--condition baseline` to run the frozen video tutorial version instead.

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
