# AI Virtual Mouse Context

## Glossary

### Project Presentation

A presentation focused on the AI Virtual Mouse prototype as an application project: problem, baseline behavior, improved behavior, safety design, architecture overview, demo flow, and benchmark results.

### Peer Tutoring Presentation

A presentation format where the presenter acts as a technical peer tutor or guest speaker. The flow teaches how the AI Virtual Mouse works, connects concepts to concrete project code, demonstrates gesture behavior, and uses benchmark results only as supporting evidence.

### Peer Tutoring Technical Depth

The peer tutoring presentation is medium-to-deep technical: code-aware, architecture-aware, and method-aware. It should mention key files and simple logic slices for hand tracking, gesture classification, the shared hand-control pipeline, debounce, benchmark safety, and metric interpretation, without becoming a full source-code walkthrough.

### Presentation Audience

The target audience for the project presentation is a university classroom or lecturer audience in an image processing course.

### Presentation Duration

The target duration is 10-14 minutes, with approximately 14 slides when a deeper technical peer tutoring explanation is requested.

### Presentation Main Message

The AI Virtual Mouse is a computer-vision hand-gesture prototype developed from a tutorial-style baseline into a safer, more modular, and more reliable point-and-click interaction system. The strongest supported improvement is a large reduction in false clicks, not full replacement of a physical mouse or faster performance in all tasks.

### Presentation Slide Structure

The project presentation uses 11 slides: title, motivation, baseline prototype, baseline problems, improved prototype, system architecture, gesture semantics, safety and benchmark design, benchmark results, demo flow, and conclusion/future work.

### Peer Tutoring Slide Structure

The peer tutoring presentation uses 14 slides for deeper technical delivery: opening learning goals, OpenCV and MediaPipe foundations, MediaPipe Solutions versus Tasks, webcam-to-cursor system flow, gesture mental model, baseline version overview, baseline code problem, improved changes, improved architecture, debounce logic, runtime safety, benchmark logic, benchmark evidence, and Ringkasan Pembelajaran.

### Presentation Language

The presentation language is Indonesian, with English technical terms when they are clearer or standard in the project, such as baseline, improved pipeline, gesture engine, debounce, and benchmark.

### Presentation Visual Style

The presentation uses a modern technical classroom deck style: clean academic layout, blue/cyan computer-vision accents, magenta cursor/gesture highlights, green success/result accents, simple architecture diagrams, and limited visual clutter.

### Peer Tutoring Visual Style

The peer tutoring deck uses a workshop/tutorial style with teaching cards, concept/code/demo labels, light pseudo-code, webcam-to-cursor diagrams, gesture visuals, and conversational Indonesian phrasing while retaining a clean technical look.

### Peer Tutoring Speaker Support

Each slide should include a short presenter prompt or transition question rather than long speaker notes, so the deck supports a peer tutoring delivery without overcrowding the slide.

### Peer Tutoring Benchmark Emphasis

Benchmark results are limited to one supporting slide. The slide should show 100% hit rate for both conditions, false clicks reduced from 192.8 to 4.2, total clicks reduced from 212.8 to 24.2, and a caveat that the improved condition was not faster on average because of an outlier.

### Peer Tutoring Technical Detail Requirements

The deck should explicitly explain OpenCV and MediaPipe, MediaPipe Solutions versus MediaPipe Tasks, why the improved version moves toward Tasks, the camera-to-cursor pipeline, the baseline code issue that causes repeated clicks, the concrete improved changes, and the benchmark logic used to derive the results.

### Ringkasan Pembelajaran

Use "Ringkasan Pembelajaran" instead of "Takeaways" for the final tutoring slide. It means the practical lessons the audience should remember after the session.

### Peer Tutoring Presenter Identity

The opening slide should include Raditya Rafif Pratama Sasmita and Politeknik Negeri Semarang. A separate presenter biography slide is not needed.

### Baseline Condition

The tutorial-compatible AI Virtual Mouse behavior used as a comparison point. It uses index-only cursor movement and index-middle pinch clicking without debounce or pause behavior.

### Improved Condition

The enhanced AI Virtual Mouse behavior used as the main prototype. It emphasizes stable interaction through adaptive smoothing, stable pinch clicking, debouncing, pause behavior, optional calibration, and explicit backend metadata.

### Benchmark Runtime

The controlled point-and-click evaluation mode. It uses a simulated cursor and does not move the operating-system mouse.

### Real Mouse Runtime

The demo mode that controls the operating-system cursor using webcam hand gestures and runtime safety controls.

### Stable Pinch Click

A click interaction where an index-middle pinch must be stable before one click is emitted, then must be released before another click can be emitted.
