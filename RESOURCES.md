# Image Processing & AI Virtual Mouse — Resources

## Knowledge

**Primary project source (the truth we teach from)**
- `AI Virtual Mouse/CONTEXT.md` — domain-language contract for the project
- `AI Virtual Mouse/src/ai_virtual_mouse_experimental/` — actual source code, the thing we'll be dissecting
- `AI Virtual Mouse/docs/ARCHITECTURE.md` — official architecture doc
- `AI Virtual Mouse/docs/API_REFERENCE.md` — module-by-module reference
- `Jobsheet 1`–`5` — used as background reference for individual concepts, not as the main path

**Canonical image-processing references**
- [OpenCV-Python Tutorials (official)](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html) — the standard reference for OpenCV in Python. Use for: any concrete API question (`cv2.cvtColor`, `cv2.threshold`, `cv2.Canny`).
- [MediaPipe Solutions docs — Hand Landmarker](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) — what the project actually uses to detect hands. Use for: understanding landmark indices, the 21-point hand model.
- [Gonzalez & Woods, *Digital Image Processing*](https://www.imageprocessingplace.com/) — the textbook. Use for: filter theory, frequency domain, formal definitions when intuition isn't enough.
- [PyImageSearch blog](https://pyimagesearch.com/) — Adrian Rosebrock's practical tutorials. Use for: hands-on OpenCV recipes in plain English. **Caveat:** quality varies, prefer the older "starter" posts over recent ones.

**Hand-tracking background**
- MediaPipe Hands paper / original repo — for understanding the 21-landmark model and why it returns normalized coordinates

## Wisdom (Communities)

- [r/computervision](https://reddit.com/r/computervision) — broad community, decent signal for "is my approach sane?" questions
- [r/learnmachinelearning](https://reddit.com/r/learnmachinelearning) — friendlier for beginners
- Stack Overflow `opencv` + `mediapipe` tags — best for "this exact error" debugging
- Local: kelas Pengolahan Citra Semester 6 + teman satu kelompok — they share your exact course context

## Gaps
- No good Indonesian-language tutorial for MediaPipe Hand Landmarker from scratch. If the user wants to teach friends in Bahasa Indonesia, they may have to translate as they go.
- The project's research paper (in `docs/Paper/`) is in English academic style — may need simplifying for tutoring purposes.
