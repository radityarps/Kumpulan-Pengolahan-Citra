/**
 * AI Virtual Mouse — Presentation PPTX Generator
 * Dosen penguji / sidang, 10-15 menit, campuran ID+EN
 * Fokus: Evolusi arsitektur dari monolithic ke modular
 */
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Raditya";
pres.title = "AI Virtual Mouse — Evolusi Arsitektur Hand Gesture Recognition";

// ─── Color Palette (Dark Tech Theme) ───
const C = {
  bgDark:    "1A1A2E",  // deep navy (title slides)
  bgMid:     "16213E",  // dark blue (section bg)
  bgCard:    "1E2D3D",  // card backgrounds
  bgLight:   "F5F7FA",  // light content bg
  accent:    "00BCD4",  // cyan accent
  accent2:   "FF6F61",  // warm coral (highlights)
  accent3:   "4CAF50",  // green (improvement)
  accent4:   "FFC107",  // amber (warning)
  textWhite: "FFFFFF",
  textLight: "B0BEC5",
  textDark:  "263238",
  textMuted: "78909C",
  border:    "2A3A4A",
};

// ─── Helper: factory for shadow objects ───
const makeShadow = () => ({ type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.20 });

// ─── Helper: add footer to slide ───
function addFooter(slide, text) {
  slide.addText(text || "AI Virtual Mouse — Presentasi Sidang", {
    x: 0.5, y: 5.2, w: 9, h: 0.3,
    fontSize: 8, color: C.textMuted, fontFace: "Calibri", align: "left"
  });
}

// ─── Helper: section divider slide ───
function sectionSlide(title, subtitle, chapterNum) {
  const slide = pres.addSlide();
  slide.background = { color: C.bgDark };

  // Accent bar left
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.08, h: 5.625, fill: { color: C.accent }
  });

  // Chapter number
  slide.addText(chapterNum, {
    x: 0.8, y: 0.8, w: 1.2, h: 0.8,
    fontSize: 48, fontFace: "Arial Black", color: C.accent, bold: true, margin: 0
  });

  // Title
  slide.addText(title, {
    x: 0.8, y: 1.7, w: 8.5, h: 1.0,
    fontSize: 32, fontFace: "Calibri", color: C.textWhite, bold: true, margin: 0
  });

  // Subtitle
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.8, y: 2.5, w: 8.5, h: 0.5,
      fontSize: 14, fontFace: "Calibri", color: C.textLight, margin: 0
    });
  }
  return slide;
}

// ─── Helper: content slide with dark header bar ───
function contentSlide(title) {
  const slide = pres.addSlide();
  slide.background = { color: C.bgLight };

  // Top accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent }
  });

  // Title
  slide.addText(title, {
    x: 0.6, y: 0.25, w: 8.8, h: 0.6,
    fontSize: 24, fontFace: "Calibri", color: C.bgDark, bold: true, margin: 0
  });

  return slide;
}

// ─── Helper: what/why/how card trio ───
function addWWHCards(slide, y, what, why, how) {
  const cardW = 2.85, cardH = 2.5, gap = 0.2, startX = 0.55;
  const cards = [
    { label: "WHAT", text: what, color: C.accent },
    { label: "WHY", text: why, color: C.accent2 },
    { label: "HOW", text: how, color: C.accent3 },
  ];

  cards.forEach((c, i) => {
    const cx = startX + i * (cardW + gap);
    // Card bg
    slide.addShape(pres.shapes.RECTANGLE, {
      x: cx, y, w: cardW, h: cardH,
      fill: { color: C.bgCard }, shadow: makeShadow()
    });
    // Label accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: cx, y, w: cardW, h: 0.06, fill: { color: c.color }
    });
    // Label text
    slide.addText(c.label, {
      x: cx + 0.15, y: y + 0.2, w: cardW - 0.3, h: 0.35,
      fontSize: 11, fontFace: "Arial Black", color: c.color, bold: true, margin: 0
    });
    // Content text
    slide.addText(c.text, {
      x: cx + 0.15, y: y + 0.55, w: cardW - 0.3, h: cardH - 0.7,
      fontSize: 10, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "top"
    });
  });
}


// ═══════════════════════════════════════════════════════════
// SLIDE 1: TITLE
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = pres.addSlide();
  slide.background = { color: C.bgDark };

  // Top decorative line
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.8, y: 1.0, w: 2.5, h: 0.06, fill: { color: C.accent }
  });

  slide.addText("AI Virtual Mouse", {
    x: 0.8, y: 1.2, w: 8.5, h: 1.0,
    fontSize: 40, fontFace: "Arial Black", color: C.textWhite, bold: true, margin: 0
  });

  slide.addText("Evolusi Arsitektur Hand Gesture Recognition\ndari Monolithic ke Modular", {
    x: 0.8, y: 2.2, w: 8.5, h: 1.0,
    fontSize: 18, fontFace: "Calibri", color: C.textLight, margin: 0
  });

  slide.addText("Pengolahan Citra — Semester 6", {
    x: 0.8, y: 3.6, w: 8.5, h: 0.4,
    fontSize: 13, fontFace: "Calibri", color: C.accent, margin: 0
  });

  slide.addText("Raditya", {
    x: 0.8, y: 4.2, w: 8.5, h: 0.4,
    fontSize: 16, fontFace: "Calibri", color: C.textWhite, margin: 0
  });
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 2: AGENDA
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Agenda");

  const items = [
    { num: "01", title: "Latar Belakang", desc: "Mengapa virtual mouse? Konteks HCI & touchless interaction." },
    { num: "02", title: "Implementasi Sesuai Video", desc: "Replikasi 1:1 tutorial Murtaza's Workshop — MediaPipe Solutions API." },
    { num: "03", title: "Fine Tuning pada Video Version", desc: "Perbaikan bug, penyesuaian gesture, optimasi parameter." },
    { num: "04", title: "Implementasi Modular (Final)", desc: "Arsitektur 8 modul + test suite — MediaPipe Tasks API." },
    { num: "05", title: "Kesimpulan", desc: "Ringkasan evolusi & key takeaways." },
  ];

  items.forEach((item, i) => {
    const y = 1.1 + i * 0.85;
    // Number circle
    slide.addShape(pres.shapes.OVAL, {
      x: 0.6, y: y + 0.05, w: 0.45, h: 0.45,
      fill: { color: i === 0 ? C.accent : C.bgCard }
    });
    slide.addText(item.num, {
      x: 0.6, y: y + 0.05, w: 0.45, h: 0.45,
      fontSize: 14, fontFace: "Arial Black", color: i === 0 ? C.textWhite : C.accent,
      align: "center", valign: "middle", margin: 0
    });
    // Connector line
    if (i < items.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: 0.825, y: y + 0.5, w: 0, h: 0.35,
        line: { color: C.border, width: 1, dashType: "dash" }
      });
    }
    // Title
    slide.addText(item.title, {
      x: 1.3, y: y, w: 8, h: 0.28,
      fontSize: 15, fontFace: "Calibri", color: C.bgDark, bold: true, margin: 0
    });
    // Description
    slide.addText(item.desc, {
      x: 1.3, y: y + 0.28, w: 8, h: 0.4,
      fontSize: 10, fontFace: "Calibri", color: C.textMuted, margin: 0
    });
  });

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 3: LATAR BELAKANG — WHAT/WHY/HOW
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Latar Belakang: Mengapa AI Virtual Mouse?");

  addWWHCards(slide, 1.1,
    "Sistem kontrol kursor berbasis computer vision yang menggunakan gestur tangan sebagai pengganti mouse fisik.\n\nTeknologi: OpenCV + MediaPipe + Autopy.",
    "Touchless HCI makin relevan pasca-COVID. Aksesibilitas untuk pengguna dengan keterbatasan motorik. Presentasi & kiosk publik tanpa kontak fisik.\n\n843K+ views — validasi minat komunitas.",
    "Webcam → Hand Detection (MediaPipe 21 landmarks) → Finger State Analysis → Gesture Classification → Coordinate Mapping + Smoothing → Mouse Control (Autopy)."
  );

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 4: IMPLEMENTASI VIDEO — OVERVIEW
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Implementasi Sesuai Video Tutorial (Murtaza's Workshop)");

  // WHAT card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 1.05, w: 4.3, h: 3.8, fill: { color: C.bgCard }, shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 1.05, w: 4.3, h: 0.06, fill: { color: C.accent }
  });
  slide.addText("WHAT — Replikasi 1:1", {
    x: 0.7, y: 1.25, w: 4, h: 0.35,
    fontSize: 13, fontFace: "Arial Black", color: C.accent, bold: true, margin: 0
  });
  slide.addText([
    { text: "Kode identik dengan tutorial YouTube", options: { bullet: true, breakLine: true } },
    { text: "MediaPipe Solutions API (mp.solutions.hands)", options: { bullet: true, breakLine: true } },
    { text: "Dua file: HandTrackingModule.py + AIVirtualMouse.py", options: { bullet: true, breakLine: true } },
    { text: "4 gesture: Move, Left Click, Right Click, Scroll", options: { bullet: true, breakLine: true } },
    { text: "Thumb detection: x-coordinate comparison", options: { bullet: true, breakLine: true } },
    { text: "Smoothing: exponential moving average", options: { bullet: true } },
  ], {
    x: 0.7, y: 1.7, w: 3.9, h: 3.0,
    fontSize: 10, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "top",
    paraSpaceAfter: 6
  });

  // WHY + HOW card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.15, y: 1.05, w: 4.3, h: 3.8, fill: { color: C.bgCard }, shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.15, y: 1.05, w: 4.3, h: 0.06, fill: { color: C.accent2 }
  });
  slide.addText("WHY — Starting Point", {
    x: 5.3, y: 1.25, w: 4, h: 0.35,
    fontSize: 13, fontFace: "Arial Black", color: C.accent2, bold: true, margin: 0
  });
  slide.addText([
    { text: "Tutorial paling populer (843K views)", options: { breakLine: true } },
    { text: "Kode sederhana — mudah dipahami", options: { breakLine: true } },
    { text: "Proof of concept: gesture → cursor works", options: { breakLine: true } },
    { text: "Baseline untuk perbandingan", options: { breakLine: true } },
    { text: "", options: { breakLine: true, fontSize: 6 } },
    { text: "HOW — Arsitektur", options: { bold: true, color: C.accent2, breakLine: true } },
    { text: "Webcam → HandDetector.findHands()", options: { breakLine: true } },
    { text: "→ findPosition() → fingersUp()", options: { breakLine: true } },
    { text: "→ np.interp() → autopy.mouse.move()", options: { breakLine: true } },
    { text: "Single-loop, no state machine", options: { color: C.accent4 } },
  ], {
    x: 5.3, y: 1.7, w: 3.9, h: 3.0,
    fontSize: 10, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "top",
    paraSpaceAfter: 4
  });

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 5: IMPLEMENTASI VIDEO — GESTURE + CODE
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Gesture Mapping & Kode Video (Asli)");

  // Gesture table
  const tableData = [
    [
      { text: "Gesture", options: { bold: true, color: C.accent, fill: { color: C.bgDark } } },
      { text: "Finger State", options: { bold: true, color: C.accent, fill: { color: C.bgDark } } },
      { text: "Action", options: { bold: true, color: C.accent, fill: { color: C.bgDark } } },
    ],
    ["Move", "[1, 1, 0, 0, 0]  index up", "Cursor mengikuti telunjuk"],
    ["Left Click", "[1, 1, 1, 0, 0]  pinch < 40px", "autopy.mouse.click()"],
    ["Right Click", "[1, 1, 1, 1, 1]  all 5 fingers", "autopy.mouse.click(RIGHT)"],
    ["Scroll", "[1, 1, *, *, *]  thumb+index", "autopy.mouse.toggle(down=True)"],
  ];

  slide.addTable(tableData, {
    x: 0.55, y: 1.05, w: 4.3, h: 2.8,
    border: { pt: 0.5, color: C.border },
    colW: [1.4, 1.55, 1.35],
    rowH: [0.45, 0.55, 0.55, 0.55, 0.55],
    fontFace: "Calibri", fontSize: 9.5, color: C.textDark,
    autoPage: false,
  });

  // Code snippet box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.15, y: 1.05, w: 4.3, h: 3.8, fill: { color: C.bgDark }, shadow: makeShadow()
  });
  slide.addText("Kode Inti — fingersUp()", {
    x: 5.3, y: 1.15, w: 4, h: 0.3,
    fontSize: 10, fontFace: "Calibri", color: C.accent, bold: true, margin: 0
  });
  slide.addText(
    "def fingersUp(self):\n" +
    "  fingers = []\n" +
    "  # Thumb: x-coordinate\n" +
    "  if tip[4].x > tip[3].x:\n" +
    "    fingers.append(1)\n" +
    "  # Other fingers: y-coordinate\n" +
    "  for id in [8,12,16,20]:\n" +
    "    if tip[id].y < pip[id].y:\n" +
    "      fingers.append(1)\n" +
    "  return fingers",
    {
      x: 5.3, y: 1.5, w: 4, h: 3.2,
      fontSize: 8.5, fontFace: "Consolas", color: C.textLight,
      margin: 0, valign: "top"
    }
  );

  // Warning callout
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 4.05, w: 4.3, h: 0.65, fill: { color: "332A1A" }
  });
  slide.addText([
    { text: "\u26A0  Masalah: ", options: { bold: true, color: C.accent4 } },
    { text: "Thumb detection handedness-dependent.\n", options: { breakLine: true } },
    { text: "Scroll pakai toggle() — bukan scroll sebenarnya.", options: {} },
  ], {
    x: 0.7, y: 4.1, w: 4, h: 0.55,
    fontSize: 9, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "top"
  });

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 6: FINE TUNING — WHAT CHANGED
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Fine Tuning pada Video Version: Perubahan dari Kode Asli");

  addWWHCards(slide, 1.1,
    "6 perbaikan + penyesuaian pada kode video tanpa mengubah arsitektur single-loop.\n\nGesture mapping diganti ke practical_no_thumb (abaikan thumb).\n\nScroll fix: ctypes Windows API.",
    "Bug pada kode asli:\n\u2022 Thumb unreliable\n\u2022 Scroll tidak berfungsi\n\u2022 Kursor inverted\n\u2022 Drag tidak ada\n\u2022 Right click terlalu mudah trigger (5 jari)",
    "1. cv2.flip(img,1) + direct coords\n2. Gesture mapping baru\n3. ctypes MOUSEEVENTF_WHEEL\n4. Drag anchor-based\n5. Edge-trigger click\n6. Threshold tuning (28px/34px)"
  );

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 7: FINE TUNING — BEFORE/AFTER COMPARISON
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Fine Tuning: Before vs After");

  // BEFORE column
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 1.05, w: 4.3, h: 4.0, fill: { color: C.bgCard }, shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 1.05, w: 4.3, h: 0.06, fill: { color: C.accent4 }
  });
  slide.addText("SEBELUM (Kode Video Asli)", {
    x: 0.7, y: 1.25, w: 4, h: 0.35,
    fontSize: 12, fontFace: "Arial Black", color: C.accent4, bold: true, margin: 0
  });

  const beforeItems = [
    ["Kamera", "No flip \u2192 x inverted (wScr - clocX)"],
    ["Gesture Move", "[1,1,0,0,0]  index up only"],
    ["Gesture Click", "[1,1,1,0,0]  index+middle pinch"],
    ["Gesture Right", "[1,1,1,1,1]  all 5 fingers up"],
    ["Gesture Scroll", "[1,1,*,*,*]  thumb+index, pakai toggle()"],
    ["Gesture Drag", "Tidak ada"],
    ["Thumb", "x-coordinate comparison"],
    ["Click logic", "Langsung klik tiap frame distance<40"],
  ];

  beforeItems.forEach((item, i) => {
    const y = 1.7 + i * 0.4;
    slide.addText(item[0], {
      x: 0.7, y, w: 1.1, h: 0.35,
      fontSize: 9, fontFace: "Calibri", color: C.accent4, bold: true, margin: 0
    });
    slide.addText(item[1], {
      x: 1.8, y, w: 2.9, h: 0.35,
      fontSize: 9, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "middle"
    });
  });

  // AFTER column
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.15, y: 1.05, w: 4.3, h: 4.0, fill: { color: C.bgCard }, shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.15, y: 1.05, w: 4.3, h: 0.06, fill: { color: C.accent3 }
  });
  slide.addText("SESUDAH (Fine Tuned)", {
    x: 5.3, y: 1.25, w: 4, h: 0.35,
    fontSize: 12, fontFace: "Arial Black", color: C.accent3, bold: true, margin: 0
  });

  const afterItems = [
    ["Kamera", "cv2.flip(img,1) \u2192 natural movement"],
    ["Gesture Move", "[*,1,0,0,0]  thumb ignored"],
    ["Gesture Click", "[*,1,1,0,0]  pinch < 28px"],
    ["Gesture Right", "[*,1,1,1,0]  index+ring pinch"],
    ["Gesture Scroll", "[*,1,1,1,1]  camera center boundary"],
    ["Gesture Drag", "[*,0,0,0,0]  fist, anchor-based"],
    ["Thumb", "Tetap x-coordinate, tetapi diabaikan (*)"],
    ["Click logic", "Edge-triggered (click_ready flag)"],
  ];

  afterItems.forEach((item, i) => {
    const y = 1.7 + i * 0.4;
    slide.addText(item[0], {
      x: 5.3, y, w: 1.1, h: 0.35,
      fontSize: 9, fontFace: "Calibri", color: C.accent3, bold: true, margin: 0
    });
    slide.addText(item[1], {
      x: 6.4, y, w: 2.9, h: 0.35,
      fontSize: 9, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "middle"
    });
  });

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 8: MASALAH MONOLITHIC
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Keterbatasan Arsitektur Monolithic (Video Version)");

  const problems = [
    { icon: "\u2716", title: "Tidak Ada Debounce", desc: "Satu frame flicker = mode switch. Drag drop saat jari sedikit bergerak.", color: C.accent2 },
    { icon: "\u2716", title: "Tidak Ada Hysteresis", desc: "Click trigger pada single threshold crossing. Tidak ada hold-time verification.", color: C.accent2 },
    { icon: "\u2716", title: "Tidak Ada Hand-Lost Grace", desc: "Satu frame tanpa tangan = semua state reset. Drag anchor hilang.", color: C.accent2 },
    { icon: "\u2716", title: "Tidak Testable", desc: "Semua logic dalam satu main loop. Tidak bisa unit test gesture classifier terpisah.", color: C.accent2 },
    { icon: "\u2716", title: "Parameter Hardcoded", desc: "Threshold, smoothing, dead zone tersebar di kode. Tuning = edit kode.", color: C.accent2 },
    { icon: "\u2716", title: "Drag Jittery", desc: "Tracking curled index finger (landmark 8) — MediaPipe kurang akurat untuk jari terlipat.", color: C.accent2 },
  ];

  problems.forEach((p, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.55 + col * 4.6;
    const y = 1.05 + row * 1.2;

    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.3, h: 1.0, fill: { color: C.bgCard }, shadow: makeShadow()
    });
    slide.addText(p.icon + "  " + p.title, {
      x: x + 0.15, y: y + 0.08, w: 4.0, h: 0.28,
      fontSize: 12, fontFace: "Calibri", color: p.color, bold: true, margin: 0
    });
    slide.addText(p.desc, {
      x: x + 0.15, y: y + 0.38, w: 4.0, h: 0.5,
      fontSize: 9, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "top"
    });
  });

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 9: MODULAR — WHAT
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Implementasi Modular: Arsitektur Final");

  addWWHCards(slide, 1.1,
    "8 modul independen + 33 unit tests + benchmark + dokumentasi lengkap.\n\nGestureClassifier, CoordinateMapper, MouseController, GestureProfiles — masing-masing Single Responsibility.",
    "Monolithic tidak bisa: di-test, di-extend, di-maintain.\n\nNeed: debounce, hysteresis, hold-time gating, gesture profiles, post-click freeze, hand-lost grace.\n\nDosen perlu lihat software engineering practice.",
    "Fase 1-7 implementation plan:\n\u2022 Fase 1: HandTrackingModule (Tasks API)\n\u2022 Fase 2: GestureClassifier\n\u2022 Fase 3: CoordinateMapper\n\u2022 Fase 4: MouseController\n\u2022 Fase 5: Main loop integration\n\u2022 Fase 6: Testing + tuning\n\u2022 Fase 7: Article + docs"
  );

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 10: MODULAR — ARCHITECTURE DIAGRAM
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Arsitektur Modular: Dependency Graph");

  // Architecture flow diagram
  const modules = [
    { name: "ai_virtual_mouse.py", desc: "Main Loop", x: 3.2, y: 0.5, w: 3.6, color: C.accent },
    { name: "config.py", desc: "Constants", x: 0.4, y: 2.3, w: 1.8, color: C.textMuted },
    { name: "hand_tracking_module.py", desc: "HandDetector\n(MediaPipe Tasks API)", x: 2.5, y: 2.3, w: 2.2, color: C.accent3 },
    { name: "gesture_classifier.py", desc: "GestureClassifier\n(rule-based + hysteresis)", x: 5.0, y: 2.3, w: 2.2, color: C.accent2 },
    { name: "coordinate_mapper.py", desc: "CoordinateMapper\n(interp + smoothing)", x: 2.5, y: 4.0, w: 2.2, color: C.accent3 },
    { name: "mouse_controller.py", desc: "MouseController\n(Autopy wrapper)", x: 5.0, y: 4.0, w: 2.2, color: C.accent2 },
    { name: "gesture_profiles.py", desc: "Profile Maps", x: 7.5, y: 2.3, w: 1.8, color: C.textMuted },
    { name: "utils.py", desc: "FPS + Overlay", x: 7.5, y: 4.0, w: 1.8, color: C.textMuted },
  ];

  modules.forEach(m => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: m.x, y: m.y, w: m.w, h: 0.8,
      fill: { color: C.bgCard }, shadow: makeShadow(),
      line: { color: m.color, width: 1.5 }
    });
    slide.addText(m.name, {
      x: m.x + 0.1, y: m.y + 0.05, w: m.w - 0.2, h: 0.3,
      fontSize: 9, fontFace: "Consolas", color: m.color, bold: true, margin: 0
    });
    slide.addText(m.desc, {
      x: m.x + 0.1, y: m.y + 0.35, w: m.w - 0.2, h: 0.4,
      fontSize: 8, fontFace: "Calibri", color: C.textLight, margin: 0
    });
  });

  // Arrows (simplified as lines)
  const arrows = [
    { x: 4.3, y: 1.3, w: 0, h: 0.9 },  // main → hand_tracking
    { x: 5.0, y: 1.3, w: 1.1, h: 0 },   // main → gesture
    { x: 3.6, y: 3.1, w: 0, h: 0.8 },   // hand_tracking → coord
    { x: 5.0, y: 3.1, w: 1.1, h: 0 },   // gesture → mouse
    { x: 6.1, y: 3.1, w: 0, h: 0.8 },   // gesture → coord
  ];

  arrows.forEach(a => {
    if (a.w === 0) {
      slide.addShape(pres.shapes.LINE, {
        x: a.x, y: a.y, w: 0, h: a.h,
        line: { color: C.border, width: 1, dashType: "dash" }
      });
    } else {
      slide.addShape(pres.shapes.LINE, {
        x: a.x, y: a.y, w: a.w, h: 0,
        line: { color: C.border, width: 1, dashType: "dash" }
      });
    }
  });

  // Right side: key improvements
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 0.9, w: 2.5, h: 1.2, fill: { color: C.bgDark }
  });
  slide.addText("Key Improvements", {
    x: 0.55, y: 0.95, w: 2.2, h: 0.25,
    fontSize: 10, fontFace: "Arial Black", color: C.accent, bold: true, margin: 0
  });
  slide.addText([
    { text: "\u2714 Debounce 300ms", options: { breakLine: true } },
    { text: "\u2714 Hysteresis ON/OFF", options: { breakLine: true } },
    { text: "\u2714 Hold-time 100ms", options: { breakLine: true } },
    { text: "\u2714 Post-click freeze", options: { breakLine: true } },
    { text: "\u2714 Hand-lost grace 4f", options: {} },
  ], {
    x: 0.55, y: 1.25, w: 2.2, h: 0.8,
    fontSize: 8.5, fontFace: "Calibri", color: C.accent3, margin: 0, valign: "top",
    paraSpaceAfter: 2
  });

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 11: PERBANDINGAN API + EVOLUSI
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = contentSlide("Evolusi Teknologi: MediaPipe API & Arsitektur");

  // API comparison table
  slide.addText("MediaPipe API: Solutions vs Tasks", {
    x: 0.55, y: 1.05, w: 9, h: 0.3,
    fontSize: 13, fontFace: "Arial Black", color: C.bgDark, bold: true, margin: 0
  });

  const apiTable = [
    [{ text: "Aspek", options: { bold: true, fill: { color: C.bgDark }, color: C.accent } },
     { text: "Solutions API (Video)", options: { bold: true, fill: { color: C.bgDark }, color: C.accent4 } },
     { text: "Tasks API (Final)", options: { bold: true, fill: { color: C.bgDark }, color: C.accent3 } }],
    ["Import", "mp.solutions.hands", "mediapipe.tasks.vision.HandLandmarker"],
    ["Input", "numpy RGB array langsung", "mp.Image (konversi eksplisit)"],
    ["Model", "Bundled dalam package", "File .task terpisah (7.8 MB)"],
    ["Drawing", "mp.solutions.drawing_utils", "Custom _draw_landmarks()"],
    ["Status", "Deprecated (0.10.0+)", "Production-ready, maintained"],
  ];

  slide.addTable(apiTable, {
    x: 0.55, y: 1.45, w: 8.9, h: 2.0,
    border: { pt: 0.5, color: C.border },
    colW: [2.0, 3.45, 3.45],
    rowH: [0.35, 0.3, 0.3, 0.3, 0.3],
    fontFace: "Calibri", fontSize: 9, color: C.textDark,
  });

  // Evolution timeline
  slide.addText("Evolusi Arsitektur", {
    x: 0.55, y: 3.65, w: 9, h: 0.3,
    fontSize: 13, fontFace: "Arial Black", color: C.bgDark, bold: true, margin: 0
  });

  const timeline = [
    { label: "Video\nOriginal", desc: "1 file\n140 lines\n4 gestures\nNo tests", color: C.accent4 },
    { label: "Video\nFine-Tuned", desc: "2 files\n6 gestures\nBug fixes\nEdge-trigger", color: C.accent },
    { label: "Main\nProject", desc: "8 modules\n33 tests\nHysteresis\nDebounce", color: C.accent3 },
  ];

  timeline.forEach((t, i) => {
    const tx = 1.5 + i * 3.0;
    // Circle
    slide.addShape(pres.shapes.OVAL, {
      x: tx + 0.5, y: 4.1, w: 0.5, h: 0.5, fill: { color: t.color }
    });
    slide.addText(String(i + 1), {
      x: tx + 0.5, y: 4.1, w: 0.5, h: 0.5,
      fontSize: 16, fontFace: "Arial Black", color: C.textWhite,
      align: "center", valign: "middle", margin: 0
    });
    // Connector line
    if (i < 2) {
      slide.addShape(pres.shapes.LINE, {
        x: tx + 1.0, y: 4.35, w: 2.0, h: 0,
        line: { color: C.border, width: 2 }
      });
    }
    // Label
    slide.addText(t.label, {
      x: tx, y: 4.7, w: 1.5, h: 0.5,
      fontSize: 9, fontFace: "Calibri", color: C.bgDark, bold: true, align: "center", margin: 0
    });
    // Description
    slide.addText(t.desc, {
      x: tx - 0.2, y: 5.0, w: 1.9, h: 0.5,
      fontSize: 8, fontFace: "Calibri", color: C.textMuted, align: "center", margin: 0
    });
  });

  addFooter(slide);
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 12: KESIMPULAN
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = pres.addSlide();
  slide.background = { color: C.bgDark };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent }
  });

  slide.addText("Kesimpulan", {
    x: 0.8, y: 0.4, w: 8.5, h: 0.7,
    fontSize: 32, fontFace: "Arial Black", color: C.textWhite, bold: true, margin: 0
  });

  const conclusions = [
    { icon: "1", title: "Dari Monolithic ke Modular", desc: "Evolusi bukan sekadar refactor — setiap modul menyelesaikan masalah spesifik yang ditemukan di versi monolithic." },
    { icon: "2", title: "Gesture Recognition Bukan Hanya Deteksi", desc: "Debounce, hysteresis, hold-time gating sama pentingnya dengan akurasi deteksi jari untuk UX yang stabil." },
    { icon: "3", title: "API Deprecation is Real", desc: "MediaPipe Solutions API dihapus dalam 2 tahun. Migrasi ke Tasks API adalah keputusan teknis yang tepat, bukan preferensi." },
  ];

  conclusions.forEach((c, i) => {
    const y = 1.3 + i * 1.3;
    // Number
    slide.addShape(pres.shapes.OVAL, {
      x: 0.8, y: y + 0.05, w: 0.5, h: 0.5, fill: { color: C.accent }
    });
    slide.addText(c.icon, {
      x: 0.8, y: y + 0.05, w: 0.5, h: 0.5,
      fontSize: 18, fontFace: "Arial Black", color: C.textWhite,
      align: "center", valign: "middle", margin: 0
    });
    // Title
    slide.addText(c.title, {
      x: 1.5, y: y, w: 7.5, h: 0.3,
      fontSize: 16, fontFace: "Calibri", color: C.textWhite, bold: true, margin: 0
    });
    // Description
    slide.addText(c.desc, {
      x: 1.5, y: y + 0.3, w: 7.5, h: 0.5,
      fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0, valign: "top"
    });
  });
})();

// ═══════════════════════════════════════════════════════════
// SLIDE 13: Q&A
// ═══════════════════════════════════════════════════════════
(function() {
  const slide = pres.addSlide();
  slide.background = { color: C.bgDark };

  // Centered content
  slide.addText("Terima Kasih", {
    x: 1, y: 1.5, w: 8, h: 1.0,
    fontSize: 40, fontFace: "Arial Black", color: C.textWhite, bold: true,
    align: "center", valign: "middle", margin: 0
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.5, y: 2.6, w: 3, h: 0.06, fill: { color: C.accent }
  });

  slide.addText("Q & A", {
    x: 1, y: 2.9, w: 8, h: 0.8,
    fontSize: 24, fontFace: "Calibri", color: C.accent,
    align: "center", valign: "middle", margin: 0
  });

  slide.addText("AI Virtual Mouse — Pengolahan Citra — Semester 6", {
    x: 1, y: 4.5, w: 8, h: 0.4,
    fontSize: 11, fontFace: "Calibri", color: C.textMuted,
    align: "center", margin: 0
  });
})();


// ─── WRITE FILE ───
const outPath = "D:\\Files\\Documents\\Kuliah\\Semester 6\\Pengolahan Citra\\AI Virtual Mouse\\AI_Virtual_Mouse_Presentation.pptx";
pres.writeFile({ fileName: outPath })
  .then(() => console.log("DONE: " + outPath))
  .catch(err => console.error("ERROR:", err));
