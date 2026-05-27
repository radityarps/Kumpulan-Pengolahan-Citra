# PRD: Experimental Research Prototype for AI Virtual Mouse

## Problem Statement

The current AI Virtual Mouse project is a tutorial-style prototype that demonstrates hand-landmark based cursor movement and clicking. It works as a learning artifact, but it is not yet strong enough as a research prototype because it lacks a controlled benchmark, structured metrics, modern MediaPipe API usage, repeatable reporting, and a polished architecture.

The user wants the experimental branch to become a better version of the project: a full polished research prototype that can support the claim that the improved AI Virtual Mouse provides better usability than the video tutorial baseline.

The prototype must preserve a frozen version of the video implementation as the baseline condition, then provide an improved condition using the modern MediaPipe Tasks API, better interaction design, safer benchmarking, richer gestures, and automatic evaluation reports.

## Solution

Build a research-oriented AI Virtual Mouse application that compares a tutorial-compatible baseline against an improved user experience.

The improved version will use MediaPipe Tasks API with an auto-downloaded HandLandmarker model, modular application architecture, adaptive cursor smoothing, calibration, click debouncing, drag support, scroll support, and pause behavior. The benchmark will use a simulated cursor inside a Pygame-controlled task environment rather than controlling the real OS mouse during evaluation.

The main evaluation method will be a point-and-click grid benchmark that records task performance and technical metrics. After each benchmark session, the system will generate CSV logs, plots, and a Markdown report suitable for use in project documentation, academic reports, and presentations.

The primary research comparison is final user experience:

- Baseline condition: frozen video clone with compatibility fixes only.
- Improved condition: polished app using modern MediaPipe Tasks API and usability improvements.

The API backend should still be recorded in logs so that modernization from the old MediaPipe Solutions API to the new MediaPipe Tasks API is visible in the research artifacts.

## User Stories

1. As a student researcher, I want a frozen baseline mode, so that I can compare the improved version against the original tutorial behavior.
2. As a student researcher, I want an improved mode, so that I can demonstrate better usability than the video baseline.
3. As a student researcher, I want the app to use the MediaPipe Tasks API, so that the implementation reflects the modern MediaPipe direction.
4. As a student researcher, I want the app to record which tracking backend is used, so that API modernization is visible in the experiment logs.
5. As a student researcher, I want the HandLandmarker model to be downloaded automatically, so that setup is reproducible and does not rely on manual file placement.
6. As a student researcher, I want benchmark data saved as CSV, so that I can analyze trial-level results later.
7. As a student researcher, I want summary metrics generated automatically, so that I can quickly report completion time, accuracy, and errors.
8. As a student researcher, I want benchmark plots generated automatically, so that I can include visual evidence in documentation and presentations.
9. As a student researcher, I want a Markdown report generated after benchmark sessions, so that the experiment is immediately explainable.
10. As a student researcher, I want baseline and improved conditions separated, so that the comparison is fair and understandable.
11. As a student researcher, I want ablation modes, so that I can see which improvement contributes to usability gains.
12. As a student researcher, I want smoothing-only mode, so that I can evaluate the effect of cursor smoothing independently.
13. As a student researcher, I want debounce-only mode, so that I can evaluate the effect of click debouncing independently.
14. As a student researcher, I want calibration-only mode, so that I can evaluate the effect of personalized tracking bounds independently.
15. As a student researcher, I want full improved mode, so that I can evaluate the complete polished experience.
16. As a user, I want to move the cursor with my index finger, so that I can control the pointer using a natural gesture.
17. As a user, I want to click with a stable pinch gesture, so that I can select targets reliably.
18. As a user, I want click debouncing, so that one pinch does not trigger multiple accidental clicks.
19. As a user, I want drag support, so that the virtual mouse can perform more realistic mouse interactions.
20. As a user, I want scroll support, so that the virtual mouse can support navigation beyond clicking.
21. As a user, I want a pause gesture or pause mode, so that I can rest my hand without unintended pointer movement.
22. As a user, I want calibration, so that the system adapts to my camera position and comfortable hand movement range.
23. As a user, I want adaptive smoothing, so that small movements are stable while large movements remain responsive.
24. As a user, I want clear visual feedback, so that I know whether I am moving, clicking, dragging, scrolling, or paused.
25. As a benchmark participant, I want the benchmark to use a simulated cursor, so that the test does not disrupt the real desktop.
26. As a benchmark participant, I want clear benchmark instructions, so that I know what task to perform.
27. As a benchmark participant, I want visible targets in a grid, so that I can complete point-and-click tasks consistently.
28. As a benchmark participant, I want a countdown or ready state before trials, so that I can prepare before measurement starts.
29. As a benchmark participant, I want feedback after each click, so that I know whether the target was hit or missed.
30. As a benchmark participant, I want the ability to quit safely, so that I can stop the benchmark if tracking becomes uncomfortable.
31. As a developer, I want a modular architecture, so that hand tracking, gesture classification, mapping, smoothing, benchmarking, and reporting can evolve independently.
32. As a developer, I want deep modules with small interfaces, so that the important logic can be tested without webcam hardware.
33. As a developer, I want configuration separated from runtime logic, so that experimental conditions can be changed without editing the main loop.
34. As a developer, I want benchmark sessions to be reproducible, so that trials can be compared across baseline and improved modes.
35. As a developer, I want safe defaults, so that the app does not unexpectedly control the OS mouse during benchmark sessions.
36. As a developer, I want optional real mouse mode outside the benchmark, so that the app can still function as a virtual mouse demo.
37. As a developer, I want logs to include timestamps, condition names, mode names, and parameter values, so that results can be traced back to their configuration.
38. As a developer, I want the benchmark to compute false clicks, missed targets, completion time, and target hit rate, so that usability can be quantified.
39. As a developer, I want technical metrics such as FPS and cursor jitter, so that responsiveness and stability can be evaluated.
40. As a developer, I want reports to identify the exact condition and backend used, so that research findings are not ambiguous.
41. As a maintainer, I want documentation updated for the experimental version, so that future users can install, run, benchmark, and interpret results.
42. As a maintainer, I want a troubleshooting guide for model download, camera failures, and tracking issues, so that setup problems can be resolved quickly.
43. As a maintainer, I want dependencies documented and pinned where needed, so that experiments remain reproducible.
44. As a reviewer, I want the benchmark methodology documented, so that I can judge whether the usability comparison is valid.
45. As a reviewer, I want out-of-scope items clearly documented, so that the prototype does not overclaim beyond the measured evidence.

## Implementation Decisions

- The experimental app will optimize for a research prototype rather than only a tutorial demo.
- The primary research claim is that the improved version provides better usability than the video baseline.
- The comparison will be final user experience rather than a pure API-only comparison.
- The baseline condition will be a frozen video clone with only compatibility and stability fixes.
- The improved condition will use MediaPipe Tasks API with HandLandmarker.
- The HandLandmarker model will be obtained through an auto-download setup step rather than manually placed by the user.
- The benchmark will use a simulated cursor in a Pygame window, not the real OS cursor.
- The app may still support real OS mouse control as a demo mode, but the benchmark path should remain simulated for safety and measurement accuracy.
- The gesture set for the improved mode will initially include movement, left click, drag, scroll, and pause.
- The benchmark task will be a point-and-click grid with randomly selected targets.
- The benchmark will output raw CSV logs, summary metrics, plots, and a Markdown report.
- The system will support ablation modes: baseline, smoothing-only, debounce-only, calibration-only, and full improved mode.
- The architecture should extract deep modules for tracking, gesture classification, coordinate mapping, smoothing, benchmark orchestration, metrics, and reporting.
- Configuration should define condition name, backend, smoothing strategy, debounce rules, calibration settings, gesture profile, benchmark parameters, and output paths.
- The app should separate camera capture from hand tracking so that tracking backends can be swapped or mocked.
- The app should separate gesture recognition from mouse/cursor effects so that gestures can be evaluated without moving the OS cursor.
- The app should separate benchmark target generation from rendering so that trial sequences can be deterministic and testable.
- The app should separate metric collection from report generation so that CSV data can be re-analyzed later.
- Logs should include enough metadata to reproduce the run: timestamp, participant/session identifier, condition, backend, mode, parameter values, screen/window size, and trial index.
- Metrics should include at minimum completion time, hit/miss status, false click count, click count, cursor path length, FPS, and jitter estimate.
- The Pygame benchmark window should provide clear instructions, target rendering, simulated cursor rendering, and safe quit controls.
- The documentation should explain the difference between baseline and improved modes, the benchmark methodology, and how to interpret generated reports.

## Testing Decisions

- Tests should focus on external behavior and measurable outputs rather than private implementation details.
- Pure logic modules should receive the strongest automated test coverage.
- Coordinate mapping should be tested with known camera bounds, screen/window bounds, and expected mapped coordinates.
- Smoothing should be tested by feeding known cursor sequences and checking stability/responsiveness behavior.
- Debouncing should be tested with sequences of pinch states and timestamps to ensure one gesture does not produce repeated clicks.
- Gesture classification should be tested with synthetic finger-state inputs and landmark distances.
- Calibration should be tested by feeding sample landmark ranges and verifying computed usable bounds.
- Benchmark target generation should be tested for deterministic output when a seed is provided.
- Metrics aggregation should be tested with sample trial logs and expected summaries.
- Report generation should be tested by generating output from fixture data and verifying that required sections and metrics are present.
- Tracking backend integration should be smoke-tested, but not heavily unit-tested because it depends on camera hardware and MediaPipe internals.
- Pygame rendering should be manually tested initially, with automated tests reserved for benchmark state transitions and metric outputs.
- The baseline mode should be manually verified against the tutorial behavior: index-only movement and index-middle pinch click.
- The improved mode should be manually verified for movement, click, drag, scroll, pause, calibration, and benchmark logging.

## Out of Scope

- Building a web dashboard is out of scope for the first experimental implementation.
- Comparing against a physical mouse is out of scope for the first benchmark because it introduces a different interaction category and may make the comparison unfair.
- Multi-user study management is out of scope, although logs should support multiple participant/session identifiers.
- Advanced statistical analysis is out of scope, but the generated CSV should support later statistical analysis.
- Full accessibility validation with target users is out of scope unless a later research phase is defined.
- Multi-hand gesture control is out of scope for the first improved version.
- Cross-platform OS mouse behavior beyond Windows-focused development is out of scope for the first pass.
- Packaging as a distributable desktop application is out of scope for the first pass.

## Further Notes

The old MediaPipe Solutions API is useful as a baseline because it matches the tutorial implementation. The improved version should use the newer MediaPipe Tasks API to support modernization, but the research claim should remain centered on usability improvement rather than API superiority alone.

The experiment should avoid overclaiming. If the benchmark only measures point-and-click behavior, the report should claim improvement in controlled point-and-click usability metrics, not general mouse replacement superiority.

A strong implementation path is:

1. Preserve baseline behavior.
2. Add modular architecture and configuration.
3. Add MediaPipe Tasks backend with auto-download.
4. Add simulated cursor and Pygame benchmark.
5. Add ablation modes.
6. Add CSV logging, metrics, plots, and Markdown report generation.
7. Update documentation and tests.
