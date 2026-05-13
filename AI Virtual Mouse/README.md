# AI Virtual Mouse — Real-Time Hand Gesture-Based Cursor Control

**Touchless cursor control** using hand gestures detected via OpenCV and MediaPipe. Move, click, right-click, drag, and scroll — no mouse required.

Proyek ini mengimplementasikan video tutorial dari kanal **Murtaza's Workshop — Robotics and AI** ([YouTube](https://youtu.be/8gPONnGIPgw)).

---

## 📁 Project Structure

```text
AI Virtual Mouse/
├── README.md                          ← This file
├── requirements.txt                   ← Python dependencies
├── article/                           ← Scientific article (IEEE format)
│   ├── 00_structure.md                ← Article outline
│   └── 01_draft.md                    ← Full article draft with experiments
├── literature/                        ← Literature review & references
│   ├── 00_literature_review.md        ← Curated literature review
│   ├── papers/                        ← Referenced PDF papers
│   └── bibtex/                        ← BibTeX reference files
│       └── references.bib
├── docs/                              ← Project documentation
│   ├── PRD.md                         ← Product Requirements Document
│   ├── implementation_plan.md         ← Phased implementation plan
│   └── project_research.md            ← Research notes
├── src/                               ← Source code
│   ├── ai_virtual_mouse.py            ← Main entry point (run this)
│   ├── config.py                      ← All tunable constants & thresholds
│   ├── hand_tracking_module.py        ← MediaPipe HandLandmarker wrapper
│   ├── gesture_classifier.py          ← Rule-based gesture classification
│   ├── gesture_profiles.py            ← Gesture pattern profile map
│   ├── coordinate_mapper.py           ← Camera-to-screen mapping + smoothing
│   ├── mouse_controller.py            ← Autopy mouse control wrapper
│   ├── utils.py                       ← FPS counter & overlay helpers
│   └── hand_landmarker.task           ← MediaPipe model file
├── tests/                             ← Automated tests
│   ├── test_smoke.py                  ← Smoke / integration test
│   ├── test_phase6.py                 ← Main unit test suite
│   └── test_benchmark.py              ← FPS benchmark
└── tools/                             ← Diagnostics and tuning utilities
    ├── diagnostics/
    └── tuning/
```

---

## 🚀 Features

| Gesture | Finger Pattern `[thumb,index,middle,ring,pinky]` | Action |
| --- | --- | --- |
| **Move** | `[*,1,0,0,0]` | Cursor movement |
| **Left Click** | `[*,1,1,0,0]` + index-middle pinch | Single left click |
| **Right Click** | `[*,1,1,1,0]` + index-ring pinch | Single right click |
| **Drag** | `[*,0,0,0,0]` | Hold left mouse button and move |
| **Scroll** | `[*,1,1,1,1]` | Up/down scroll using camera center boundary |

**Key capabilities:**

- Real-time 21-landmark hand detection via MediaPipe Tasks API (HandLandmarker)
- Rule-based gesture classifier — no ML training required, works out-of-box
- Exponential smoothing with optimized factor (5.0) for jitter-free cursor
- Practical no-thumb profile with pinch hysteresis and hold-time gating
- Dynamic screen resolution detection via Autopy
- Debounce protection (300 ms) for non-move mode switching
- Instant move/drag response with post-click movement freeze to reduce drift
- Edge-triggered click actions (one trigger per gesture entry)
- Live FPS counter and gesture mode overlay
- Modular architecture: each module independently testable

---

## 🧰 Technology Stack

| Component           | Library                | Version |
| ------------------- | ---------------------- | ------- |
| Computer Vision     | OpenCV (opencv-python) | 4.13.0  |
| Hand Tracking       | MediaPipe (Tasks API)  | 0.10.35 |
| Numerical Computing | NumPy                  | 2.4.4   |
| Mouse Control       | Autopy                 | 4.0.1   |
| Language            | Python                 | 3.12+   |

---

## ⚙️ Installation

```bash
# Clone the repository
git clone <repo-url>
cd "AI Virtual Mouse"

# (Recommended) Create & activate a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Verify the MediaPipe model file is present
# Expected: src/hand_landmarker.task  (~7.8 MB)
dir src\hand_landmarker.task  # Windows
# ls -lh src/hand_landmarker.task  # Linux/macOS
```

---

## 🖥️ Usage

```bash
# Run the virtual mouse application
python src/ai_virtual_mouse.py

# Run the smoke test (webcam required, no mouse movement)
python tests/test_smoke.py

# Run the full unit test suite
python tests/test_phase6.py

# Run the FPS benchmark (10 seconds, webcam required)
python tests/test_benchmark.py

# Run parameter tuning utilities
python tools/tuning/test_parameter_tuning.py

# Optional diagnostic scripts
python tools/diagnostics/diagnose_mouse.py
```

**In-app controls:**

- Press **`q`** to quit the application
- The video feed shows detected hand landmarks (green), fingertip markers, FPS counter, and current gesture mode

---

## 📊 Performance

| Metric                 | Value                                |
| ---------------------- | ------------------------------------ |
| Mean FPS               | **20.0**                             |
| Median FPS             | **20.2**                             |
| Max FPS                | **49.3**                             |
| 95th Percentile FPS    | **27.3**                             |
| Gesture Classification | Rule-based (negligible overhead)     |
| Smoothing Overhead     | O(1) per frame                       |
| Hand Detection Model   | MediaPipe HandLandmarker (Tasks API) |

_Benchmarked on Intel Core i5-1135G7, 8 GB RAM, integrated 720p webcam, Windows 11._

---

## 🧪 Testing

| Test Suite                                    | Tests | Status | Description                                             |
| --------------------------------------------- | ----- | ------ | ------------------------------------------------------- |
| Smoke (`tests/test_smoke.py`)                 | —     | ✅     | Webcam + pipeline integration                           |
| Unit & Integration (`tests/test_phase6.py`)   | 33    | ✅     | Gesture classifier, coordinate mapper, mouse controller |
| Benchmark (`tests/test_benchmark.py`)         | —     | ✅     | FPS over 10 seconds                                     |
| Parameter Tuning (`tools/tuning/`)            | —     | ✅     | Threshold/smoothing tuning scripts                      |

**Skipped:** Scroll test — `autopy.mouse.scroll()` not available in Autopy 4.0.1.

---

## 🔧 Configuration

All tunable parameters are in `src/config.py`:

| Parameter | Default | Description |
| --- | --- | --- |
| `SMOOTHING_FACTOR` | 5.0 | Higher = smoother cursor, more lag; grid-search optimal |
| `LEFT_CLICK_PINCH_ON_PX` | 28 | Left click pinch ON threshold (hysteresis entry) |
| `LEFT_CLICK_PINCH_OFF_PX` | 38 | Left click pinch OFF threshold (hysteresis release) |
| `RIGHT_CLICK_PINCH_ON_PX` | 34 | Right click pinch ON threshold (hysteresis entry) |
| `RIGHT_CLICK_PINCH_OFF_PX` | 44 | Right click pinch OFF threshold (hysteresis release) |
| `CLICK_HOLD_TIME_MS` | 100 | Minimum pinch hold duration to trigger click |
| `MOVE_FREEZE_AFTER_CLICK_MS` | 200 | Temporary cursor freeze after click trigger |
| `DEBOUNCE_TIME_MS` | 300 | Min stable gesture duration before activation |
| `FRAME_REDUCTION` | 100 | Dead-zone margin at frame edges (px) |
| `SCROLL_CENTER_DEAD_ZONE_PX` | 35 | No-scroll zone around camera center line |
| `SCROLL_STEP_AMOUNT` | 2 | Scroll step per trigger (up/down) |
| `SCROLL_REPEAT_MS` | 120 | Minimum interval between scroll triggers |
| `MIN_DETECTION_CONFIDENCE` | 0.5 | Minimum palm detection confidence |
| `MIN_TRACKING_CONFIDENCE` | 0.5 | Minimum landmark tracking confidence |

---

## ⚠️ Known Limitations

1. **Scroll backend depends on Autopy build** — some Autopy installs do not expose `mouse.scroll()`. In that case scroll gestures are classified but ignored.

2. **Single-hand only** — Tracks one hand at a time. Multi-hand gestures (pinch-to-zoom, rotation) not supported.

3. **Lighting sensitivity** — Performance degrades under strong backlight or very low light (inherent to RGB-based hand detection).

4. **No interactive calibration UI** — tune values manually in `src/config.py` if needed.

---

## 📚 Documentation

| Document                   | Path                                 |
| -------------------------- | ------------------------------------ |
| Product Requirements       | `docs/PRD.md`                        |
| Implementation Plan        | `docs/implementation_plan.md`        |
| Scientific Article (draft) | `article/01_draft.md`                |
| Literature Review          | `literature/00_literature_review.md` |
| Research Notes             | `docs/project_research.md`           |

---

## 📝 References

1. Zhang, F., et al. _MediaPipe Hands: On-device Real-time Hand Tracking._ arXiv:2006.10214, 2020.
2. Xu, P. _A Real-time Hand Gesture Recognition and Human-Computer Interaction System._ arXiv:1704.07296, 2017.
3. Köpüklü, O., et al. _Real-time Hand Gesture Detection and Classification Using CNNs._ IEEE FG, 2019.
4. Amprimo, G., et al. _Hand tracking for clinical applications: validation of GMH and GMH-D._ arXiv:2308.01088, 2023.

Full reference list: `literature/00_literature_review.md`

---

## 🙏 Credits

- **Murtaza Hassan** — Murtaza's Workshop (original tutorial)
- **Google MediaPipe** — Hand landmark detection framework
- **OpenCV** — Computer vision library
- **Autopy** — Cross-platform mouse control

---

_Project developed as part of **Pengolahan Citra (Image Processing)** coursework, Semester 6._
