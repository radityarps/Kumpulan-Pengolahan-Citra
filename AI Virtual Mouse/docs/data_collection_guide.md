# Data Collection Guide — AI Virtual Mouse Paper

**Purpose:** This guide tells you exactly what data to collect, how to collect it, and where to fill it into the paper.

**Paper file:** `article/AI_Virtual_Mouse_Paper.docx`  
**All `[DATA NEEDED]` markers in the DOCX correspond to steps below.**

---

## Overview: What Data Is Missing

| # | Data Point | Section in Paper | Priority | Estimated Time |
|---|---|---|---|---|
| 1 | FPS Benchmark Results | 4.4 — Table 6 | 🔴 REQUIRED | 5 min |
| 2 | Smoothing Grid Search Results | 4.5 — Table 7 | 🟡 High | 10 min |
| 3 | Gesture Recognition Accuracy | 4.2 — Table 4 | 🔴 REQUIRED | 1-2 hours |
| 4 | Confusion Matrix | 4.3 — Table 5 | 🟡 High | Same as #3 |
| 5 | SUS Usability Scores | 4.6 — Tables 8-9 | 🟡 High | 1-2 hours |
| 6 | Figures (diagrams, screenshots) | Throughout | 🟡 High | 1-2 hours |

---

## Step 1: Run FPS Benchmark (5 minutes)

**What you get:** Table 6 data (Mean, Median, Max, 95th percentile, Min FPS, frame count).

**How to run:**

```bash
cd "D:\Files\Documents\Kuliah\Semester 6\Pengolahan Citra\AI Virtual Mouse"
python tests/test_benchmark.py
```

**What to do:**
1. Make sure your webcam is NOT covered — benchmark needs real camera input.
2. Sit normally in front of the webcam (as if using the app).
3. Run the script. It runs for 10 seconds.
4. Copy ALL the output numbers.

**What you'll see:**
```
==================================================
  PERFORMANCE BENCHMARK RESULTS
==================================================
  Duration:         10.3s
  Frames captured:  177
  FPS samples:      ...
  Mean FPS:         20.0
  Median FPS:       20.2
  Min FPS:          ...
  Max FPS:          49.3
  95th %ile FPS:    27.3
==================================================
```

**Fill into:** Table 6 in the DOCX.

---

## Step 2: Smoothing Grid Search (10 minutes)

**What you get:** Table 7 data (responsiveness, stability, score for each smoothing factor).

**How to run:**

Create this Python script as `tests/smoothing_grid_search.py`:

```python
"""Smoothing parameter grid search for paper results."""
import numpy as np

def simulate_cursor_path(frames=200, noise_amp=3.0):
    """Generate synthetic cursor movement with noise."""
    t = np.linspace(0, 4 * np.pi, frames)
    true_x = 500 + 300 * np.sin(t)
    true_y = 300 + 200 * np.cos(t)
    noisy_x = true_x + np.random.normal(0, noise_amp, frames)
    noisy_y = true_y + np.random.normal(0, noise_amp, frames)
    return true_x, true_y, noisy_x, noisy_y

def exponential_smooth(raw, factor):
    """Apply exponential smoothing. factor = s (higher = smoother)."""
    smoothed = np.zeros_like(raw)
    smoothed[0] = raw[0]
    for i in range(1, len(raw)):
        smoothed[i] = smoothed[i-1] + (raw[i] - smoothed[i-1]) / factor
    return smoothed

def evaluate(factor, true_x, noisy_x):
    """Return (responsiveness, stability, score)."""
    smoothed = exponential_smooth(noisy_x, factor)
    # Responsiveness: mean step size of smoothed (higher = more responsive)
    responsiveness = np.mean(np.abs(np.diff(smoothed)))
    # Stability: std dev of error between smoothed and noisy
    stability = np.std(smoothed - noisy_x)
    # Combined score: balance responsiveness and stability
    score = responsiveness / stability
    return responsiveness, stability, score

if __name__ == "__main__":
    np.random.seed(42)
    true_x, true_y, noisy_x, noisy_y = simulate_cursor_path()
    
    factors = [3, 4, 5, 6, 7, 9, 11]
    
    print(f"{'Factor':>8} {'Respons.':>10} {'Stability':>10} {'Score':>10}")
    print("-" * 42)
    
    for s in factors:
        resp_x, stab_x, score_x = evaluate(s, true_x, noisy_x)
        resp_y, stab_y, score_y = evaluate(s, true_y, noisy_y)
        # Average x and y
        resp = (resp_x + resp_y) / 2
        stab = (stab_x + stab_y) / 2
        score = (score_x + score_y) / 2
        print(f"{s:>8} {resp:>10.3f} {stab:>10.3f} {score:>10.1f}")
```

**Run:**
```bash
python tests/smoothing_grid_search.py
```

**Fill into:** Table 7 in the DOCX. Mark the best row as "(optimal)".

---

## Step 3: Gesture Recognition Accuracy (1-2 hours)

**What you get:** Table 4 data (accuracy per gesture per lighting condition) + Table 5 (confusion matrix).

### 3.1 Setup

You need to test under 3 lighting conditions:
- **Bright**: Normal office lighting (daytime, overhead lights on)
- **Dim**: Evening with only 1 desk lamp
- **Backlit**: Face a window during daytime (camera between you and window)

### 3.2 Test Protocol

For each lighting condition:

1. Run the program:
   ```bash
   python src/ai_virtual_mouse.py
   ```

2. Perform each gesture **50 times**:
   - **Move**: Lift index finger, move hand around. Verify cursor follows.
   - **Left Click**: Pinch index + middle finger together. Verify click happens.
   - **Right Click**: Pinch index + ring finger together. Verify right-click.
   - **Drag**: Make a fist. Verify drag activates. Move hand to drag.
   - **Scroll**: Extend four fingers. Move hand up/down to scroll.

3. Count:
   - ✅ Correct: Gesture recognized and correct action executed.
   - ❌ Missed: Gesture performed but system didn't react.
   - ❌ Wrong: System executed wrong action.

4. Record in this table:

```
LIGHTING: ___________ (Bright / Dim / Backlit)

Gesture     | Attempts | Correct | Missed | Wrong | Accuracy
------------------------------------------------------------
Move        |    50    |   ___   |  ___   |  ___  |   ___%
Left Click  |    50    |   ___   |  ___   |  ___  |   ___%
Right Click |    50    |   ___   |  ___   |  ___  |   ___%
Drag        |    50    |   ___   |  ___   |  ___  |   ___%
Scroll      |    50    |   ___   |  ___   |  ___  |   ___%
------------------------------------------------------------
TOTAL       |   250    |   ___   |  ___   |  ___  |   ___%
```

### 3.3 Confusion Matrix

For Table 5, also track WHAT the system did when it was wrong:

```
                    PREDICTED
                Move  Click  RClick  Drag  Scroll  None
ACTUAL  Move     __    __      __     __     __     __
        Click    __    __      __     __     __     __
        RClick   __    __      __     __     __     __
        Drag     __    __      __     __     __     __
        Scroll   __    __      __     __     __     __
```

**Fill into:** Table 4 and Table 5 in the DOCX.

---

## Step 4: SUS Usability Testing (1-2 hours)

**What you get:** Table 8 (SUS scores) + Table 9 (Likert ratings).

### 4.1 Recruit Participants

Minimum 5 people. Ideally mix of:
- Experienced computer users
- Novice/less technical users

### 4.2 Test Procedure per Participant

1. **Brief them**: "You'll control the computer cursor using hand gestures in front of a webcam. No mouse or touchpad."
2. **Demo the gestures**: Show Move, Click, Right Click, Drag, Scroll.
3. **Give them a task**: 
   - Open a browser, navigate to google.com using gestures
   - Search for something
   - Click a result
   - Scroll down the page
   - Right-click and save an image (or similar)
   - Close the browser
4. **Ask them to complete the SUS questionnaire** (10 questions).
5. **Ask the 5 Likert-scale questions**.

### 4.3 SUS Questionnaire

Ask each participant to rate these 10 statements (1 = Strongly Disagree, 5 = Strongly Agree):

| # | Statement |
|---|---|
| 1 | I think that I would like to use this system frequently. |
| 2 | I found the system unnecessarily complex. |
| 3 | I thought the system was easy to use. |
| 4 | I think that I would need the support of a technical person to be able to use this system. |
| 5 | I found the various functions in this system were well integrated. |
| 6 | I thought there was too much inconsistency in this system. |
| 7 | I would imagine that most people would learn to use this system very quickly. |
| 8 | I found the system very cumbersome to use. |
| 9 | I felt very confident using the system. |
| 10 | I needed to learn a lot of things before I could get going with this system. |

**How to calculate SUS score:**
- Odd items (1, 3, 5, 7, 9): Score = Rating - 1
- Even items (2, 4, 6, 8, 10): Score = 5 - Rating
- Sum all scores, multiply by 2.5 → Final SUS score (0-100)

### 4.4 Likert-Scale Questions (1-5)

| # | Statement |
|---|---|
| L1 | The cursor movement felt natural and responsive. |
| L2 | Click actions were easy to perform. |
| L3 | I could complete tasks without excessive fatigue. |
| L4 | I would prefer this over a traditional mouse for presentations. |
| L5 | The system was easy to learn. |

### 4.5 Record Results

```
Participant | Type (Exp/Nov) | SUS Score | L1 | L2 | L3 | L4 | L5
-------------------------------------------------------------------
1           |                |           |    |    |    |    |
2           |                |           |    |    |    |    |
3           |                |           |    |    |    |    |
4           |                |           |    |    |    |    |
5           |                |           |    |    |    |    |
-------------------------------------------------------------------
MEAN        |                |           |    |    |    |    |
```

**Fill into:** Table 8 and Table 9 in the DOCX.

---

## Step 5: Create Figures (1-2 hours)

You need these figures. Create them, export as PNG, then insert into the DOCX.

### Figure 1: System Architecture Diagram

**Tool:** draw.io (free, diagrams.net) or PowerPoint

**Content:**
```
[Webcam (OpenCV)]
       │
       ▼
[HandDetector.findHands()]  ← MediaPipe Hands
       │
       ▼
[lmList = findPosition()]    ← 21 landmark (x,y,z)
       │
       ▼
[fingers = fingersUp()]      ← Array 5 jari [0/1]
       │
       ▼
[Gesture Classification]     ← Rule-based: if-else
       │
       ├── Move Mode
       ├── Click Mode (pinch)
       ├── Right Click Mode (pinch)
       ├── Drag Mode (fist)
       └── Scroll Mode (4 fingers)
       │
       ▼
[Coordinate Mapping]         ← numpy.interp(640×480 → screen)
       │
       ▼
[Exponential Smoothing]      ← s = 5.0
       │
       ▼
[Mouse Control (Autopy)]     ← move(), click(), toggle(), scroll()
```

**Export as:** `fig1_architecture.png` (at least 1200px wide)

### Figure 2: Screenshot of Running Application

- Run `python src/ai_virtual_mouse.py`
- Take screenshot with:
  - Hand visible with landmarks
  - FPS counter showing
  - Mode text visible ("Move Mode" or "Click Mode")
  - Finger state debug info visible

**Export as:** `fig2_screenshot.png`

### Figure 3: Confusion Matrix Heatmap (optional, after Step 3)

**Tool:** Python matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Fill in your confusion matrix data
labels = ['Move', 'Click', 'RClick', 'Drag', 'Scroll', 'None']
data = np.array([
    # [Move, Click, RClick, Drag, Scroll, None]
    # Fill from your Step 3 data
])

plt.figure(figsize=(8, 6))
sns.heatmap(data, annot=True, fmt='d', cmap='Blues',
            xticklabels=labels, yticklabels=labels)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Gesture Classification Confusion Matrix')
plt.tight_layout()
plt.savefig('fig3_confusion_matrix.png', dpi=150)
```

### Figure 4: FPS Distribution (optional, from benchmark)

Run benchmark multiple times and plot FPS distribution.

---

## Step 6: Fill Into the DOCX

After collecting all data:

1. Open `article/AI_Virtual_Mouse_Paper.docx` in Microsoft Word or LibreOffice.
2. Search for `[DATA NEEDED]` (Ctrl+F).
3. Replace each marker with actual numbers from Steps 1-5.
4. Insert figures (Insert → Picture → select PNG files).
5. Update Table of Contents (if Word asks).
6. Fill author details (name, department, university, email).
7. Proofread: remove all remaining `[DATA NEEDED]` markers.
8. Save as final.

---

## Quick Reference: All Commands

```bash
# Step 1: FPS Benchmark
python tests/test_benchmark.py

# Step 2: Smoothing Grid Search
python tests/smoothing_grid_search.py   # (create this file first)

# Step 3: Run the app for gesture testing
python src/ai_virtual_mouse.py

# Step 3b: Run unit tests (verification)
python -m pytest tests/test_phase6.py -v

# Re-generate DOCX after changes to generate_paper.js
node article/generate_paper.js
```

---

## Checklist

- [ ] Step 1: FPS benchmark ran, output saved
- [ ] Step 2: Smoothing grid search ran, best factor confirmed = 5
- [ ] Step 3: Gesture accuracy tested under 3 lighting conditions (250 attempts each)
- [ ] Step 3: Confusion matrix filled
- [ ] Step 4: SUS questionnaire administered to ≥5 participants
- [ ] Step 4: Likert ratings collected
- [ ] Step 5: Figure 1 (architecture diagram) created
- [ ] Step 5: Figure 2 (app screenshot) created
- [ ] Step 5: Figure 3 (confusion matrix heatmap) created
- [ ] Step 6: All `[DATA NEEDED]` markers replaced with real data
- [ ] Step 6: All figures inserted into DOCX
- [ ] Step 6: Author info filled
- [ ] Step 6: Final proofread — no placeholders remain
