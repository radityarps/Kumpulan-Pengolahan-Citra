# Mission: Image Processing & AI Virtual Mouse — deep enough to teach

## Why
The user is taking Pengolahan Citra (Image Processing, Semester 6) and wants to understand the material deeply enough to **teach it to friends and tutor them** — not just to pass the course. The concrete outcome: when a friend asks "how does the AI Virtual Mouse actually work?", the user can explain the chain from a webcam frame, through hand landmarks, to a moving cursor — and can answer follow-up "why" questions without bluffing.

## Success looks like
- Can explain the core image-processing concepts (pixels, color spaces, filters, thresholds, edge detection) using their own analogies, not textbook phrases
- Can walk a friend through the `AI Virtual Mouse` source code and explain what each module does and why it's split that way
- Can answer "what would happen if we changed X?" questions about the pipeline (e.g. "what if we used the whole camera frame instead of the reduced rectangle?")
- Can identify which Jobsheet topic underpins which part of the project

## Constraints
- Beginner in Python and image processing — start from first principles
- No prior exposure to OpenCV / MediaPipe
- Lessons should be short, completable in one sitting, and tied to the AI Virtual Mouse project
- The user is teaching in Bahasa Indonesia (most likely), so explanations should be in casual Indonesian; technical terms in English
- Limited sessions — focus on the *highest-leverage* concepts, not encyclopedic coverage

## Out of scope
- Deep math behind convolution (we'll use intuition, not proofs)
- Building a new project from scratch (we work *backwards* from the existing one)
- The full semester's 5 jobsheets in sequence (we use them as reference, not as the path)
- Performance optimization / production engineering concerns
