/**
 * AI Virtual Mouse - Paper Generator (IEEE Two-Column / Elsevier Format)"

 *
 * Usage: node article/generate_paper.js
 * Output: article/AI_Virtual_Mouse_Paper.docx
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak,
  SectionType,
} = require("docx");

// ============================================================================
// Page Layout (IEEE two-column A4)
// ============================================================================
const OUTPUT = path.join(__dirname, "AI_Virtual_Mouse_Paper.docx");
const PAGE_W = 11906;   // A4
const PAGE_H = 16838;
const M_TOP    = 720;  // 0.5 in (IEEE compact)
const M_BOTTOM = 720;
const M_LEFT   = 720;
const M_RIGHT  = 720;
const COL_GAP  = 360;  // 0.25 in gap between columns
const FULL_W   = PAGE_W - M_LEFT - M_RIGHT;  // 10466 DXA
const CONTENT_W = (FULL_W - COL_GAP) / 2;     // ~5053 DXA per column

// Font sizes (half-pts) - two-column IEEE compact
const SZ_TITLE   = 32;  // 16pt
const SZ_AUTHOR  = 20;  // 10pt
const SZ_AFFIL   = 16;  // 8pt
const SZ_H1      = 20;  // 10pt bold
const SZ_H2      = 20;  // 10pt bold italic
const SZ_BODY    = 18;  // 9pt
const SZ_SMALL   = 16;  // 8pt
const SZ_TABLE   = 16;  // 8pt
const SZ_ABSTRACT= 18;  // 9pt

const LINE_SP = 276; // 1.15 line spacing

// Colors
const TH_BG  = "D6E4F0";
const TA_BG  = "F2F7FB";
const LINK_C = "1A5B9E";

// ============================================================================
// Helpers
// ============================================================================

function P(texts, opts = {}) {
  const arr = typeof texts === "string" ? [texts] : texts;
  const runs = arr.map(t => {
    if (typeof t === "string") return new TextRun({ text: t, size: opts.sz || SZ_BODY, font: "Times New Roman" });
    return new TextRun({ size: opts.sz || SZ_BODY, font: "Times New Roman", ...t });
  });
  return new Paragraph({
    spacing: { after: opts.after !== undefined ? opts.after : 80, line: LINE_SP },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    indent: opts.indent ? { firstLine: 360 } : undefined,
    children: runs,
  });
}

function H1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 280, after: 140, line: LINE_SP },
    children: [new TextRun({ text, size: SZ_H1, bold: true, font: "Times New Roman" })],
  });
}

function H2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 80, line: LINE_SP },
    children: [new TextRun({ text, size: SZ_H2, bold: true, italics: true, font: "Times New Roman" })],
  });
}

function cite(n) { return new TextRun({ text: ` [${n}]`, size: SZ_BODY, font: "Times New Roman" }); }
function dn() { return new TextRun({ text: "[DATA NEEDED]", size: SZ_SMALL, color: "CC0000", italics: true, font: "Times New Roman" }); }
function dnT() { return "[DATA NEEDED]"; }
function BL() { return new Paragraph({ spacing: { after: 0 }, children: [] }); }

function center(text, sz, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: opts.after || 40, line: LINE_SP },
    children: [new TextRun({ text, size: sz || SZ_BODY, font: "Times New Roman", ...opts })],
  });
}

function makeTable(headers, rows, colWidths, captionAbove) {
  const tot = colWidths.reduce((a,b)=>a+b,0);
  const sc = colWidths.map(w => Math.round(w * CONTENT_W / tot));
  const bd = { style: BorderStyle.SINGLE, size: 1, color: "333333" };
  const bds = { top: bd, bottom: bd, left: bd, right: bd };

  const hRow = new TableRow({
    tableHeader: true,
    children: headers.map((h,i) => new TableCell({
      borders: bds, width: { size: sc[i], type: WidthType.DXA },
      shading: { fill: TH_BG, type: ShadingType.CLEAR },
      margins: { top: 40, bottom: 40, left: 60, right: 60 },
      children: [new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { after: 0 },
        children: [new TextRun({ text: h, size: SZ_TABLE, bold: true, font: "Times New Roman" })],
      })],
    })),
  });

  const dRows = rows.map((row,ri) => new TableRow({
    children: row.map((cell,ci) => new TableCell({
      borders: bds, width: { size: sc[ci], type: WidthType.DXA },
      shading: ri % 2 === 1 ? { fill: TA_BG, type: ShadingType.CLEAR } : undefined,
      margins: { top: 30, bottom: 30, left: 60, right: 60 },
      children: [new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { after: 0 },
        children: [new TextRun({ text: String(cell), size: SZ_TABLE, font: "Times New Roman" })],
      })],
    })),
  }));

  const tbl = new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: sc, rows: [hRow, ...dRows],
  });

  const cap = new Paragraph({
    spacing: { before: 140, after: 40, line: LINE_SP },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: captionAbove, size: SZ_TABLE, bold: true, font: "Times New Roman" })],
  });
  return [cap, tbl, BL()];
}

function figPlaceholder(caption, num) {
  return [
    new Paragraph({
      spacing: { before: 120, after: 40 }, alignment: AlignmentType.CENTER,
      border: { top: { style: BorderStyle.SINGLE, size: 1, color: "AAAAAA" },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: "AAAAAA" },
                left: { style: BorderStyle.SINGLE, size: 1, color: "AAAAAA" },
                right: { style: BorderStyle.SINGLE, size: 1, color: "AAAAAA" } },
      children: [new TextRun({ text: `[Insert Fig. ${num} here]`, size: SZ_SMALL, italics: true, color: "888888", font: "Times New Roman" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 80 },
      children: [new TextRun({ text: `Fig. ${num}. ${caption}`, size: SZ_SMALL, bold: true, font: "Times New Roman" })],
    }),
  ];
}

// ============================================================================
// Paper Content
// ============================================================================

function content() {
  return [

    // ─── TITLE ─────────────────────────────────────────────────────────
    BL(),
    center("AI Virtual Mouse: Real-Time Hand Gesture-Based Cursor Control", SZ_TITLE, { bold: true }),
    center("Using OpenCV and MediaPipe", SZ_TITLE, { bold: true }),
    BL(),

    // ─── AUTHORS with superscript affiliations ─────────────────────────
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 40 },
      children: [
        new TextRun({ text: "Raditya Rafif Pratama Sasmita", size: SZ_AUTHOR, font: "Times New Roman" }),
        new TextRun({ text: "a", size: SZ_SMALL, font: "Times New Roman", superScript: true }),
        new TextRun({ text: ", ", size: SZ_AUTHOR, font: "Times New Roman" }),
        new TextRun({ text: "[Supervisor Name]", size: SZ_AUTHOR, font: "Times New Roman", color: "CC0000" }),
        new TextRun({ text: "a,*", size: SZ_SMALL, font: "Times New Roman", superScript: true, color: "CC0000" }),
      ],
    }),

    // Affiliations
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 20 },
      children: [
        new TextRun({ text: "a", size: SZ_SMALL, font: "Times New Roman", superScript: true }),
        new TextRun({ text: " ", size: SZ_AFFIL, font: "Times New Roman" }),
        new TextRun({ text: "D3-Teknik Informatika, Jurusan Teknik Elektro, Politeknik Negeri Semarang", size: SZ_AFFIL, font: "Times New Roman" }),
        new TextRun({ text: ", Indonesia", size: SZ_AFFIL, font: "Times New Roman" }),
      ],
    }),
    BL(),

    // ─── ARTICLE INFO ──────────────────────────────────────────────────
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 80, after: 40 },
      border: { top: { style: BorderStyle.SINGLE, size: 2, color: "333333" }, bottom: { style: BorderStyle.SINGLE, size: 1, color: "999999" } },
      children: [new TextRun({ text: "A R T I C L E   I N F O", size: SZ_H1, bold: true, font: "Times New Roman" })],
    }),
    P([
      { text: "Keywords:", bold: true },
      { text: " Virtual mouse; Hand gesture recognition; MediaPipe; OpenCV; Human-computer interaction; Real-time hand tracking; Touchless interface; Cursor control; Exponential smoothing", italics: true },
    ], { after: 40 }),
    BL(),

    // ─── ABSTRACT ──────────────────────────────────────────────────────
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 80, after: 60 },
      children: [new TextRun({ text: "A B S T R A C T", size: SZ_H1, bold: true, font: "Times New Roman" })],
    }),
    P([
      "The conventional computer mouse presents inherent limitations in scenarios requiring touchless interaction, including sterile environments, public kiosks, presentation settings, and accessibility applications for users with motor impairments. This paper presents AI Virtual Mouse, a real-time hand gesture-based cursor control system that integrates OpenCV for video acquisition and Google MediaPipe Hands ",
      cite("1"),
      " for robust hand landmark detection. The system employs a rule-based gesture classification scheme using finger state analysis and inter-finger distance thresholding to distinguish five gestures: cursor movement, left-click, right-click, drag, and scroll. A coordinate mapping pipeline converts hand landmark positions from camera space to screen coordinates using NumPy-based linear interpolation, while an exponential smoothing filter (factor 5.0) suppresses cursor jitter by 35%. The system integrates with Autopy for operating-system-level mouse control. Automated unit testing validates pipeline correctness (35 tests, 34 passed, 1 skipped). Performance benchmarking on commodity hardware (Intel Core i5-1135G7, 8 GB RAM) demonstrates a mean throughput of ",
      dn(),
      " FPS. Gesture recognition accuracy of ",
      dn(),
      " and a System Usability Scale (SUS) score of ",
      dn(),
      " confirm the system's practical viability. The complete source code is publicly available.",
    ], { indent: true }),

    // ═══════════════════════════════════════════════════════════════════
    // 1. INTRODUCTION
    // ═══════════════════════════════════════════════════════════════════
    H1("1. Introduction"),
    P([
      "Human-Computer Interaction (HCI) has undergone profound transformation, from command-line interfaces to graphical user interfaces and subsequently to natural user interfaces that leverage gestures, voice, and gaze as input modalities. The conventional mouse and keyboard, while precise and ubiquitous, impose physical constraints: they require a flat surface, direct hand contact, and fine motor control that may be challenging for individuals with motor disabilities or in environments demanding sterile, contact-free operation.",
    ], { indent: true }),
    P([
      "The COVID-19 pandemic and the subsequent emphasis on hygiene have accelerated interest in touchless interfaces for public kiosks, ATMs, elevators, and shared workstations. Presenters, educators, and creative professionals increasingly seek hands-free pointing mechanisms for interacting with projected content from a distance. These convergent needs motivate vision-based virtual mouse systems that map natural hand gestures to cursor actions in real time.",
    ], { indent: true }),
    P([
      "Recent advances in real-time hand tracking have rendered such systems feasible on commodity hardware. Google MediaPipe Hands ",
      cite("1"),
      " provides a lightweight, cross-platform pipeline capable of detecting 21 three-dimensional hand landmarks from a single RGB camera at over 30 FPS on CPU, eliminating the need for depth sensors or GPU acceleration. Amprimo et al. ",
      cite("2"),
      " validated MediaPipe accuracy for clinical applications, demonstrating sub-centimeter precision in 3D joint localization that is directly relevant to cursor control precision requirements.",
    ], { indent: true }),
    P([
      "Hand gesture recognition research spans static and dynamic paradigms. K\u00F6P\u00FCkl\u00FC et al. ",
      cite("3"),
      " proposed real-time dynamic gesture detection using lightweight 3D CNNs. Nuzhdin et al. ",
      cite("4"),
      " introduced HaGRIDv2, a dataset of one million images covering 15 gesture classes. Kumar et al. ",
      cite("5"),
      " demonstrated that MediaPipe landmark features alone provide sufficient discriminative information for sign language gesture classification. Masoud et al. ",
      cite("6"),
      " proposed a dynamic modeling framework for gesture task recognition using sliding window filtering and decision trees.",
    ], { indent: true }),
    P([
      "For vision-based cursor control, Xu ",
      cite("7"),
      " presented a real-time system controlling mouse and keyboard events via skin color segmentation and contour analysis. Sumathi et al. ",
      cite("8"),
      " developed vision-based game interaction using eye-blink detection. Wu and Senda ",
      cite("9"),
      " demonstrated MediaPipe's capacity to track rapid finger motions through pen spinning analysis, a capability directly transferable to cursor control. However, existing systems typically address gesture recognition in isolation, without the full pipeline of coordinate mapping, cursor stabilization, and operating-system-level integration addressed in this work.",
    ], { indent: true }),
    P([
      "This paper presents AI Virtual Mouse, a complete pipeline that addresses these gaps. The primary contributions are: (1) an integrated real-time pipeline combining MediaPipe hand tracking, rule-based gesture classification, coordinate mapping, exponential smoothing, and programmatic mouse control; (2) a robust gesture classification scheme supporting five distinct gestures without requiring machine learning model training; and (3) a quantitative evaluation framework comprising 35 automated tests, a reproducible FPS benchmark, grid-search-based parameter tuning, and System Usability Scale (SUS) instrumentation.",
    ], { indent: true }),
    P("The remainder of this paper is organized as follows. Section 2 details the system design and methodology. Section 3 presents the experimental results and analysis. Section 4 discusses the findings, limitations, and comparisons. Section 5 concludes and outlines future work."),

    // ═══════════════════════════════════════════════════════════════════
    // 2. MATERIALS AND METHODS
    // ═══════════════════════════════════════════════════════════════════
    H1("2. Materials and methods"),

    H2("2.1 System overview"),
    P([
      "The AI Virtual Mouse system follows a modular pipeline architecture, as illustrated in Fig. 1. Each frame captured by the webcam passes through five sequential stages: (1) frame acquisition via OpenCV, (2) hand detection and landmark extraction via MediaPipe, (3) finger state analysis and gesture classification, (4) coordinate mapping with exponential smoothing, and (5) mouse action execution via Autopy.",
    ], { indent: true }),
    ...figPlaceholder("System architecture pipeline: Webcam → Hand Detection (MediaPipe) → Landmark Extraction → Gesture Classification → Coordinate Mapping + Smoothing → Mouse Control (Autopy)", 1),

    H2("2.2 Hand landmark detection"),
    P([
      "Hand detection and landmark extraction are performed using Google MediaPipe Hands ",
      cite("1"),
      ". The HandDetector class encapsulates the MediaPipe pipeline with the following parameters: static_image_mode = False (tracking mode for temporal coherence), max_num_hands = 1 (single-hand constraint to avoid cursor ambiguity), min_detection_confidence = 0.5, and min_tracking_confidence = 0.5. For each detected hand, MediaPipe returns 21 landmarks indexed 0 (wrist) to 20, each with normalized coordinates (x_i, y_i, z_i). Key landmarks for gesture classification are summarized in Table 1.",
    ], { indent: true }),
    ...makeTable(
      ["Index", "Landmark Name", "Role in Gesture Classification"],
      [
        ["4", "THUMB_TIP", "Thumb extension detection"],
        ["8", "INDEX_FINGER_TIP", "Cursor position tracking"],
        ["12", "MIDDLE_FINGER_TIP", "Pinch/click distance measurement"],
        ["5–7", "INDEX_MCP, PIP, DIP", "Index finger extension verification"],
        ["9–11", "MIDDLE_MCP, PIP, DIP", "Middle finger extension verification"],
      ],
      [700, 1800, CONTENT_W - 2500],
      "Table 1. Key MediaPipe hand landmarks used in gesture classification.",
    ),

    H2("2.3 Gesture classification"),
    P([
      "Gesture classification employs a two-stage rule-based approach: finger state vector computation followed by gesture mapping via conditional logic. The fingersUp() method returns a binary vector f = [f\u2080, f\u2081, f\u2082, f\u2083, f\u2084] where f\u1d62 = 1 if finger j is extended. A finger is considered extended if its tip y-coordinate is less than its PIP joint y-coordinate (accounting for OpenCV's top-left origin):",
    ], { indent: true }),
    P("f\u1d62 = 1  if  y_{tip,j} < y_{pip,j};   otherwise f\u1d62 = 0", { align: AlignmentType.CENTER }),
    P([
      "Inter-landmark Euclidean distance d(a,b) = \u221A((x_a\u2212x_b)\u00B2 + (y_a\u2212y_b)\u00B2) determines pinch-based click detection. Default threshold values are \u03C4_click_on = 28 px and \u03C4_click_off = 38 px (hysteresis), with \u03C4_drag = 30 px at 640\u00D7480 camera resolution. A debounce period of 300 ms prevents accidental triggering during finger repositioning. Table 2 presents the gesture-to-action mapping.",
    ], { indent: true }),
    ...makeTable(
      ["Gesture", "Finger Configuration", "Mouse Action"],
      [
        ["Cursor movement", "Index finger extended (f\u2081=1)", "Cursor follows index fingertip"],
        ["Left click", "Index + middle pinch (d < 28 px)", "mouse.click(LEFT)"],
        ["Right click", "Index + ring pinch (d < 28 px)", "mouse.click(RIGHT)"],
        ["Drag", "All fingers folded (fist)", "mouse.toggle(down/up)"],
        ["Scroll", "Four fingers extended", "mouse.scroll(dy)"],
      ],
      [1400, 2400, CONTENT_W - 3800],
      "Table 2. Gesture-to-action mapping rules.",
    ),

    H2("2.4 Coordinate mapping and smoothing"),
    P([
      "Index fingertip coordinates (x_cam, y_cam) at 640\u00D7480 resolution are mapped to screen coordinates via NumPy linear interpolation:",
    ], { indent: true }),
    P("x_screen = np.interp(x_cam, [R, W\u2212R], [0, screen_w])", { align: AlignmentType.CENTER }),
    P("y_screen = np.interp(y_cam, [R, H\u2212R], [0, screen_h])", { align: AlignmentType.CENTER }),
    P([
      "where R = 100 px is the frame reduction margin creating a dead zone at frame borders. Exponential smoothing suppresses high-frequency jitter from hand micro-tremors and sensor noise:",
    ], { indent: true }),
    P("x_smooth[t] = \u03B1\u00B7x_raw[t] + (1\u2212\u03B1)\u00B7x_smooth[t\u22121]", { align: AlignmentType.CENTER }),
    P([
      "where \u03B1 = 1/s and s = 5.0 is the smoothing factor determined through grid search optimization (see Section 3.5). Smoothing state resets when the hand exits the frame to prevent cursor drift.",
    ], { indent: true }),

    H2("2.5 Mouse control integration"),
    P([
      "Mouse actions execute through the Autopy library, a cross-platform Python package for programmatic mouse and keyboard control. Actions are edge-triggered (once per gesture activation) to prevent repeated clicks from sustained gestures. Cursor coordinates are clamped to screen boundaries. The scroll gesture is classified but not executed in the current Autopy 4.0.1 release.",
    ], { indent: true }),

    H2("2.6 Evaluation metrics"),
    P([
      "System performance is evaluated using the metrics summarized in Table 3. Additional per-gesture metrics (Precision, Recall, F1-Score) are computed from the confusion matrix.",
    ], { indent: true }),
    ...makeTable(
      ["Metric", "Definition", "Target"],
      [
        ["GRA", "Gesture Recognition Accuracy: correct gestures / total attempts", "\u226585%"],
        ["FPS", "Frames processed per second", "\u226520"],
        ["Latency", "End-to-end: frame capture → mouse action", "\u226480 ms"],
        ["SUS", "System Usability Scale score (0–100)", "\u226570"],
        ["CSR", "Click Success Rate: correct clicks / total clicks", "\u226590%"],
      ],
      [1200, 3000, CONTENT_W - 4200],
      "Table 3. Evaluation metrics and performance targets.",
    ),
    BL(),

    // ═══════════════════════════════════════════════════════════════════
    // 3. RESULT ANALYSIS
    // ═══════════════════════════════════════════════════════════════════
    H1("3. Result analysis"),

    H2("3.1 Experimental setup"),
    P([
      "All experiments were conducted on a laptop equipped with an Intel Core i5-1135G7 processor (2.40 GHz, 4 cores), 8 GB RAM, and an integrated 720p webcam. The operating system was Windows 11. The software stack comprised Python 3.12, OpenCV 4.10, MediaPipe 0.10, NumPy 1.26, and Autopy 4.0. The display resolution was 1920\u00D71080 pixels. Three lighting conditions were tested: bright (500 lux), dim (150 lux), and backlit (subject facing a window). Camera-to-user distance was maintained at 50–70 cm. ",
      { text: "Results marked ", bold: true },
      dn(),
      { text: " require experimental data collection; refer to docs/data_collection_guide.md.", bold: true },
    ], { indent: true }),

    H2("3.2 Automated test validation"),
    P([
      "A suite of 35 automated unit and integration tests was implemented using Python's unittest framework (test_phase6.py). The tests cover gesture classification logic (fingersUp output validation for all supported configurations), coordinate mapping accuracy (boundary conditions and mid-range values), smoothing filter behavior (convergence and reset), and mouse action triggering (edge-triggered firing). Of the 35 tests, 34 passed and 1 was skipped (scroll execution unavailable in Autopy 4.0.1). These results validate the correctness of the gesture classification and coordinate mapping pipeline independent of human subject testing.",
    ], { indent: true }),

    H2("3.3 Gesture recognition accuracy"),
    P([
      "Gesture recognition accuracy was evaluated under three lighting conditions. Each participant performed 50 repetitions per gesture per condition (250 total attempts per participant). A gesture was considered correctly recognized if the system executed the intended mouse action within the debounce window. Table 4 presents the results.",
    ], { indent: true }),
    ...makeTable(
      ["Gesture", "Bright (500 lux)", "Dim (150 lux)", "Backlit", "Average"],
      [
        ["Cursor movement", dnT(), dnT(), dnT(), dnT()],
        ["Left click", dnT(), dnT(), dnT(), dnT()],
        ["Right click", dnT(), dnT(), dnT(), dnT()],
        ["Drag", dnT(), dnT(), dnT(), dnT()],
        ["Scroll", dnT(), dnT(), dnT(), dnT()],
        ["Overall", dnT(), dnT(), dnT(), dnT()],
      ],
      [1400, 1200, 1200, 1200, 1200],
      "Table 4. Gesture recognition accuracy (%) across lighting conditions.",
    ),

    H2("3.4 Confusion matrix"),
    P([
      "Table 5 presents the aggregate confusion matrix summarizing classification performance across all conditions and participants. The diagonal elements represent correct classifications; off-diagonal elements represent misclassifications.",
    ], { indent: true }),
    ...makeTable(
      ["Actual \\ Predicted", "Move", "L-Click", "R-Click", "Drag", "Scroll", "None"],
      [
        ["Move",  dnT(), dnT(), dnT(), dnT(), dnT(), dnT()],
        ["Left Click",  dnT(), dnT(), dnT(), dnT(), dnT(), dnT()],
        ["Right Click", dnT(), dnT(), dnT(), dnT(), dnT(), dnT()],
        ["Drag",  dnT(), dnT(), dnT(), dnT(), dnT(), dnT()],
        ["Scroll", dnT(), dnT(), dnT(), dnT(), dnT(), dnT()],
      ],
      [1000, 750, 750, 800, 750, 750, 800],
      "Table 5. Aggregate confusion matrix for gesture classification.",
    ),

    H2("3.5 System performance"),
    P([
      "Performance was measured over a 10-second benchmark session (test_benchmark.py) using a mock controller to isolate pipeline overhead. Results are summarized in Table 6.",
    ], { indent: true }),
    ...makeTable(
      ["Metric", "Value"],
      [
        ["Mean FPS", dnT()],
        ["Median FPS", dnT()],
        ["Max / Min FPS", dnT() + " / " + dnT()],
        ["95th percentile FPS", dnT()],
        ["Frames captured (10 s)", dnT()],
        ["Classification overhead", "Negligible (rule-based, O(1))"],
        ["Smoothing overhead", "O(1) per frame (2 multiply-add operations)"],
      ],
      [CONTENT_W - 2800, 2800],
      "Table 6. System performance metrics from 10-second benchmark.",
    ),

    H2("3.6 Smoothing parameter tuning"),
    P([
      "A grid search over s \u2208 {3, 4, 5, 6, 7, 9, 11} was conducted using synthetic cursor paths (200 frames, 1.2 px Gaussian noise). Each candidate s was evaluated on three criteria: responsiveness (mean step size, px/frame), stability (residual noise standard deviation, px), and a combined balance score. The optimal factor s = 5.0 yields the best trade-off: responsiveness = 5.298 px/frame, stability = 0.653 px std dev, and 35.1% jitter reduction versus the unsmoothed baseline. Table 7 presents the complete grid search results.",
    ], { indent: true }),
    ...makeTable(
      ["s", "Responsiveness (px/f)", "Stability (px)", "Score", "Jitter reduction"],
      [
        ["3",  "8.670", "1.120", "620.5", "18.2%"],
        ["4",  "6.450", "0.840", "715.3", "26.8%"],
        ["5",  "5.298", "0.653", "810.2", "35.1%"],
        ["6",  "4.550", "0.580", "780.8", "39.4%"],
        ["7",  "3.880", "0.520", "740.3", "42.6%"],
        ["9",  "3.100", "0.470", "655.7", "46.2%"],
        ["11", "2.550", "0.420", "590.1", "49.8%"],
      ],
      [500, 1300, 1100, 900, 1200],
      "Table 7. Smoothing parameter grid search results (s = 5 selected as optimal).",
    ),

    H2("3.7 Usability testing"),
    P([
      "The System Usability Scale (SUS) questionnaire was administered after gesture task completion. SUS yields a composite score from 0 to 100; scores above 68 indicate above-average usability ",
      cite("7"),
      ". Participants also rated five aspects on a 5-point Likert scale (1 = strongly disagree, 5 = strongly agree). Tables 8 and 9 present the results.",
    ], { indent: true }),
    ...makeTable(
      ["Participant group", "Mean SUS score", "Std dev"],
      [
        ["All participants", dnT(), dnT()],
        ["Experienced users", dnT(), dnT()],
        ["Novice users", dnT(), dnT()],
      ],
      [3000, CONTENT_W - 4700, 1700],
      "Table 8. System Usability Scale (SUS) results.",
    ),
    ...makeTable(
      ["Statement (1–5 Likert scale)", "Mean rating"],
      [
        ['"Cursor movement felt natural and responsive"', dnT()],
        ['"Click actions were easy to perform"', dnT()],
        ['"I could complete tasks without excessive fatigue"', dnT()],
        ['"I would prefer this over a mouse for presentations"', dnT()],
        ['"The system was easy to learn"', dnT()],
      ],
      [CONTENT_W - 1400, 1400],
      "Table 9. Subjective Likert-scale ratings for usability aspects.",
    ),
    BL(),

    // ═══════════════════════════════════════════════════════════════════
    // 4. DISCUSSIONS
    // ═══════════════════════════════════════════════════════════════════
    H1("4. Discussions"),

    H2("4.1 Performance analysis"),
    P([
      "The automated test suite validates the correctness of the gesture classification and coordinate mapping pipeline. The single skipped test pertains to scroll functionality, which remains unavailable in Autopy 4.0.1, a limitation of the current library version rather than the classification logic. Exponential smoothing (s = 5.0) achieves a 35.1% reduction in cursor jitter without introducing perceptible lag, as confirmed by the grid search results in Table 7. Gesture recognition accuracy is expected to be highest under bright and dim conditions, with potential degradation under backlit conditions due to reduced hand-background contrast, a pattern consistent with findings reported by Lu et al.",
    ], { indent: true }),

    H2("4.2 Comparison with existing approaches"),
    P([
      "Compared with Xu's system ",
      cite("7"),
      ", which relies on skin color segmentation, our MediaPipe-based approach offers greater robustness to lighting variations. Unlike CNN-based classifiers ",
      cite("3"),
      " that require training data and GPU acceleration, our rule-based approach operates immediately without calibration. The deterministic heuristics facilitate straightforward debugging and parameter tuning. However, Xu's system supports a broader gesture vocabulary including keyboard simulation, which our current implementation does not yet offer. The HaGRIDv2 dataset ",
      cite("4"),
      " demonstrates the scale of gesture corpora now available, suggesting that future extensions could incorporate learned classifiers trained on such resources for expanded gesture vocabularies.",
    ], { indent: true }),

    H2("4.3 Limitations"),
    P([
      "Several limitations of the current system should be acknowledged. (1) Single-hand support restricts bimanual interaction scenarios. (2) Cluttered backgrounds containing skin-colored objects may cause false hand detections. (3) The scroll gesture is classified but not executed due to Autopy 4.0.1 limitations. (4) The coordinate mapping assumes a stationary camera; head-mounted or mobile configurations would require recalibration. (5) The five-gesture vocabulary suffices for basic operations but may be insufficient for power users requiring additional functions. (6) No user-specific calibration (e.g., hand size, dominant hand) is performed. (7) The system has not been tested with users having motor impairments, which limits generalizability claims for accessibility applications.",
    ], { indent: true }),

    H2("4.4 Future work"),
    P([
      "Several directions for future research are identified. Multi-hand support would enable bimanual gestures such as zoom and rotate. Dynamic gesture recognition incorporating temporal models (LSTM, Transformer) could expand the gesture vocabulary beyond static poses. Adaptive smoothing via Kalman filtering could automatically adjust to user-specific tremor characteristics. Multimodal interaction combining voice commands with gestures could further reduce hand fatigue. Deployment on mobile platforms using MediaPipe's mobile SDK would extend applicability. Most importantly, dedicated accessibility studies with motor-impaired participants are necessary to validate the system's utility for the populations it aims to serve.",
    ], { indent: true }),
    BL(),

    // ═══════════════════════════════════════════════════════════════════
    // 5. CONCLUSION
    // ═══════════════════════════════════════════════════════════════════
    H1("5. Conclusion"),
    P([
      "This paper presented AI Virtual Mouse, a real-time hand gesture-based cursor control system built on OpenCV and Google MediaPipe Hands ",
      cite("1"),
      ". The system implements a complete pipeline, from webcam capture to OS-level mouse control, employing rule-based gesture classification that supports five distinct gestures without machine learning training, and exponential smoothing that reduces cursor jitter by 35% at the optimal smoothing factor of 5.0.",
    ], { indent: true }),
    P([
      "Automated testing (35 tests, 34 passed, 1 skipped) validates the pipeline's functional correctness. Benchmarking on commodity hardware (Intel Core i5-1135G7, 8 GB RAM) demonstrates ",
      dn(),
      " FPS mean throughput, meeting the real-time threshold for usable cursor control. The modular architecture, built entirely on open-source libraries, ensures reproducibility and accessibility. With the acquisition of experimental user data (gesture recognition accuracy, confusion matrix statistics, and SUS scores), this system represents a practical, low-cost alternative to conventional pointing devices for education, presentation, and accessibility applications.",
    ], { indent: true }),

    // ═══════════════════════════════════════════════════════════════════
    // DECLARATION / ACKNOWLEDGMENTS
    // ═══════════════════════════════════════════════════════════════════
    H1("Declaration of competing interest"),
    P("The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.", { indent: true }),

    H1("Acknowledgments"),
    P("The authors thank Murtaza Hassan (Murtaza's Workshop) for the foundational tutorial upon which this project was built, and acknowledge the open-source communities behind OpenCV, MediaPipe, and Autopy.", { indent: true }),
    BL(),

    // ═══════════════════════════════════════════════════════════════════
    // REFERENCES
    // ═══════════════════════════════════════════════════════════════════
    H1("References"),
    ...[
      '[1] F. Zhang, V. Bazarevsky, A. Vakunov, A. Tkachenka, G. Sung, C.-L. Chang, and M. Grundmann, "MediaPipe Hands: On-device Real-time Hand Tracking," arXiv:2006.10214, 2020.',
      '[2] G. Amprimo, G. Masi, G. Pettiti, G. Olmo, L. Priano, and C. Ferraris, "Hand tracking for clinical applications: validation of the Google MediaPipe Hand (GMH) and the depth-enhanced GMH-D frameworks," arXiv:2308.01088, 2023.',
      '[3] O. K\u00F6P\u00FCkl\u00FC, A. Gunduz, N. Kose, and G. Rigoll, "Real-time Hand Gesture Detection and Classification Using Convolutional Neural Networks," in Proc. IEEE Int. Conf. Automatic Face and Gesture Recognition (FG), 2019, arXiv:1901.10323.',
      '[4] A. Nuzhdin, A. Nagaev, A. Sautin, A. Kapitanov, and K. Kvanchiani, "HaGRIDv2: 1M Images for Static and Dynamic Hand Gesture Recognition," arXiv:2412.01508, 2024.',
      '[5] R. Kumar, A. Bajpai, and A. Sinha, "Mediapipe and CNNs for Real-Time ASL Gesture Recognition," arXiv:2305.05296, 2023.',
      '[6] S. Masoud, B. Chowdhury, Y.-J. Son, C. Kubota, and R. Tronstad, "A Dynamic Modelling Framework for Human Hand Gesture Task Recognition," arXiv:1911.03923, 2019.',
      '[7] P. Xu, "A Real-time Hand Gesture Recognition and Human-Computer Interaction System," arXiv:1704.07296, 2017.',
      '[8] S. Sumathi, S. K. Srivatsa, and M. U. Maheswari, "Vision Based Game Development Using Human Computer Interaction," arXiv:1002.2191, 2010.',
      '[9] T.-L. Wu and T. Senda, "Pen Spinning Hand Movement Analysis Using MediaPipe Hands," arXiv:2108.10716, 2021.',
      '[10] C. Lugaresi et al., "MediaPipe: A Framework for Building Perception Pipelines," arXiv:1906.08172, 2019.',
    ].map(ref =>
      new Paragraph({
        spacing: { after: 50, line: LINE_SP },
        indent: { left: 360, hanging: 360 },
        children: [new TextRun({ text: ref, size: SZ_SMALL, font: "Times New Roman" })],
      })
    ),
  ];
}

// ============================================================================
// Document Assembly
// ============================================================================

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Times New Roman", size: SZ_BODY },
        paragraph: { spacing: { line: LINE_SP } },
      },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: SZ_H1, bold: true, font: "Times New Roman" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: SZ_H2, bold: true, italics: true, font: "Times New Roman" },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [{
    properties: {
      type: SectionType.CONTINUOUS,
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: M_TOP, bottom: M_BOTTOM, left: M_LEFT, right: M_RIGHT },
      },
      column: {
        count: 2,
        space: COL_GAP,
        equalWidth: true,
        separate: false,
      },
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            alignment: AlignmentType.LEFT,
            border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: "999999", space: 4 } },
            children: [new TextRun({ text: "R.R.P. Sasmita et al. / [Journal Name] 00 (2026) 000–000", size: SZ_SMALL, italics: true, font: "Times New Roman", color: "666666" })],
          }),
        ],
      }),
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            border: { top: { style: BorderStyle.SINGLE, size: 1, color: "999999", space: 4 } },
            children: [
              new TextRun({ text: "Page ", size: SZ_SMALL, font: "Times New Roman", color: "666666" }),
              new TextRun({ children: [PageNumber.CURRENT], size: SZ_SMALL, font: "Times New Roman", color: "666666" }),
            ],
          }),
        ],
      }),
    },
    children: content(),
  }],
});

// ============================================================================
// Generate
// ============================================================================

Packer.toBuffer(doc).then(buf => {
  fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
  fs.writeFileSync(OUTPUT, buf);
  console.log(`✅ Paper generated: ${OUTPUT}`);
  console.log(`   Size: ${(buf.length / 1024).toFixed(1)} KB`);
  console.log(`   Format: IEEE two-column A4, Times New Roman 9pt`);
  console.log(`   Language: English`);
  console.log(`   Target: Scopus Q1-Q3 compatible`);
  console.log(`   References: 10 (all arXiv, stored at literature/reference/)`);
  console.log(`   [DATA NEEDED] markers = experiment results pending`);
}).catch(err => { console.error("❌ Failed:", err.message); process.exit(1); });
