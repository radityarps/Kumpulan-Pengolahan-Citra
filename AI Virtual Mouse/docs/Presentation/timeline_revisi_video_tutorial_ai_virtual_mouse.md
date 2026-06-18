---
title: "Timeline Video Tutorial AI Virtual Mouse"
author: "Raditya"
lang: id-ID
---

# Revisi Struktur — Timeline Video Fleksibel Lebih dari 10 Menit

Catatan produksi:

- Video tidak wajib 10 menit.
- Durasi boleh lebih panjang jika penjelasan kode dan benchmark membutuhkan waktu.
- Fokus utama: penonton paham demo, alur sistem, fungsi kode, benchmark, dan bukti improved lebih baik dari baseline.
- Timeline di bawah bisa dipakai sebagai struktur utama saat rekaman.

## Timeline Utama Video Tutorial

### 00:00–00:30 — Opening dan Tujuan Video

Visual:

- Presenter kecil di pojok.
- Tampilkan judul project: AI Virtual Mouse.
- Tampilkan layar desktop sebelum demo.

Narasi:

> Halo, saya Raditya. Di video ini saya akan mendemokan dan menjelaskan project AI Virtual Mouse. Fokus video ini bukan instalasi dari awal, tetapi bagaimana program dijalankan, bagaimana sistem bekerja dari kode, bagaimana baseline dibandingkan dengan versi improved, dan bagaimana benchmark digunakan untuk membuktikan hasil perbaikannya.

Cue editing:

- Tambahkan title overlay: `AI Virtual Mouse — Demo, Code Flow, Benchmark`.
- Jangan terlalu lama di opening. Langsung masuk demo.

---

### 00:30–02:30 — Demo Awal Versi Improved

Visual:

- Jalankan program improved.
- Tampilkan webcam preview.
- Tampilkan cursor bergerak dengan gesture index finger.
- Tampilkan click dengan gesture index-middle pinch.
- Tampilkan pause dengan open palm.

Command Bash:


| Kode / Command / File path |
|---|
| `source .venv-improved/Scripts/activate` |
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse` |


Command PowerShell:


| Kode / Command / File path |
|---|
| `$env:PYTHONPATH='src'; .venv-improved\Scripts\python.exe -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse` |


Narasi:

> Pertama saya tunjukkan dulu hasil akhirnya. Program ini membaca gerakan tangan dari webcam, lalu mengubahnya menjadi kontrol mouse. Untuk versi improved, gesture utamanya dibuat lebih sederhana: telunjuk saja untuk menggerakkan cursor, pinch telunjuk dan jari tengah untuk click, dan telapak terbuka untuk pause.
>
> Perhatikan bahwa cursor tidak bergerak langsung dari gambar webcam begitu saja. Di belakangnya ada pipeline: webcam membaca frame, hand tracker mendeteksi landmark tangan, gesture engine menentukan gesture, pipeline menghitung target cursor dan click, lalu runtime menjalankan mouse action.

Safety cue:

- Sebutkan tombol `q` untuk keluar.
- Sebutkan open palm untuk pause.
- Jangan arahkan cursor ke tombol berbahaya seperti delete, close, atau submit.

---

### 02:30–03:30 — Requirement dan Cara Menjalankan

Visual:

- Tampilkan terminal.
- Tampilkan struktur folder project.
- Tampilkan command run.

Narasi:

> Requirement utama program ini adalah Python environment yang sudah berisi OpenCV, MediaPipe, NumPy, dan backend mouse seperti AutoPy atau PyAutoGUI. OpenCV digunakan untuk membuka webcam dan membaca frame. MediaPipe digunakan untuk mendeteksi tangan. NumPy digunakan untuk perhitungan koordinat. AutoPy atau PyAutoGUI digunakan untuk menggerakkan mouse sistem operasi.
>
> Karena video ini adalah tutorial program, bukan tutorial instalasi, environment diasumsikan sudah siap. Untuk menjalankan versi improved, saya memakai module `ai_virtual_mouse_experimental` dengan mode demo, condition improved, dan flag `--allow-real-mouse` agar program boleh menggerakkan mouse asli.

Command model:


| Kode / Command / File path |
|---|
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --download-model` |


Command smoke test:


| Kode / Command / File path |
|---|
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --smoke-backend` |


Command demo:


| Kode / Command / File path |
|---|
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse` |


---

### 03:30–05:30 — Baseline Asli dan Masalah Kodenya

Visual:

- Buka file:


| Kode / Command / File path |
|---|
| `src/video version/AiVirtualMouseProject.py` |


Tampilkan import:


| Kode / Command / File path |
|---|
| `import time` |
| `import autopy` |
| `import cv2` |
| `import HandTrackingModule as htm` |
| `import numpy as np` |


Narasi:

> Sebelum menjelaskan versi improved, saya jelaskan dulu baseline asli. Baseline asli ada di file `src/video version/AiVirtualMouseProject.py`. Ini adalah versi awal AI Virtual Mouse. Di sini import yang digunakan cukup langsung: `cv2` untuk webcam, `HandTrackingModule` untuk deteksi tangan, `numpy` untuk mapping koordinat, `autopy` untuk mouse, dan `time` untuk menghitung FPS.

Tampilkan kode webcam:


| Kode / Command / File path |
|---|
| `cap = cv2.VideoCapture(0)` |
| `cap.set(3, wCam)` |
| `cap.set(4, hCam)` |
| `detector = htm.handDetector(maxHands=1)` |
| `wScr, hScr = autopy.screen.size()` |


Narasi:

> Bagian ini membuka webcam, mengatur ukuran kamera, membuat detector tangan, dan mengambil ukuran layar. Jadi dari awal baseline sudah langsung menghubungkan webcam, detector, dan mouse screen.

Tampilkan loop:


| Kode / Command / File path |
|---|
| `while True:` |
| `    success, img = cap.read()` |


Narasi:

> Setelah itu program masuk loop tanpa henti. Setiap iterasi membaca satu frame dari webcam. Frame ini kemudian diproses untuk mencari posisi tangan dan gesture.

Tampilkan click baseline:


| Kode / Command / File path |
|---|
| `if fingers[1] == 1 and fingers[2] == 1:` |
| `    length, img, lineInfo = detector.findDistance(8, 12, img)` |
| `    if length < 40:` |
| `        autopy.mouse.click()` |


Narasi:

> Masalah utama baseline ada di bagian click. Jika telunjuk dan jari tengah terdeteksi naik, program menghitung jarak landmark 8 dan 12. Jika jaraknya kurang dari 40 pixel, program langsung memanggil `autopy.mouse.click()`. Tidak ada debounce, tidak ada cooldown, tidak ada stable frame, dan tidak ada armed state. Akibatnya satu gerakan yang sedikit tidak stabil bisa menghasilkan banyak click.

---

### 05:30–06:30 — Baseline Runtime untuk Perbandingan

Visual:

- Tampilkan command baseline runtime.

Command:


| Kode / Command / File path |
|---|
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition baseline --allow-real-mouse` |


Narasi:

> Selain baseline asli, project ini juga punya baseline runtime melalui `--condition baseline`. Ini bukan file baseline asli, tetapi mode runtime pembanding di sistem experimental. Mode ini digunakan agar baseline dan improved bisa dijalankan dalam kerangka yang sama. Dengan begitu perbandingan lebih adil, karena benchmark dan runtime memakai struktur yang sama, hanya condition yang berbeda.

---

### 06:30–08:30 — Alur Besar Sistem Improved

Visual:

- Tampilkan diagram teks.


| Kode / Command / File path |
|---|
| `run_real_mouse_runtime()` |
| `    -> cv2.VideoCapture(...)` |
| `    -> cap.read()` |
| `    -> pipeline.process_frame(image)` |
| `        -> HandTracker.track(image)` |
| `        -> hand_input_from_tracking(...)` |
| `        -> classify_simple_real_mouse_gesture(...)` |
| `        -> map_point_to_output(...)` |
| `        -> apply_smoothing(...)` |
| `        -> update_click_debounce(...)` |
| `        -> HandControlFrame(...)` |
| `    -> mouse.move(...)` |
| `    -> mouse.click()` |


Narasi:

> Sekarang masuk ke versi improved. Alur besarnya seperti ini. Program dimulai dari `run_real_mouse_runtime`. Di sana webcam dibuka, frame dibaca, lalu frame dikirim ke pipeline. Pipeline memanggil hand tracker, mengubah tracking result menjadi gesture input, menjalankan gesture engine, mapping koordinat, smoothing, dan debounce. Hasil akhirnya adalah `HandControlFrame`. Setelah itu runtime baru memanggil `mouse.move` atau `mouse.click`.
>
> Jadi versi improved memisahkan tanggung jawab kode. Runtime mengurus kamera dan mouse. Hand tracker mengurus deteksi tangan. Gesture engine mengurus aturan gesture. Pipeline menggabungkan semuanya.

---

### 08:30–10:00 — Webcam dan Runtime Loop

Visual:

- Buka file:


| Kode / Command / File path |
|---|
| `src/ai_virtual_mouse_experimental/real_mouse_runtime.py` |


Tampilkan kode:


| Kode / Command / File path |
|---|
| `def run_real_mouse_runtime(config: ExperimentalConfig, plan: RuntimePlan) -> int:` |
| `    cv2 = import_module("cv2")` |
| `    mouse = _create_mouse_controller()` |
| `    cap = cv2.VideoCapture(config.backend.camera_index)` |
| `    cap.set(3, config.backend.camera_width)` |
| `    cap.set(4, config.backend.camera_height)` |


Narasi:

> Kode ini membuka runtime utama. `import_module("cv2")` memuat OpenCV. `_create_mouse_controller()` menyiapkan backend mouse. `cv2.VideoCapture` membuka webcam berdasarkan camera index. Lalu `cap.set` mengatur lebar dan tinggi kamera.

Ta
mpilkan kode:


| Kode / Command / File path |
|---|
| `while True:` |
| `    success, image = cap.read()` |
| `    if not success:` |
| `        print("Camera frame could not be read.")` |
| `        break` |
| &nbsp; |
| `    frame_result: HandControlFrame = pipeline.process_frame(image)` |


Narasi:

> Setelah kamera dibuka, program masuk loop. `cap.read()` membaca satu frame. Jika gagal, loop berhenti. Jika berhasil, frame dikirim ke `pipeline.process_frame(image)`. Di titik ini frame kamera mulai diproses menjadi gesture dan mouse command.

---

### 10:00–12:00 — Hand Tracker

Visual:

- Buka file:


| Kode / Command / File path |
|---|
| `src/ai_virtual_mouse_experimental/hand_tracker.py` |


Tampilkan kode:


| Kode / Command / File path |
|---|
| `@dataclass(frozen=True)` |
| `class HandTrackingResult:` |
| `    landmarks: list[Point] | None = None` |
| `    fingers_up: list[int] | None = None` |
| `    pinch_distance_px: float | None = None` |
| `    index_middle_vertical_delta_px: float | None = None` |
| `    success: bool = False` |
| `    backend_used: str = "unknown"` |
| `    fallback_reason: str | None = None` |


Narasi:

> Hand tracker menghasilkan `HandTrackingResult`. Data ini berisi landmark tangan, status jari, jarak pinch, status sukses, dan backend yang dipakai. Jadi output hand tracker belum berupa mouse action. Outputnya masih data tangan.

Tampilkan backend:


| Kode / Command / File path |
|---|
| `class HandTracker:` |
| `    """Unified hand tracker: Tasks primary, Solutions fallback."""` |


Narasi:

> Hand tracker memakai MediaPipe. Sistem mencoba backend MediaPipe Tasks lebih dulu. Jika gagal, sistem fallback ke MediaPipe Solutions. Ini membuat runtime lebih tahan terhadap perbedaan environment.

---

### 12:00–13:30 — Hand Tracking Result ke Gesture Input

Visual:

- Buka file:


| Kode / Command / File path |
|---|
| `src/ai_virtual_mouse_experimental/hand_control_pipeline.py` |


Tampilkan kode:


| Kode / Command / File path |
|---|
| `def hand_input_from_tracking(` |
| `    result: HandTrackingResult, config: GestureEngineConfig` |
| `) -> GestureInput:` |
| `    fingers = result.fingers_up or []` |
| `    if len(fingers) < 5:` |
| `        return GestureInput()` |
| `    return GestureInput(` |
| `        thumb=bool(fingers[0]),` |
| `        index=bool(fingers[1]),` |
| `        middle=bool(fingers[2]),` |
| `        ring=bool(fingers[3]),` |
| `        pinky=bool(fingers[4]),` |
| `        pinch_distance_px=result.pinch_distance_px,` |
| `        pinch_duration_s=0.0,` |
| `        index_middle_vertical_delta_px=result.index_middle_vertical_delta_px or 0.0,` |
| `    )` |


Narasi:

> Setelah hand tracker selesai, pipeline mengubah `HandTrackingResult` menjadi `GestureInput`. List `fingers_up` diubah menjadi boolean seperti thumb, index, middle, ring, dan pinky. Jarak pinch juga diteruskan. Format ini lebih mudah dipakai gesture engine.

---

### 13:30–16:00 — Gesture Engine: Move, Click, Pause

Visual:

- Buka file:


| Kode / Command / File path |
|---|
| `src/ai_virtual_mouse_experimental/gesture_engine.py` |


Tampilkan kode:


| Kode / Command / File path |
|---|
| `def classify_simple_real_mouse_gesture(` |
| `    hand: GestureInput,` |
| `    config: GestureEngineConfig | None = None,` |
| `) -> GestureResult:` |
| `    cfg = config or GestureEngineConfig()` |
| &nbsp; |
| `    if is_open_palm(hand):` |
| `        return _pause_result()` |
| &nbsp; |
| `    if hand.index and hand.middle and not hand.ring and not hand.pinky:` |
| `        if is_pinching(hand, cfg):` |
| `            return _click_result("index_middle_stable_pinch")` |
| `        return GestureResult(name="idle", reason="index_middle_without_pinch")` |
| &nbsp; |
| `    if hand.index and not hand.middle and not hand.ring and not hand.pinky:` |
| `        return _move_result()` |
| &nbsp; |
| `    return GestureResult(name="idle", reason="no_supported_real_mouse_gesture")` |


Narasi:

> Gesture engine adalah bagian yang menentukan arti gerakan tangan. Jika telapak terbuka, hasilnya pause. Jika telunjuk dan jari tengah aktif lalu pinch valid, hasilnya click. Jika hanya telunjuk aktif, hasilnya move. Selain itu, gesture dianggap idle.

Tampilkan kode:


| Kode / Command / File path |
|---|
| `def is_pinching(hand: GestureInput, config: GestureEngineConfig) -> bool:` |
| `    return (` |
| `        hand.pinch_distance_px is not None` |
| `        and hand.pinch_distance_px < config.click_threshold_px` |
| `    )` |


Narasi:

> Fungsi `is_pinching` mengecek apakah jarak pinch ada dan nilainya lebih kecil dari threshold. Ini yang membedakan gesture dua jari biasa dengan gesture click.

---

### 16:00–18:00 — Debounce Click

Visual:

- Tetap di `gesture_engine.py`.

Tampilkan kode:


| Kode / Command / File path |
|---|
| `@dataclass(frozen=True)` |
| `class ClickDebounceConfig:` |
| `    stable_frames_required: int = 2` |
| `    release_frames_required: int = 2` |
| `    cooldown_seconds: float = 0.35` |


Tampilkan logic:


| Kode / Command / File path |
|---|
| `cooldown_elapsed = now_s - state.last_click_time_s >= cfg.cooldown_seconds` |
| `stable = next_state.pressed_frames >= cfg.stable_frames_required` |
| `if next_state.armed and stable and cooldown_elapsed:` |
| `    return ClickDebounceResult(..., emit_click=True, reason="stable_click_emitted")` |


Narasi:

> Perbaikan penting ada di debounce. Baseline langsung click ketika jarak dua jari kurang dari threshold. Versi improved tidak begitu. Pinch harus stabil selama beberapa frame, sistem harus dalam kondisi armed, dan cooldown dari click sebelumnya harus sudah lewat. Baru setelah itu `emit_click=True`.
>
> Inilah alasan false click bisa turun besar. Program tidak lagi menganggap setiap frame pinch sebagai click baru.

---

### 18:00–20:00 — Hand Control Pipeline dan Mapping Cursor

Visual:

- Buka:


| Kode / Command / File path |
|---|
| `src/ai_virtual_mouse_experimental/hand_control_pipeline.py` |


Tampilkan output:


| Kode / Command / File path |
|---|
| `@dataclass(frozen=True)` |
| `class HandControlFrame:` |
| `    cursor_target: Point | None = None` |
| `    click_fired: bool = False` |
| `    paused: bool = False` |
| `    gesture_name: str = "idle"` |
| `    feedback_label: str = "Idle"` |
| `    backend_used: str = "unknown"` |
| `    fps: float = 0.0` |
| `    safety_triggered: bool = False` |
| `    hand_detected: bool = False` |
| `    landmarks_image: np.ndarray | None = None` |


Narasi:

> Pipeline menggabungkan semuanya menjadi `HandControlFrame`. Field `cursor_target` adalah posisi cursor final. Field `click_fired` adalah hasil click setelah debounce. Field `paused` memberi tahu runtime apakah mouse action perlu ditahan. Field `landmarks_image` dipakai untuk tampilan overlay.

Tampilkan import:


| Kode / Command / File path |
|---|
| `from .cursor_mapping import apply_smoothing, map_point_to_output` |
| `from .gesture_engine import classify_simple_real_mouse_gesture, update_click_debounce` |
| `from .hand_tracker import HandTracker, HandTrackingResult` |


Narasi:

> Dari import ini terlihat pipeline memakai hand tracker, gesture engine, mapping, smoothing, dan debounce. Jadi pipeline adalah penghubung antar modul, bukan sekadar helper kecil.

---

### 20:00–21:30 — Mouse Action Nyata

Visual:

- Kembali ke:


| Kode / Command / File path |
|---|
| `src/ai_virtual_mouse_experimental/real_mouse_runtime.py` |


Tampilkan controller:


| Kode / Command / File path |
|---|
| `def _create_mouse_controller() -> MouseController:` |
| `    try:` |
| `        autopy = import_module("autopy")` |
| `        width, height = autopy.screen.size()` |
| `        return MouseController(` |
| `            width=int(width),` |
| `            height=int(height),` |
| `            backend="autopy",` |
| `            move=autopy.mouse.move,` |
| `            click=autopy.mouse.click,` |
| `        )` |


Tampilkan action:


| Kode / Command / File path |
|---|
| `if frame_result.cursor_target is not None and not frame_result.paused:` |
| `    mouse.move(frame_result.cursor_target.x, frame_result.cursor_target.y)` |
| &nbsp; |
| `if frame_result.click_fired:` |
| `    mouse.click()` |


Narasi:

> Mouse action benar-benar terjadi di runtime. Jika ada cursor target dan tidak pause, `mouse.move` dipanggil. Jika `click_fired=True`, `mouse.click` dipanggil. Jadi gesture tidak langsung mengklik mouse. Gesture harus melewati tracker, gesture engine, pipeline, dan debounce dulu.

---

### 21:30–24:00 — Benchmark: Cara Kerja dan Fungsi

Visual:

- Buka file:


| Kode / Command / File path |
|---|
| `src/ai_virtual_mouse_experimental/benchmark_shell.py` |
| `src/ai_virtual_mouse_experimental/benchmark_grid.py` |
| `src/ai_virtual_mouse_experimental/benchmark_report.py` |


Command:


| Kode / Command / File path |
|---|
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline` |
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition improved` |


Narasi:

> Benchmark digunakan untuk membandingkan baseline dan improved secara lebih objektif. Benchmark tidak menggerakkan mouse sistem operasi. Benchmark memakai simulated cursor dan tar
get grid. Artinya sistem membuat target di layar benchmark, lalu menghitung apakah click mengenai target atau tidak. Jika click terjadi di dalam radius target, dihitung hit. Jika di luar radius, dihitung false click.

Detail konsep:

- `generate_grid_targets(settings)`: membuat target benchmark.
- `random_seed`: membuat urutan target konsisten.
- `register_click`: mencatat click.
- Hit: jarak click ke pusat target <= radius target.
- False click: click di luar target.
- `completion_time_s`: waktu menyelesaikan target.
- `false_clicks_before_hit`: jumlah false click sebelum hit.
- `compute_metrics`: menghitung ringkasan hasil.

Narasi lanjutan:

> Dengan cara ini baseline dan improved dibandingkan memakai kondisi yang sama. Perbedaannya bukan target, tetapi logic condition yang dipakai. Baseline cenderung menghasilkan click berlebih, sedangkan improved memakai debounce sehingga click lebih terkendali.

---

### 24:00–25:30 — Compare Sessions dan Hasil

Visual:

- Tampilkan command compare.


| Kode / Command / File path |
|---|
| `PYTHONPATH=src python -m ai_virtual_mouse_experimental --compare-sessions outputs/sessions/session-a outputs/sessions/session-b` |


Narasi:

> Setelah benchmark baseline dan improved dijalankan, hasil session dibandingkan. Dari perbandingan ini kita melihat metrik utama: hit rate, false click, dan total click.

Tampilkan evidence:


| Kode / Command / File path |
|---|
| `Hit rate baseline : 100%` |
| `Hit rate improved : 100%` |
| `False clicks      : 192,8 -> 4,2` |
| `Total clicks      : 212,8 -> 24,2` |


Narasi:

> Hasilnya menunjukkan hit rate sama-sama 100 persen. Artinya kedua versi bisa menyelesaikan target. Perbedaan besar ada pada false click dan total click. False click turun dari 192,8 menjadi 4,2. Total click turun dari 212,8 menjadi 24,2. Jadi improved bukan hanya berhasil menjalankan fungsi yang sama, tetapi juga jauh lebih stabil dan lebih sedikit salah click.

---

### 25:30–27:00 — Kesimpulan Evidence-Based

Visual:


| Kode / Command / File path |
|---|
| `1. Baseline bisa bekerja, tetapi click terlalu agresif.` |
| `2. Improved memisahkan tracker, gesture engine, pipeline, dan runtime.` |
| `3. Benchmark membuktikan false click dan total click turun besar.` |


Narasi:

> Kesimpulannya, baseline asli sudah bisa mengubah gesture tangan menjadi mouse virtual, tetapi logic click-nya terlalu langsung. Ketika jarak dua jari kurang dari threshold, mouse langsung click. Tanpa debounce dan cooldown, ini menyebabkan banyak false click.
>
> Versi improved memperbaiki masalah itu dengan struktur yang lebih jelas. Webcam dan mouse action ada di runtime. Deteksi tangan ada di hand tracker. Aturan gesture ada di gesture engine. Mapping, smoothing, dan debounce digabung di pipeline. Hasil akhirnya baru dikirim ke mouse action.
>
> Dari benchmark, improved terbukti lebih baik. Hit rate tetap 100 persen, false click turun dari 192,8 menjadi 4,2, dan total click turun dari 212,8 menjadi 24,2. Jadi improved lebih stabil, lebih terkendali, dan lebih layak digunakan sebagai AI Virtual Mouse.

---

### 27:00–Selesai — Closing

Visual:

- Tampilkan demo singkat lagi atau layar hasil benchmark.
- Presenter kecil muncul lagi.

Narasi:

> Itu penjelasan project AI Virtual Mouse dari demo, cara menjalankan, baseline, alur kode improved, sampai benchmark. Dengan struktur ini kita bisa melihat bukan hanya programnya berjalan, tetapi juga bagian kode mana yang bertanggung jawab untuk webcam, hand tracker, gesture engine, pipeline, mouse action, dan evaluasi benchmark.

Editing cue:

- Akhiri dengan freeze frame hasil benchmark atau cursor demo.
- Tambahkan teks: `Improved: same hit rate, far fewer false clicks`.
