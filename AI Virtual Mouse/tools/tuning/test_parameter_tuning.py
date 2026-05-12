"""
AI Virtual Mouse — Fase 6 Parameter Tuning
Evaluates smoothing factor and threshold parameters against synthetic data.
Reports optimal values balancing responsiveness and stability.

Run: python tools/tuning/test_parameter_tuning.py
"""

import math
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.config import (
    CLICK_THRESHOLD_PX,
    DEBOUNCE_TIME_MS,
    DRAG_THRESHOLD_PX,
    SCROLL_DEAD_ZONE_PX,
    SCROLL_SENSITIVITY,
)
from src.coordinate_mapper import CoordinateMapper


# ── Smoothing Factor Grid Search ──────────────────────────────────────────


def simulate_cursor_path(steps=100, noise_amplitude=3.0):
    """Generate a synthetic cursor path: linear motion + random jitter."""
    raw = []
    for i in range(steps):
        x = 100.0 + (i * 5.0)  # steady 5 px/frame movement
        y = 200.0 + (i * 2.0)
        # Add sinusoidal + random jitter
        jitter_x = noise_amplitude * math.sin(i * 0.5) + (
            noise_amplitude * 0.3 * (i % 3 - 1)
        )
        jitter_y = noise_amplitude * math.cos(i * 0.5) + (
            noise_amplitude * 0.3 * (i % 5 - 2)
        )
        raw.append((x + jitter_x, y + jitter_y))
    return raw


def evaluate_smoothing(factor, path):
    """Run smoothing over path; return mean absolute step size (responsiveness)
    and standard deviation of steps (stability). Lower stddev = smoother."""
    mapper = CoordinateMapper(
        frame_width=640,
        frame_height=480,
        frame_reduction=100,
        smoothing_factor=factor,
    )
    smoothed = []
    for x, y in path:
        sx, sy = mapper.smooth(x, y)
        smoothed.append((sx, sy))

    steps = [
        math.hypot(
            smoothed[i][0] - smoothed[i - 1][0],
            smoothed[i][1] - smoothed[i - 1][1],
        )
        for i in range(1, len(smoothed))
    ]
    mean_step = sum(steps) / len(steps) if steps else 0.0
    variance = sum((s - mean_step) ** 2 for s in steps) / len(steps) if steps else 0.0
    stddev = math.sqrt(variance)
    return mean_step, stddev


def _extract_score(item):
    """Extract score from a (factor, mean_step, stddev, score) tuple."""
    return item[3]


def tune_smoothing():
    """Grid search over SMOOTHING_FACTOR values."""
    path = simulate_cursor_path(200, noise_amplitude=3.0)
    candidates = [3, 5, 7, 9, 11, 15, 20]

    print()
    print("=" * 60)
    print("  SMOOTHING FACTOR TUNING RESULTS")
    print("=" * 60)
    header = (
        f"{'Factor':>6} | {'Responsiveness':>14} | {'Stability':>14} | {'Score':>12}"
    )
    subheader = (
        f"{'':>6} | {'(mean step px)':>14} | {'(stddev,lower)':>14}"
        f" | {'(ratio*100)':>12}"
    )
    print(header)
    print(subheader)
    print("-" * 60)

    results = []
    for factor in candidates:
        mean_step, stddev = evaluate_smoothing(factor, path)
        # Score: responsiveness / stability (higher better)
        score = (mean_step / (stddev + 0.001)) * 100 if stddev > 0 else 999
        results.append((factor, mean_step, stddev, score))
        print(f"{factor:6d} | {mean_step:14.3f} | {stddev:14.3f} | {score:12.1f}")

    print("-" * 60)

    # Pick best (highest score)
    best = max(results, key=_extract_score)
    print()
    print(f"-> Recommended SMOOTHING_FACTOR: {best[0]} (score: {best[3]:.1f})")
    print(f"   Responsiveness: {best[1]:.3f} px/frame")
    print(f"   Stability:      {best[2]:.3f} px stddev")
    return best[0]


# ── Threshold Sensitivity Analysis ─────────────────────────────────────────


def analyze_thresholds():
    """Print tuning guidance for click, drag, debounce thresholds."""
    print()
    print("=" * 60)
    print("  THRESHOLD TUNING GUIDANCE")
    print("=" * 60)
    print(f"{'Parameter':<22} | {'Current':>8} | Guidance")
    print("-" * 60)
    print(f"{'CLICK_THRESHOLD_PX':<22} | {CLICK_THRESHOLD_PX:8d} | <20: false clicks")
    print(f"{'':<22} | {'':>8} | >60: hard to trigger")
    print(f"{'DRAG_THRESHOLD_PX':<22} | {DRAG_THRESHOLD_PX:8d} | <15: accidental drag")
    print(f"{'':<22} | {'':>8} | >50: hard to drag")
    print(f"{'DEBOUNCE_TIME_MS':<22} | {DEBOUNCE_TIME_MS:8d} | <150: mode flicker")
    print(f"{'':<22} | {'':>8} | >500: slow response")
    print(f"{'SCROLL_SENSITIVITY':<22} | {SCROLL_SENSITIVITY:8d} | 1: fast scroll")
    print(f"{'':<22} | {'':>8} | 4: slow scroll")
    print(f"{'SCROLL_DEAD_ZONE':<22} | {SCROLL_DEAD_ZONE_PX:8d} | <3: scroll jitter")
    print(f"{'':<22} | {'':>8} | >10: unresponsive")
    print("-" * 60)


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    best_smoothing = tune_smoothing()
    analyze_thresholds()

    print()
    print("=" * 60)
    print("  PARAMETER TUNING SUMMARY")
    print("=" * 60)
    print(f"  SMOOTHING_FACTOR:  {best_smoothing} (recommended from grid search)")
    print(f"  CLICK_THRESHOLD:   {CLICK_THRESHOLD_PX} px (current default)")
    print(f"  DRAG_THRESHOLD:    {DRAG_THRESHOLD_PX} px (current default)")
    print(f"  DEBOUNCE_TIME:     {DEBOUNCE_TIME_MS} ms (current default)")
    print("  FRAME_REDUCTION:   100 px (comfortable dead zone)")
    print("=" * 60)
    print()
    print("Note: Thresholds validated via unit tests and smoke test.")
    print("Final tuning requires human-in-the-loop testing (Fase 6.4).")
