# AI Virtual Mouse — Rencana Implementasi (Implementation Plan)

**Dokumen turunan dari:** `docs/PRD.md` v1.0 — 11 Mei 2026  
**Tanggal rencana:** 11 Mei 2026  
**Status:** Ready for execution

---

## Daftar Isi

1. [Ringkasan Target MVP](#1-ringkasan-target-mvp)
2. [Arsitektur File & Dependensi](#2-arsitektur-file--dependensi)
3. [Fase Implementasi](#3-fase-implementasi)
   - [Fase 0: Environment & Project Scaffold](#fase-0-environment--project-scaffold-15-jam)
   - [Fase 1: HandTrackingModule](#fase-1-handtrackingmodule-2-3-jam)
   - [Fase 2: GestureClassifier](#fase-2-gestureclassifier-3-4-jam)
   - [Fase 3: CoordinateMapper + Smoothing](#fase-3-coordinatemapper--smoothing-2-3-jam)
   - [Fase 4: MouseController](#fase-4-mousecontroller-1-2-jam)
   - [Fase 5: Main Loop Integration + UI Overlay](#fase-5-main-loop-integration--ui-overlay-3-5-jam)
   - [Fase 6: Testing & Parameter Tuning](#fase-6-testing--parameter-tuning-4-6-jam)
   - [Fase 7: Dokumentasi & Artikel](#fase-7-dokumentasi--artikel-6-10-jam)
4. [Urutan Eksekusi & Dependencies](#4-urutan-eksekusi--dependencies)
5. [Spesifikasi Detail Tiap Modul](#5-spesifikasi-detail-tiap-modul)
6. [Konfigurasi & Constants](#6-konfigurasi--constants)
7. [Test Plan](#7-test-plan)
8. [Risk Register](#8-risk-register)
9. [Definition of Done per Fase](#9-definition-of-done-per-fase)

---

## 1. Ringkasan Target MVP

Berdasarkan PRD §10.1, **Minimal Viable Product** adalah:

| #   | MVP Criterion                                                                          | Komponen                                  |
| --- | -------------------------------------------------------------------------------------- | ----------------------------------------- |
| M1  | Webcam capture + hand landmark detection berfungsi                                     | `hand_tracking_module.py` + OpenCV loop   |
| M2  | Gestur Move (telunjuk+tengah) dan Click (telunjuk) berfungsi                           | `gesture_classifier.py`                   |
| M3  | Coordinate mapping + exponential smoothing terintegrasi                                | `coordinate_mapper.py`                    |
| M4  | Mouse control (move + left click) via Autopy                                           | `mouse_controller.py`                     |
| M5  | Kode modular, terdokumentasi, dapat dijalankan dengan `python src/ai_virtual_mouse.py` | `ai_virtual_mouse.py` + `utils.py`        |
| M6  | Artikel ilmiah selesai dengan placeholder hasil eksperimen                             | `article/01_draft.md` (fill placeholders) |

**Fitur Fase 2 (Stretch Goals — PRD §10.2):**

- Right-click, Drag, Scroll
- GUI control panel (opsional ekstra)

---

## 2. Arsitektur File & Dependensi

### 2.1 Struktur Source Final

```
src/
├── ai_virtual_mouse.py        # Main loop, integrasi semua modul
├── hand_tracking_module.py    # Class HandDetector (wrapper MediaPipe)
├── gesture_classifier.py      # Class GestureClassifier (fingersUp, findDistance, rule logic)
├── coordinate_mapper.py       # Class CoordinateMapper (interpolasi + smoothing)
├── mouse_controller.py        # Class MouseController (wrapper Autopy)
├── config.py                  # Semua konstanta, threshold, magic numbers
└── utils.py                   # FPS counter, overlay text, frame decoration
```

### 2.2 Dependency Graph

```
ai_virtual_mouse.py
 ├── config.py                   (konstanta global)
 ├── utils.py                    (FPS, overlay)
 ├── hand_tracking_module.py     (→ MediaPipe, OpenCV)
 │    └── config.py
 ├── gesture_classifier.py       (→ hand_tracking_module untuk lmList)
 │    └── config.py
 ├── coordinate_mapper.py        (→ NumPy, config)
 │    └── config.py
 └── mouse_controller.py         (→ Autopy, config)
      └── config.py
```

### 2.3 Library Versions (dari PRD §6.3)

| Library         | Minimum | Target Install |
| --------------- | ------- | -------------- |
| `opencv-python` | 4.5+    | 4.10+          |
| `mediapipe`     | 0.8.10+ | 0.10+          |
| `numpy`         | 1.19+   | 1.26+          |
| `autopy`        | 4.0.0   | 4.0.0          |

---

## 3. Fase Implementasi

### Fase 0: Environment & Project Scaffold (~1.5 jam)

**Tujuan:** Semua dependensi terinstall, struktur folder siap, `config.py` terdefinisi, `utils.py` memiliki fungsi dasar overlay.

**Langkah:**

1. **Buat virtual environment**

   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   ```

2. **Install dependensi**

   ```bash
   pip install opencv-python mediapipe numpy autopy
   pip freeze > requirements.txt
   ```

3. **Buat `src/config.py`** — Semua konstanta dari PRD dikumpulkan di satu file:
   - Resolusi kamera: `FRAME_WIDTH=640`, `FRAME_HEIGHT=480`
   - Threshold MediaPipe: `MIN_DETECTION_CONFIDENCE=0.7`, `MIN_TRACKING_CONFIDENCE=0.5`
   - Max hands: `MAX_NUM_HANDS=1`
   - Smoothing factor: `SMOOTHING_FACTOR=7`
   - Click threshold: `CLICK_THRESHOLD_PX=40`
   - Drag threshold: `DRAG_THRESHOLD_PX=30`
   - Frame reduction margin: `FRAME_REDUCTION=100`
   - Debounce period: `DEBOUNCE_TIME_MS=300`
   - Scroll sensitivity: `SCROLL_SENSITIVITY=2`

4. **Buat `src/utils.py`** — Fungsi helper:
   - `put_fps(img, fps, pos)` — overlay FPS di frame
   - `put_mode_text(img, mode, pos)` — overlay "Move Mode" / "Click Mode" / "Drag Mode" / "Scroll Mode" / "None"
   - `draw_landmark_toggle(img, lmList, connections, toggle)` — gambar landmark + koneksi jika toggle=True
   - `draw_bounding_box(img, bbox, color)` — visualisasi bounding box tangan (opsional)

5. **Buat `requirements.txt`** dari `pip freeze`

**Definition of Done:**

- [ ] `python -c "import cv2; import mediapipe; import numpy; import autopy"` berhasil tanpa error
- [ ] `config.py` dan `utils.py` ada, dengan semua konstanta dan fungsi helper
- [ ] Webcam dapat dibuka dan menampilkan video feed (quick smoke test)

---

### Fase 1: HandTrackingModule (~2-3 jam)

**Tujuan:** Class `HandDetector` yang membungkus MediaPipe Hands, menyediakan method `findHands()`, `findPosition()`, dan `fingersUp()`.

**Rancangan Class:**

```python
class HandDetector:
    """
    Wrapper untuk MediaPipe Hands.
    Menggunakan static_image_mode=False, max_num_hands=1,
    min_detection_confidence=0.7, min_tracking_confidence=0.5.
    """
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]  # ujung jari

    def findHands(self, img, draw=True):
        """Deteksi tangan di frame. Return img (dengan/tanpa gambar landmark)."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        return img

    def findPosition(self, img, hand_no=0, draw=True):
        """Return list lmList dengan (id, x_px, y_px) + bounding box bbox."""
        self.lmList = []
        if self.results.multi_hand_landmarks:
            h, w, c = img.shape
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            # Hitung bounding box
            x_list = [lm[1] for lm in self.lmList]
            y_list = [lm[2] for lm in self.lmList]
            if x_list and y_list:
                bbox = min(x_list), min(y_list), max(x_list), max(y_list)
                return self.lmList, bbox
        return [], (0, 0, 0, 0)

    def fingersUp(self):
        """Return list [thumb, index, middle, ring, pinky] masing-masing 0/1."""
        fingers = []
        if len(self.lmList) == 0:
            return [0, 0, 0, 0, 0]
        # Thumb: bandingkan x-coordinate tip (4) vs IP joint (3)
        if self.lmList[self.tip_ids[0]][1] > self.lmList[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 jari lainnya: bandingkan y-coordinate tip vs PIP joint (tip_id - 2)
        for tip_id in self.tip_ids[1:]:
            if self.lmList[tip_id][2] < self.lmList[tip_id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img=None, draw=True):
        """Hitung Euclidean distance antara landmark p1 dan p2."""
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        distance = math.hypot(x2 - x1, y2 - y1)
        if draw and img is not None:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        return distance, (cx, cy), (x1, y1, x2, y2)
```

**Validasi:**

- Smoke test: jalankan loop sederhana yang membaca webcam, panggil `findHands()` + `findPosition()`, tampilkan landmark, cetak `fingersUp()` ke konsol setiap frame.
- Pastikan mapping finger state benar: angkat telunjuk saja → `[0, 1, 0, 0, 0]`, telunjuk+tengah → `[0, 1, 1, 0, 0]`, dst.

**Definition of Done:**

- [ ] Class `HandDetector` di `hand_tracking_module.py`
- [ ] Method `findHands()`, `findPosition()`, `fingersUp()`, `findDistance()` berfungsi
- [ ] Diuji dengan webcam: landmark terlihat, fingersUp konsisten benar

---

### Fase 2: GestureClassifier (~3-4 jam)

**Tujuan:** Class `GestureClassifier` yang menerima `lmList`, `fingersUp`, dan jarak antar landmark, lalu mengembalikan gesture mode dan perintah mouse. Menerapkan debounce 300ms.

**Rancangan Class:**

```python
class GestureClassifier:
    """
    Rule-based gesture classification.
    Input: lmList, fingers array, distances
    Output: gesture_mode string + action trigger boolean
    """
    def __init__(self, click_threshold=40, drag_threshold=30, debounce_ms=300):
        self.click_threshold = click_threshold
        self.drag_threshold = drag_threshold
        self.debounce_ms = debounce_ms
        # State tracking untuk debounce
        self.current_mode = "None"
        self.mode_start_time = 0  # timestamp saat mode berubah
        self.stable_mode = "None"
        # Untuk click edge-triggered
        self.click_ready = True
        self.drag_active = False
        self.last_scroll_y = None

    def classify(self, fingers, lmList, findDistance_fn):
        """
        Kembalikan (mode, action).
        mode: "Move", "Click", "RightClick", "Drag", "Scroll", "None"
        action: "move", "click", "right_click", "drag_start", "drag_end", "scroll", None
        """
        if not lmList:
            return "None", None

        # Dapatkan jarak yang diperlukan
        dist_idx_mid, _, _ = findDistance_fn(8, 12, draw=False)
        dist_idx_thumb, _, _ = findDistance_fn(4, 8, draw=False)

        # --- Mode Detection ---
        detected_mode = "None"
        action = None

        if fingers == [0, 1, 1, 0, 0]:
            # Index + Middle up = Move Mode
            # Jika drag sedang aktif dan jarak kecil → drag
            if self.drag_active:
                detected_mode = "Drag"
                if dist_idx_thumb > self.drag_threshold:
                    action = "drag_end"
                    self.drag_active = False
                else:
                    action = "move"  # drag movement
            else:
                detected_mode = "Move"
                action = "move"

        elif fingers == [0, 1, 0, 0, 0]:
            # Only Index up = Click Mode
            detected_mode = "Click"
            if dist_idx_mid < self.click_threshold and self.click_ready:
                action = "click"
                self.click_ready = False
            elif dist_idx_mid >= self.click_threshold:
                self.click_ready = True

        elif fingers == [0, 0, 1, 0, 0]:
            # Only Middle up = Right Click Mode
            detected_mode = "RightClick"
            if dist_idx_mid < self.click_threshold and self.click_ready:
                action = "right_click"
                self.click_ready = False
            elif dist_idx_mid >= self.click_threshold:
                self.click_ready = True

        elif fingers == [0, 1, 1, 1, 0]:
            # Three fingers up = Drag Mode (initiate)
            detected_mode = "Drag"
            if not self.drag_active and dist_idx_thumb < self.drag_threshold:
                action = "drag_start"
                self.drag_active = True

        elif fingers == [0, 1, 1, 1, 1]:
            # Four fingers up = Scroll Mode
            detected_mode = "Scroll"
            # Hitung scroll dari delta y index finger (landmark 8)
            if self.last_scroll_y is not None:
                delta_y = self.last_scroll_y - lmList[8][2]
                if abs(delta_y) > 5:  # dead zone
                    scroll_amount = delta_y // self.scroll_sensitivity
                    action = ("scroll", scroll_amount)
            self.last_scroll_y = lmList[8][2]

        else:
            detected_mode = "None"
            self.last_scroll_y = None
            if self.drag_active:
                action = "drag_end"
                self.drag_active = False

        # --- Debounce Logic ---
        now = time.time() * 1000  # ms
        if detected_mode != self.current_mode:
            self.current_mode = detected_mode
            self.mode_start_time = now
        else:
            if now - self.mode_start_time >= self.debounce_ms:
                self.stable_mode = detected_mode

        return self.stable_mode, action
```

**Edge cases yang harus diatasi:**

- Tangan hilang dari frame → reset semua state, mode="None", `drag_active=False`, `last_scroll_y=None`
- Transisi cepat antar gesture → debounce mencegah false trigger
- Click berulang karena user menahan jari → `click_ready` flag untuk edge-triggered
- Scroll saat tangan pertama kali terdeteksi → `last_scroll_y` diinisialisasi saat masuk Scroll mode

**Definition of Done:**

- [ ] `GestureClassifier.classify()` mengembalikan (mode, action) yang benar
- [ ] Debounce 300ms berfungsi
- [ ] Click edge-triggered (tidak auto-repeat)
- [ ] Semua transisi state ditangani (None ↔ Move ↔ Click ↔ Drag ↔ Scroll)
- [ ] Unit test sederhana dengan mock `lmList` dan `findDistance_fn`

---

### Fase 3: CoordinateMapper + Smoothing (~2-3 jam)

**Tujuan:** Class `CoordinateMapper` yang melakukan interpolasi dari koordinat kamera ke koordinat layar, plus exponential smoothing.

**Rancangan Class:**

```python
class CoordinateMapper:
    """
    Maps hand landmark coordinates from camera space (640×480)
    to screen space (detected via autopy.screen.size()).
    Applies exponential smoothing to reduce jitter.
    """
    def __init__(self, frame_width=640, frame_height=480,
                 frame_reduction=100, smoothing_factor=7):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_reduction = frame_reduction
        self.smoothing_factor = smoothing_factor

        # Dapatkan resolusi layar aktual
        self.screen_width, self.screen_height = autopy.screen.size()

        # State smoothing
        self.smooth_x = 0
        self.smooth_y = 0
        self.initialized = False

    def map_to_screen(self, cx, cy):
        """
        Interpolasi (cx, cy) kamera ke (screen_x, screen_y).
        Formula:
          x_screen = np.interp(cx, [frame_red, w - frame_red], [0, screen_w])
          y_screen = np.interp(cy, [frame_red, h - frame_red], [0, screen_h])
        """
        x = np.interp(cx,
                      [self.frame_reduction, self.frame_width - self.frame_reduction],
                      [0, self.screen_width])
        y = np.interp(cy,
                      [self.frame_reduction, self.frame_height - self.frame_reduction],
                      [0, self.screen_height])
        return x, y

    def smooth(self, raw_x, raw_y):
        """
        Exponential smoothing:
          smooth[t] = smooth[t-1] + (raw - smooth[t-1]) / smoothing_factor
        Inisialisasi langsung pada frame pertama.
        """
        if not self.initialized:
            self.smooth_x = raw_x
            self.smooth_y = raw_y
            self.initialized = True
        else:
            self.smooth_x = self.smooth_x + (raw_x - self.smooth_x) / self.smoothing_factor
            self.smooth_y = self.smooth_y + (raw_y - self.smooth_y) / self.smoothing_factor
        return self.smooth_x, self.smooth_y

    def reset_smoothing(self):
        """Reset state smoothing (dipanggil saat tangan hilang)."""
        self.initialized = False

    def process(self, cx, cy):
        """Full pipeline: map → smooth → return screen coords."""
        raw_x, raw_y = self.map_to_screen(cx, cy)
        return self.smooth(raw_x, raw_y)
```

**Catatan penting:**

- Smoothing di-reset saat tangan hilang (via `reset_smoothing()`) — dari PRD N9: kursor tidak boleh bergerak liar saat tangan tidak terdeteksi.
- Frame reduction menciptakan dead zone di tepi frame — dari PRD §3.4.1.
- Screen resolution auto-detected via `autopy.screen.size()`.
- Smoothing O(1) overhead, tidak signifikan terhadap FPS.

**Definition of Done:**

- [ ] `map_to_screen()` mengembalikan koordinat yang benar (verifikasi manual: tangan di kiri kamera → kursor di kiri layar)
- [ ] `smooth()` mengurangi jitter (uji: print raw vs smooth, lihat smooth lebih stabil)
- [ ] `reset_smoothing()` dipanggil → `initialized` jadi False
- [ ] Tidak crash jika screen resolution di atas 1080p

---

### Fase 4: MouseController (~1-2 jam)

**Tujuan:** Class `MouseController` yang membungkus Autopy, eksekusi perintah mouse berdasarkan action dari GestureClassifier.

**Rancangan Class:**

```python
class MouseController:
    """
    Wrapper untuk Autopy mouse control.
    Menerjemahkan action string ke API call.
    """
    def __init__(self, click_delay=0.1):
        self.click_delay = click_delay
        self.drag_active = False
        self.last_action = None
        self.last_action_time = 0

    def execute(self, action, screen_x=None, screen_y=None, **kwargs):
        """
        Eksekusi action:
          - "move": autopy.mouse.move(screen_x, screen_y)
          - "click": autopy.mouse.click()
          - "right_click": autopy.mouse.click(RIGHT)
          - "drag_start": autopy.mouse.toggle(True)
          - "drag_end": autopy.mouse.toggle(False)
          - "scroll": autopy.mouse.scroll(amount)
        """
        if screen_x is not None and screen_y is not None:
            # Clamp ke batas layar agar tidak error
            screen_x = max(0, min(screen_x, autopy.screen.size()[0] - 1))
            screen_y = max(0, min(screen_y, autopy.screen.size()[1] - 1))

        if action == "move":
            autopy.mouse.move(int(screen_x), int(screen_y))
        elif action == "click":
            autopy.mouse.click()
            time.sleep(self.click_delay)
        elif action == "right_click":
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
            time.sleep(self.click_delay)
        elif action == "drag_start":
            autopy.mouse.toggle(True, autopy.mouse.Button.LEFT)
        elif action == "drag_end":
            autopy.mouse.toggle(False, autopy.mouse.Button.LEFT)
        elif isinstance(action, tuple) and action[0] == "scroll":
            _, amount = action
            autopy.mouse.scroll(amount)

    def cleanup(self):
        """Pastikan tidak ada drag yang tertinggal saat exit."""
        if self.drag_active:
            autopy.mouse.toggle(False, autopy.mouse.Button.LEFT)
```

**Edge Cases:**

- Koordinat di-clamp ke screen boundary (hindari error Autopy)
- Cleanup drag saat program exit
- Click delay untuk mencegah double-click tidak sengaja

**Definition of Done:**

- [ ] `execute("move", x, y)` → kursor bergerak
- [ ] `execute("click")` → klik kiri terjadi
- [ ] `execute("right_click")` → klik kanan terjadi
- [ ] `execute("scroll", amount=N)` → scroll terjadi
- [ ] Koordinat negative di-clamp ke 0

---

### Fase 5: Main Loop Integration + UI Overlay (~3-5 jam)

**Tujuan:** Menggabungkan semua modul ke `ai_virtual_mouse.py`, menambahkan UI overlay (FPS, mode, visualisasi landmark), keyboard control.

**Rancangan Main Loop:**

```python
# ai_virtual_mouse.py

import cv2
import time
from hand_tracking_module import HandDetector
from gesture_classifier import GestureClassifier
from coordinate_mapper import CoordinateMapper
from mouse_controller import MouseController
from config import *
from utils import put_fps, put_mode_text, draw_landmark_toggle

def main():
    # --- Inisialisasi ---
    cap = cv2.VideoCapture(0)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)

    detector = HandDetector(max_hands=MAX_NUM_HANDS,
                            detection_con=MIN_DETECTION_CONFIDENCE,
                            track_con=MIN_TRACKING_CONFIDENCE)
    classifier = GestureClassifier(click_threshold=CLICK_THRESHOLD_PX,
                                   drag_threshold=DRAG_THRESHOLD_PX,
                                   debounce_ms=DEBOUNCE_TIME_MS)
    mapper = CoordinateMapper(frame_width=FRAME_WIDTH,
                              frame_height=FRAME_HEIGHT,
                              frame_reduction=FRAME_REDUCTION,
                              smoothing_factor=SMOOTHING_FACTOR)
    controller = MouseController()

    # State
    prev_time = 0
    show_landmarks = True  # Toggle dengan tombol 'l'

    print("[AI Virtual Mouse] Starting... Press 'q' to quit, 'l' to toggle landmarks.")

    while True:
        success, img = cap.read()
        if not success:
            print("[ERROR] Cannot read from webcam.")
            break

        # Flip horizontal untuk mirror (natural movement)
        img = cv2.flip(img, 1)

        # --- Pipeline ---
        # 1. Hand Detection
        img = detector.findHands(img, draw=show_landmarks)
        lmList, bbox = detector.findPosition(img, draw=show_landmarks)

        # 2. Gesture Classification
        if lmList:
            fingers = detector.fingersUp()
            # Injek findDistance sebagai callable
            mode, action = classifier.classify(
                fingers, lmList,
                lambda p1, p2, draw=False: detector.findDistance(p1, p2, draw=draw)
            )
        else:
            mode, action = "None", None
            mapper.reset_smoothing()
            classifier.stable_mode = "None"

        # 3. Coordinate Mapping + Smoothing + Mouse Control
        if lmList and mode == "Move":
            # Gunakan ujung telunjuk (landmark 8) untuk posisi kursor
            ix, iy = lmList[8][1], lmList[8][2]
            smooth_x, smooth_y = mapper.process(ix, iy)
            controller.execute("move", smooth_x, smooth_y)

        elif lmList and mode == "Click" and action == "click":
            controller.execute("click")

        elif lmList and mode == "RightClick" and action == "right_click":
            controller.execute("right_click")

        elif lmList and mode == "Drag":
            if action == "drag_start":
                controller.execute("drag_start")
            elif action == "drag_end":
                controller.execute("drag_end")
            elif action == "move":
                # Pindahkan kursor saat drag
                ix, iy = lmList[8][1], lmList[8][2]
                smooth_x, smooth_y = mapper.process(ix, iy)
                controller.execute("move", smooth_x, smooth_y)

        elif lmList and mode == "Scroll" and isinstance(action, tuple):
            controller.execute(action[0], amount=action[1])

        # 4. Overlay UI
        # FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        put_fps(img, int(fps))

        # Mode text
        put_mode_text(img, mode)

        # Show
        cv2.imshow("AI Virtual Mouse", img)

        # Keyboard control
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('l'):
            show_landmarks = not show_landmarks

    # Cleanup
    controller.cleanup()
    cap.release()
    cv2.destroyAllWindows()
    print("[AI Virtual Mouse] Shutdown complete.")

if __name__ == "__main__":
    main()
```

**UI Overlay Spesifikasi:**

- **FPS:** Pojok kiri atas, font `FONT_HERSHEY_SIMPLEX`, scale 1, warna hijau
- **Mode:** Pojok kanan atas, ukuran lebih besar, warna berbeda per mode:
  - Move: Hijau
  - Click: Biru
  - RightClick: Orange
  - Drag: Merah
  - Scroll: Kuning
  - None: Putih
- **Landmark toggle:** Tombol `l` di keyboard
- **Exit:** Tombol `q`

**Edge Cases di Main Loop:**

- `cap.read()` gagal → print error + break bersih
- Tangan hilang → mode="None", smooth di-reset, tidak ada mouse action
- Flip horizontal (`cv2.flip(img, 1)`) untuk mirror — gerakan tangan terasa natural

**Definition of Done:**

- [ ] Program berjalan: `python src/ai_virtual_mouse.py`
- [ ] Webcam feed terlihat
- [ ] Landmark muncul saat tangan terdeteksi
- [ ] Toggle landmark dengan `l`
- [ ] Kursor bergerak di Mode Move
- [ ] Klik terjadi di Mode Click
- [ ] Mode text overlay berubah sesuai gesture
- [ ] FPS counter real-time
- [ ] Exit bersih dengan `q`
- [ ] Tidak crash saat tangan hilang

---

### Fase 6: Testing & Parameter Tuning (~4-6 jam)

**Tujuan:** Validasi performa, tuning parameter, uji dengan berbagai kondisi.

**Test Cases (dari PRD §4 dan §5):**

#### 6.1 Functional Tests

| #   | Test Case                                         | Acceptance Criteria                             |
| --- | ------------------------------------------------- | ----------------------------------------------- |
| T1  | Tangan terdeteksi, telunjuk+tengah terangkat      | Mode="Move", kursor bergerak mengikuti telunjuk |
| T2  | Hanya telunjuk terangkat, dekatkan ke tengah      | Mode="Click", klik kiri terjadi                 |
| T3  | Hanya jari tengah terangkat, dekatkan ke telunjuk | Mode="RightClick", klik kanan terjadi           |
| T4  | 3 jari terangkat, dekatkan ibu jari-telunjuk      | Mode="Drag", drag dimulai                       |
| T5  | 4 jari terangkat, gerakkan tangan vertikal        | Mode="Scroll", scroll terjadi                   |
| T6  | Tangan ditarik keluar frame                       | Mode="None", kursor berhenti, tidak crash       |
| T7  | Transisi cepat Move → Click → Move                | Tidak ada false click, debounce berfungsi       |
| T8  | Menahan Click mode tanpa melepaskan jari          | Tidak auto-repeat click                         |
| T9  | Webcam tidak tersedia                             | Error message jelas, exit bersih                |
| T10 | Toggle landmark dengan `l`                        | Landmark on/off toggle berfungsi                |

#### 6.2 Performance Metrics

| Metric            | Target                    | Cara Ukur                                             |
| ----------------- | ------------------------- | ----------------------------------------------------- |
| FPS               | ≥ 20 FPS (PRD KR3)        | FPS counter di overlay, rata-rata 60 detik            |
| Latency           | ≤ 80 ms (PRD KR2)         | `time.time()` sebelum detect dan sesudah mouse action |
| CPU Usage         | ≤ 50% dual-core (PRD N3)  | Task Manager / `htop`                                 |
| Smoothing Quality | Jitter minimal, tidak lag | Uji visual + catat delta smooth vs raw                |

#### 6.3 Parameter Tuning Grid

| Parameter            | Default | Range Uji                | Catatan                                                    |
| -------------------- | ------- | ------------------------ | ---------------------------------------------------------- |
| `SMOOTHING_FACTOR`   | 7       | {5, 7, 9, 11, 15}        | Cari keseimbangan responsiveness vs stability              |
| `CLICK_THRESHOLD_PX` | 40      | {25, 30, 35, 40, 50, 60} | Terlalu kecil → false positive; terlalu besar → sulit klik |
| `DRAG_THRESHOLD_PX`  | 30      | {20, 25, 30, 40}         | Seperti click threshold                                    |
| `DEBOUNCE_TIME_MS`   | 300     | {150, 200, 300, 500}     | Terlalu kecil → jitter mode; terlalu besar → laggy         |
| `FRAME_REDUCTION`    | 100     | {50, 100, 150}           | Dead zone kenyamanan kursor                                |

**Tuning Process:**

1. Uji dengan 3 orang berbeda (beda ukuran tangan, kecepatan gerak)
2. Catat subjective feedback: "terlalu sensitif", "sulit klik", "laggy"
3. Tentukan nilai optimal berdasarkan majority preference
4. Update `config.py` dengan nilai final

#### 6.4 Usability Testing (SUS)

- Rekrut minimal 5 partisipan
- Berikan task standar: arahkan kursor ke 5 target di layar + klik
- Administer SUS questionnaire (10 pertanyaan)
- Hitung skor (target ≥ 70, PRD KR4)

**Definition of Done:**

- [ ] Semua T1-T10 pass
- [ ] FPS rata-rata ≥ 20
- [ ] Parameter final ditentukan dan dicatat
- [ ] SUS score terukur dan dicatat (untuk artikel)

---

### Fase 7: Dokumentasi & Artikel (~6-10 jam)

**Tujuan:** Melengkapi dokumentasi kode, README, dan artikel ilmiah.

#### 7.1 Code Documentation

- Docstring Google-style di setiap class dan method
- Komentar inline untuk logic yang kompleks
- Type hints Python 3.7+ (`def findPosition(self, img: np.ndarray, hand_no: int = 0) -> Tuple[List, Tuple]:`)

#### 7.2 README.md Update

- Tambah bagian "How to Run" yang lengkap
- Tambah screenshot / GIF demo
- Tambah troubleshooting section
- Tambah parameter tuning guide

#### 7.3 Artikel Ilmiah (article/01_draft.md)

- **Isi placeholder hasil eksperimen** di Section 4 (Experiments & Results):
  - Table 1: Gesture Recognition Accuracy → isi dengan data dari Fase 6
  - Table 2: Confusion Matrix
  - Table 3: System Performance (FPS, latency, memory, CPU)
  - Table 4: SUS results
- **Isi placeholder [N]**, **[XX]**, dsb dengan data aktual
- Finalisasi references, formatting
- Proofreading

**Definition of Done:**

- [ ] Semua class dan method memiliki docstring
- [ ] README lengkap dengan instruksi run, dependencies, troubleshooting
- [ ] Artikel ilmiah semua placeholder terisi dengan data eksperimen
- [ ] `requirements.txt` final

---

## 4. Urutan Eksekusi & Dependencies

```
Fase 0 (Scaffold)
   │
   ├──► Fase 1 (HandTrackingModule)
   │       │
   │       ├──► Fase 2 (GestureClassifier) ──┐
   │       │                                  │
   │       └──► Fase 3 (CoordinateMapper) ────┤
   │                                          │
   └──────► Fase 4 (MouseController) ─────────┘
                                               │
                                     Fase 5 (Integration)
                                               │
                                     Fase 6 (Testing)
                                               │
                                     Fase 7 (Docs & Article)
```

**Dependencies kritis:**

- Fase 1 HARUS selesai sebelum Fase 2 dan 3 (butuh `lmList` dan `findDistance`)
- Fase 2, 3, 4 bisa paralel (independen satu sama lain)
- Fase 5 HARUS menunggu Fase 1, 2, 3, 4
- Fase 6 HARUS menunggu Fase 5
- Fase 7 bisa mulai paralel dengan Fase 6 (artikel draft), tapi data eksperimen baru bisa diisi setelah Fase 6 selesai

**Estimasi total:** 22-32 jam (paruh waktu, cocok dengan estimasi PRD 4-6 minggu)

---

## 5. Spesifikasi Detail Tiap Modul

### 5.1 config.py — Constants

```python
# Kamera
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAMERA_ID = 0

# MediaPipe
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 1

# Gesture
CLICK_THRESHOLD_PX = 40
DRAG_THRESHOLD_PX = 30
DEBOUNCE_TIME_MS = 300
SCROLL_SENSITIVITY = 2

# Mapping
FRAME_REDUCTION = 100
SMOOTHING_FACTOR = 7

# Mouse
CLICK_DELAY = 0.1

# UI
FONT = cv2.FONT_HERSHEY_SIMPLEX
FPS_POS = (20, 70)
MODE_POS = (20, 120)
LANDMARK_VISIBLE_DEFAULT = True

# Warna (BGR)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_ORANGE = (0, 165, 255)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE = (255, 255, 255)
MODE_COLORS = {
    "None": COLOR_WHITE,
    "Move": COLOR_GREEN,
    "Click": COLOR_BLUE,
    "RightClick": COLOR_ORANGE,
    "Drag": COLOR_RED,
    "Scroll": COLOR_YELLOW,
}
```

### 5.2 utils.py — Helper Functions

```python
def put_fps(img, fps, pos=(20, 70), font=cv2.FONT_HERSHEY_SIMPLEX,
            scale=1, color=(0, 255, 0), thickness=2):
    cv2.putText(img, f"FPS: {fps}", pos, font, scale, color, thickness)

def put_mode_text(img, mode, pos=(20, 120), font=cv2.FONT_HERSHEY_PLAIN,
                  scale=2, thickness=2):
    color = MODE_COLORS.get(mode, COLOR_WHITE)
    cv2.putText(img, f"Mode: {mode}", pos, font, scale, color, thickness)
```

---

## 6. Konfigurasi & Constants

Seluruh magic number dan parameter di-_extract_ ke `config.py`. Tidak ada hardcoded value di modul lain. Ini memudahkan tuning tanpa mencari-cari di kode.

**Konvensi:**

- Semua konstanta UPPER_SNAKE_CASE
- Threshold dalam piksel (kecuali confidence 0-1)
- Waktu dalam milidetik

---

## 7. Test Plan

### 7.1 Unit Tests (Opsional tapi Disarankan)

| Modul               | Apa yang diuji                                                        |
| ------------------- | --------------------------------------------------------------------- |
| `GestureClassifier` | Mock `lmList` + `findDistance_fn` untuk setiap kombinasi finger state |
| `CoordinateMapper`  | Mock `autopy.screen.size()`, uji mapping dengan nilai known           |
| `MouseController`   | Mock `autopy.mouse`, verifikasi fungsi dipanggil dengan argumen benar |

### 7.2 Integration Test

- Smoke test: `python src/ai_virtual_mouse.py` → tidak crash, webcam terbuka
- End-to-end: Semua gesture dipicu satu per satu

### 7.3 Regression Test

- Setelah setiap perubahan parameter, smoke test ulang
- Pastikan tidak ada import error atau crash

---

## 8. Risk Register

| Risk (dari PRD §9)                           | Mitigasi Implementasi                                                                                                                        |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Akurasi gestur rendah karena pencahayaan** | Uji di 3 kondisi pencahayaan; dokumentasikan batasan di artikel; `MEDIAPIPE_CONFIDENCE` bisa diturunkan (trade-off false positive)           |
| **Jitter kursor berlebihan**                 | Sediakan `SMOOTHING_FACTOR` yang mudah diubah via `config.py`; rencana fallback: implementasi Kalman filter sederhana jika perlu             |
| **Kompatibilitas Autopy di Windows**         | Autopy v4.0.0 sudah stabil di Windows; uji di lingkungan target; fallback ke PyAutoGUI jika ada isu (`pip install pyautogui` + ganti import) |
| **FPS < 15**                                 | Kurangi `FRAME_WIDTH/HEIGHT` ke 480×360; nonaktifkan drawing landmark; gunakan `static_image_mode=True` jika tracking terlalu mahal          |
| **Library version conflict**                 | Gunakan virtual environment; pin versi di `requirements.txt`                                                                                 |
| **Waktu tidak cukup**                        | Fokus pada MVP (Move + Click); Drag, Scroll, RightClick bisa dikurangi jadi placeholder di kode                                              |

---

## 9. Definition of Done per Fase

### Fase 0 ✅

- [ ] Virtual environment aktif
- [ ] `pip list` menunjukkan opencv-python, mediapipe, numpy, autopy
- [ ] `requirements.txt` terbuat
- [ ] `src/config.py` dan `src/utils.py` terbuat
- [ ] Webcam smoke test OK

### Fase 1 ✅

- [ ] `HandDetector` class di `hand_tracking_module.py`
- [ ] Method `findHands()`, `findPosition()`, `fingersUp()`, `findDistance()` berfungsi
- [ ] Smoke test: landmark terlihat, fingersUp benar

### Fase 2 ✅

- [ ] `GestureClassifier` class di `gesture_classifier.py`
- [ ] 5 gestures terdeteksi (Move, Click, RightClick, Drag, Scroll)
- [ ] Debounce 300ms berfungsi
- [ ] Unit test lulus

### Fase 3 ✅

- [ ] `CoordinateMapper` class di `coordinate_mapper.py`
- [ ] Interpolasi benar, smoothing terasa
- [ ] Reset smoothing saat tangan hilang

### Fase 4 ✅

- [ ] `MouseController` class di `mouse_controller.py`
- [ ] Move, click, right-click, scroll berfungsi
- [ ] Cleanup drag saat exit

### Fase 5 ✅

- [ ] `ai_virtual_mouse.py` berjalan tanpa error
- [ ] Pipeline end-to-end berfungsi
- [ ] UI overlay: FPS, mode, landmark toggle
- [ ] Exit bersih dengan `q`

### Fase 6 ✅

- [ ] 10 functional tests pass
- [ ] FPS ≥ 20
- [ ] Parameter final ditentukan
- [ ] SUS score tercatat

### Fase 7 ✅

- [ ] Semua docstring lengkap
- [ ] README up-to-date
- [ ] Artikel ilmiah selesai dengan data
- [ ] `requirements.txt` final

---

_Rencana ini mengacu pada PRD v1.0 (11 Mei 2026) dan akan di-update jika ada perubahan requirement._
