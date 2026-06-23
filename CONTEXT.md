# AI Virtual Mouse

This context defines the domain language for the AI Virtual Mouse research prototype and its runtime variants.

## Language

**Real Mouse Runtime**:
A webcam-controlled runtime where recognized hand gestures operate the real operating system cursor.
_Avoid_: video version, real app, program like the video

**Benchmark Runtime**:
A webcam-controlled runtime where recognized hand gestures operate a simulated cursor inside the benchmark window.
_Avoid_: test mode, fake mouse, benchmark app when contrasted with runtime behavior

**Shared Hand-Control Pipeline**:
The common interpretation path from hand landmarks to gesture state and mapped cursor intent.
_Avoid_: tracking code, mouse logic

**Improved Condition**:
The experimental treatment that uses modernized hand tracking when available and improved gesture, mapping, smoothing, calibration, and debounce behavior.
_Avoid_: new version, better mode

**Backend Fallback**:
A recorded runtime substitution from MediaPipe Tasks to MediaPipe Solutions when the primary backend cannot start.
_Avoid_: silent fallback, hidden downgrade

**Simple Real Mouse Profile**:
The first Real Mouse Runtime gesture profile that supports movement, left click, and pause only.
_Avoid_: full gestures, demo profile

**Pause Toggle Gesture**:
An open-palm hold that toggles whether the Real Mouse Runtime ignores cursor and click actions.
_Avoid_: open palm pause, hand stop

**Stable Pinch Click**:
A left-click gesture emitted once when an index-middle pinch remains active for the configured debounce frames.
_Avoid_: pinch click, click every frame

**Default Tracking Bounds**:
The video-style reduced camera rectangle used before any user-specific calibration exists.
_Avoid_: no calibration, hardcoded mapping

**Optional Calibration**:
A user-triggered capture of comfortable hand movement bounds that can replace Default Tracking Bounds.
_Avoid_: required calibration

**Adaptive Smoothing Default**:
The Real Mouse Runtime's default cursor smoothing policy that reduces jitter while preserving responsiveness for large movements.
_Avoid_: smoothening value, fixed smoothing

**Runtime Safety Controls**:
The required escape mechanisms for Real Mouse Runtime: keyboard quit, Pause Toggle Gesture, and corner failsafe.
_Avoid_: just press q, kill switch

## Relationships

- A **Shared Hand-Control Pipeline** can feed a **Real Mouse Runtime** or a **Benchmark Runtime**.
- A **Real Mouse Runtime** controls the operating system cursor; a **Benchmark Runtime** must not control it.
- An **Improved Condition** can use a **Backend Fallback**, but the fallback must be visible in metadata.
- The **Simple Real Mouse Profile** belongs to the **Real Mouse Runtime** and intentionally excludes drag and scroll.
- A **Pause Toggle Gesture** controls whether the **Real Mouse Runtime** accepts actions from the **Shared Hand-Control Pipeline**.
- A **Stable Pinch Click** is rearmed only after the pinch is released for the configured release frames.
- **Optional Calibration** can replace **Default Tracking Bounds** for cursor mapping.
- **Adaptive Smoothing Default** is configurable through runtime configuration, not through the initial Real Mouse Runtime UI.
- **Runtime Safety Controls** protect users when the **Real Mouse Runtime** controls the operating system cursor.

## Example dialogue

> **Dev:** "Should this gesture change affect the Real Mouse Runtime only?"
> **Domain expert:** "No — if it changes hand interpretation, put it in the Shared Hand-Control Pipeline so the Benchmark Runtime measures the same behavior."

## Flagged ambiguities

- "program like video version" was resolved to **Real Mouse Runtime**.
- "benchmark and/or real mouse demo" separates into **Benchmark Runtime** and **Real Mouse Runtime**.
- A failed Tasks backend should not silently become Solutions; this is a **Backend Fallback** and must be recorded.
- "first real app" was resolved to **Simple Real Mouse Profile**: movement, left click, and pause only.
- "pause" was resolved to **Pause Toggle Gesture**: an open-palm hold toggles paused/unpaused state.
- "click" was resolved to **Stable Pinch Click**: emit once on stable pinch start, then rearm after release.
- "calibration" was resolved as **Optional Calibration**: the Real Mouse Runtime starts with **Default Tracking Bounds**.
- "smoothing" was resolved to **Adaptive Smoothing Default** configured in TOML.
- "safety" was resolved to **Runtime Safety Controls**: keyboard quit, pause toggle, and corner failsafe.
