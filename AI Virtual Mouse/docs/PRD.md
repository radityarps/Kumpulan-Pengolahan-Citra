# Product Requirements Document (PRD)
# AI Virtual Mouse — Kontrol Kursor Berbasis Gestur Tangan

**Versi:** 1.0  
**Tanggal:** 11 Mei 2026  
**Penulis:** Raditya  
**Proyek:** Tugas Pengolahan Citra — Semester 6

---

## Daftar Isi

1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Tujuan & Kriteria Sukses](#2-tujuan--kriteria-sukses)
3. [Target Pengguna & Persona](#3-target-pengguna--persona)
4. [Fungsionalitas (Functional Requirements)](#4-fungsionalitas-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Arsitektur Teknis](#6-arsitektur-teknis)
7. [Dependensi & Batasan](#7-dependensi--batasan)
8. [Milestone & Timeline](#8-milestone--timeline)
9. [Risiko & Mitigasi](#9-risiko--mitigasi)
10. [Kriteria Rilis](#10-kriteria-rilis)
11. [Lampiran](#11-lampiran)

---

## 1. Ringkasan Eksekutif

### 1.1 Latar Belakang

Mouse konvensional memiliki keterbatasan: memerlukan permukaan datar, kontak fisik, dan tidak ergonomis untuk presentasi jarak jauh atau lingkungan steril. Pandemi COVID-19 mempercepat kebutuhan antarmuka *touchless*. Kemajuan computer vision — khususnya MediaPipe Hands dari Google — kini memungkinkan deteksi tangan real-time hanya dengan webcam standar, membuka peluang membangun virtual mouse berbasis gestur.

### 1.2 Deskripsi Produk

**AI Virtual Mouse** adalah sistem berbasis Python yang memungkinkan pengguna mengontrol kursor komputer menggunakan gerakan tangan di depan webcam, tanpa menyentuh perangkat keras mouse. Sistem mendeteksi 21 *hand landmark* melalui MediaPipe, mengklasifikasikan gestur secara *rule-based* (jari terangkat / jarak antar-landmark), memetakan koordinat tangan ke layar, dan mengeksekusi aksi mouse via library Autopy.

### 1.3 Target Platform

- **OS**: Windows 10/11, Linux (via WSL atau native)
- **Hardware minimal**: Laptop/PC dengan webcam (640×480), CPU dual-core
- **Python**: 3.7+
- **Library inti**: OpenCV, MediaPipe, NumPy, Autopy

---

## 2. Tujuan & Kriteria Sukses

### 2.1 Tujuan

| ID | Tujuan | Prioritas |
|----|--------|-----------|
| O1 | Membangun pipeline lengkap: tangkap webcam → deteksi tangan → klasifikasi gestur → kontrol mouse | P0 (Wajib) |
| O2 | Mendukung minimal 4 gestur: gerak kursor, klik kiri, klik kanan, drag | P0 (Wajib) |
| O3 | Menerapkan *exponential smoothing* untuk mengurangi *jitter* kursor | P1 (Penting) |
| O4 | Mencapai frame rate ≥ 20 FPS pada hardware standar | P1 (Penting) |
| O5 | Menghasilkan artikel ilmiah dan dokumentasi lengkap | P0 (Wajib) |

### 2.2 Kriteria Sukses (Key Results)

| KR | Metrik | Target |
|----|--------|--------|
| KR1 | Akurasi klasifikasi gestur | ≥ 85% |
| KR2 | *End-to-end latency* (frame → aksi mouse) | ≤ 80 ms |
| KR3 | Frame rate pipeline | ≥ 20 FPS |
| KR4 | Skor System Usability Scale (SUS) | ≥ 70 |
| KR5 | Jarak deteksi efektif | 30–80 cm dari kamera |

---

## 3. Target Pengguna & Persona

| Persona | Kebutuhan | Skenario |
|---------|-----------|----------|
| **Presenter / Dosen** | Kontrol slide presentasi tanpa menyentuh laptop | Ruang presentasi, berdiri jauh dari meja |
| **Pengguna dengan keterbatasan motorik** | Alternatif mouse tanpa fine motor control | Rumah, tempat kerja |
| **Profesional di lingkungan steril** | Antarmuka touchless untuk lab bersih / ruang operasi | Laboratorium, rumah sakit |
| **Pengguna umum** | Eksplorasi interaksi HCI baru | Rumah, eksperimen |

---

## 4. Fungsionalitas (Functional Requirements)

### 4.1 Modul Webcam Capture

| ID | Requirement | Detail |
|----|-------------|--------|
| F1 | Inisialisasi webcam | `cv2.VideoCapture(0)`, resolusi 640×480 |
| F2 | Frame loop real-time | Loop utama membaca frame, menampilkan feed dengan overlay landmark |
| F3 | Keluar bersih | Tekan `q` untuk exit, `cv2.destroyAllWindows()` |

### 4.2 Modul Hand Detection & Landmark

| ID | Requirement | Detail |
|----|-------------|--------|
| F4 | Deteksi 21 hand landmark | Via MediaPipe Hands, `static_image_mode=False`, `max_num_hands=1` |
| F5 | Visualisasi landmark | Gambar titik dan koneksi pada frame (opsional toggle) |
| F6 | Threshold confidence | `min_detection_confidence=0.7`, `min_tracking_confidence=0.5` |

### 4.3 Modul Gesture Classification

| ID | Requirement | Gestur | Kondisi |
|----|-------------|--------|---------|
| F7 | Mode Gerak (*Move*) | Kursor mengikuti ujung telunjuk | Telunjuk DAN jari tengah terangkat |
| F8 | Mode Klik Kiri | Klik kiri mouse | Hanya telunjuk terangkat, lalu jarak telunjuk–tengah < *threshold* |
| F9 | Mode Klik Kanan | Klik kanan mouse | (opsional) Ibu jari + telunjuk terangkat |
| F10 | Mode Drag | Drag & drop | Tiga jari terangkat (opsional fase 2) |
| F11 | Mode Scroll | Scroll vertikal | Dua jari terangkat (telunjuk+tengah) + gerakan vertikal |

*Catatan:* Prioritas fase 1 adalah F7 dan F8 (gerak + klik kiri). F9–F11 opsional — dikembangkan jika waktu cukup.

### 4.4 Modul Coordinate Mapping & Smoothing

| ID | Requirement | Detail |
|----|-------------|--------|
| F12 | Interpolasi koordinat | `numpy.interp()` dari 640×480 ke resolusi layar aktual |
| F13 | Exponential smoothing | *Weighted moving average* dengan faktor `smoothening` 7–9, rumus: `curr_loc = prev_loc + (target - prev_loc) / smoothening` |

### 4.5 Modul Mouse Control

| ID | Requirement | Detail |
|----|-------------|--------|
| F14 | Gerak kursor | `autopy.mouse.move(x, y)` |
| F15 | Klik | `autopy.mouse.click()` (left/right berdasarkan mode) |
| F16 | Drag | `autopy.mouse.toggle(down=True)` → gerak → `toggle(down=False)` |

### 4.6 UI / Display Overlay

| ID | Requirement | Detail |
|----|-------------|--------|
| F17 | FPS counter | Tampilkan FPS real-time di pojok frame |
| F18 | Mode indicator | Teks overlay: "Move Mode", "Click Mode" |
| F19 | Landmark toggle | Tombol `l` untuk on/off visualisasi landmark |

---

## 5. Non-Functional Requirements

### 5.1 Performa

| ID | Requirement | Target |
|----|-------------|--------|
| N1 | Frame rate minimum | ≥ 15 FPS (ideal ≥ 20 FPS) |
| N2 | Latency end-to-end | ≤ 100 ms |
| N3 | CPU usage | ≤ 50% pada dual-core |

### 5.2 Usability

| ID | Requirement |
|----|-------------|
| N4 | Tidak perlu kalibrasi manual — *auto-detect* resolusi layar |
| N5 | Feedback visual jelas (mode teks, landmark) |
| N6 | Dokumentasi: README, komentar kode, docstring Python |

### 5.3 Reliability

| ID | Requirement |
|----|-------------|
| N7 | Tidak crash jika tangan hilang dari frame (graceful degradation) |
| N8 | Tidak crash jika kamera tidak tersedia (error message jelas) |
| N9 | Kursor tidak bergerak liar saat tangan tidak terdeteksi |

### 5.4 Maintainability

| ID | Requirement |
|----|-------------|
| N10 | Kode modular: setiap komponen di file terpisah |
| N11 | Modul `HandTrackingModule.py` reusable (bisa dipakai proyek lain) |

---

## 6. Arsitektur Teknis

### 6.1 Diagram Pipeline

```
[Webcam (OpenCV)]
       │
       ▼
[HandDetector.findHands()]  ← MediaPipe Hands
       │
       ▼
[lmList = findPosition()]    ← 21 landmark (x,y,z)
       │
       ▼
[fingers = fingersUp()]      ← Array 5 jari [0/1]
       │
       ▼
[Gesture Classification]     ← Rule-based: if-else
       │
       ├── Move Mode:  [1,1,0,0,0] → map index tip → screen coords
       ├── Click Mode: [0,1,0,0,0] + distance < threshold → click
       └── Drag Mode:  [0,1,1,1,0] → toggle down → move → toggle up
       │
       ▼
[Coordinate Mapping]         ← numpy.interp(640×480 → screen)
       │
       ▼
[Exponential Smoothing]      ← weighted moving average
       │
       ▼
[Mouse Control (Autopy)]     ← move(), click(), toggle()
```

### 6.2 Struktur File Source

```
src/
├── ai_virtual_mouse.py       # Main loop, integrasi semua modul
├── hand_tracking_module.py   # Class HandDetector (wrapper MediaPipe)
├── gesture_classifier.py     # Class GestureClassifier (fingersUp, findDistance, rule logic)
├── coordinate_mapper.py      # Class CoordinateMapper (interpolasi + smoothing)
├── mouse_controller.py       # Class MouseController (wrapper Autopy)
└── utils.py                  # FPS counter, overlay text, config loader
```

### 6.3 Dependensi Library

| Library | Versi Minimum | Fungsi |
|---------|---------------|--------|
| `opencv-python` | 4.5+ | Webcam capture, display, image processing |
| `mediapipe` | 0.8.10+ | Hand landmark detection (21 titik) |
| `numpy` | 1.19+ | Interpolasi koordinat |
| `autopy` | 4.0.0 | Kontrol mouse OS-level |

---

## 7. Dependensi & Batasan

### 7.1 Dependensi Eksternal

- **Kamera/webcam** — harus tersedia dan berfungsi (`/dev/video0` di Linux, default camera di Windows)
- **Pencahayaan** — ruangan cukup terang; deteksi menurun pada cahaya redup / backlight
- **Background** — sebaiknya polos/netral; background kompleks menurunkan akurasi deteksi

### 7.2 Batasan Sistem

| Batasan | Detail |
|---------|--------|
| Hanya 1 tangan | `max_num_hands=1` — multi-hand tidak didukung (fitur lanjutan) |
| Tidak ada dynamic gesture | Gestur bersifat statis per-frame; tidak ada gesture temporal (swipe, pinch-to-zoom) |
| Autopy kompatibilitas | Beberapa sistem mungkin butuh permission khusus (Wayland di Linux, accessibility permission di macOS) — target utama: Windows |
| Tidak ada GUI | Antarmuka hanya webcam feed + overlay OpenCV; tidak ada control panel GUI |

---

## 8. Milestone & Timeline

Estimasi total: **4–6 minggu** (paruh waktu, ~10–15 jam/minggu)

| Minggu | Fase | Deliverable |
|--------|------|-------------|
| 1 | **Setup & Research** | - Environment siap (Python, library terinstall)<br>- Video tutorial dipelajari<br>- Draft artikel: Bab 1–2 |
| 2 | **Core Pipeline** | - `HandTrackingModule.py` selesai<br>- Deteksi & visualisasi landmark berfungsi<br>- FingersUp & findDistance berfungsi |
| 3 | **Gesture + Mapping** | - 5 gestur (move, click, right-click, drag, scroll) selesai<br>- Coordinate mapping & smoothing terintegrasi |
| 4 | **Testing & Tuning** | - Uji akurasi gestur, latency, FPS<br>- Kuesioner SUS<br>- Tuning parameter smoothing |
| 5 | **Dokumentasi** | - Artikel ilmiah selesai (Bab 1–6)<br>- README, docstring, komentar kode |
| 6 | **Final polish** | - Revisi berdasarkan feedback<br>- Video demo (opsional)<br>- Submit |

### 8.1 Dependencies Antar Milestone

```
M1 (Setup) ──► M2 (Core) ──► M3 (Gesture) ──► M4 (Testing)
                                                    │
M1 (Setup) ──► M5 (Artikel) ◄───────────────────────┘
```

Artikel (M5) bisa dimulai paralel dengan M1, tapi hasil eksperimen (M4) baru bisa diisi setelah testing.

---

## 9. Risiko & Mitigasi

| Risiko | Prob. | Dampak | Mitigasi |
|--------|-------|--------|----------|
| Akurasi gestur rendah karena pencahayaan buruk | Sedang | Tinggi | Uji di beberapa kondisi pencahayaan; dokumentasikan batasan; tambah fallback color-based detection |
| Jitter kursor berlebihan | Sedang | Sedang | Tuning smoothing factor; uji beberapa nilai (5, 7, 9, 11); possible Kalman filter |
| Kompatibilitas Autopy di Windows/Linux | Rendah | Tinggi | Siapkan fallback ke PyAutoGUI; uji di kedua OS |
| Performa rendah (FPS < 15) | Rendah | Sedang | Turunkan resolusi kamera; batasi visualisasi; gunakan tracking mode MediaPipe |
| Library version conflict | Sedang | Sedang | Gunakan virtual environment (venv); pin versi di requirements.txt |
| Waktu tidak cukup untuk semua gestur | Sedang | Sedang | Prioritas: Move + Click wajib (P0); drag/scroll opsional (P2) |

---

## 10. Kriteria Rilis

### 10.1 Minimal Viable Product (MVP — Minimum untuk Submit)

- [x] Webcam capture + hand landmark detection berfungsi
- [x] Gestur Move (telunjuk+tengah) dan Click (telunjuk) berfungsi
- [x] Coordinate mapping + smoothing terintegrasi
- [x] Artikel ilmiah selesai dengan placeholder hasil eksperimen
- [x] Kode modular, terdokumentasi, dapat dijalankan dengan `python src/ai_virtual_mouse.py`

### 10.2 Stretch Goals (Jika Waktu Tersedia)

- [ ] Gestur Right-Click, Drag, Scroll
- [ ] Multi-hand support (2 tangan)
- [ ] Dynamic gesture (swipe, pinch)
- [ ] GUI control panel (ubah smoothing, sensitivity)
- [ ] Voice command integration
- [ ] Video demo

---

## 11. Lampiran

### 11.1 Referensi Utama

1. Zhang, F. et al. (2020). *MediaPipe Hands: On-device Real-time Hand Tracking*. arXiv:2006.10214.
2. Xu, P. (2017). *A Real-time Hand Gesture Recognition and Human-Computer Interaction System*. arXiv:1704.07296.
3. Köpüklü, O. et al. (2019). *Real-time Hand Gesture Detection and Classification Using CNNs*. arXiv:1901.10323.
4. Murtaza's Workshop (2021). *AI Virtual Mouse | OpenCV Python | Computer Vision*. YouTube: [youtu.be/8gPONnGIPgw](https://youtu.be/8gPONnGIPgw)
5. Amprimo, G. et al. (2023). *Hand tracking for clinical applications: validation of the Google MediaPipe Hand*. arXiv:2308.01088.

### 11.2 Glosarium

| Istilah | Definisi |
|---------|----------|
| Landmark | Titik kunci anatomi tangan (21 titik per tangan, 3D) |
| FingersUp | Metode deterministik: deteksi jari terangkat dengan membandingkan y-coordinate ujung vs pangkal jari |
| Exponential Smoothing | Weighted moving average untuk mengurangi jitter: `new = prev + (target - prev) / factor` |
| Rule-based Classification | Klasifikasi gestur berbasis aturan if-else (bukan machine learning) |
| SUS | System Usability Scale — kuesioner standar 10 pertanyaan untuk mengukur usability |

### 11.3 File Terkait

- **README.md**: `/mnt/d/Files/Documents/Kuliah/Semester 6/Pengolahan Citra/AI Virtual Mouse/README.md`
- **Artikel Ilmiah**: `/mnt/d/Files/Documents/Kuliah/Semester 6/Pengolahan Citra/AI Virtual Mouse/article/01_draft.md`
- **Literatur Review**: `/mnt/d/Files/Documents/Kuliah/Semester 6/Pengolahan Citra/AI Virtual Mouse/literature/00_literature_review.md`
- **Riset Proyek**: `/mnt/d/Files/Documents/Kuliah/Semester 6/Pengolahan Citra/AI Virtual Mouse/docs/project_research.md`
- **Source Code**: `/mnt/d/Files/Documents/Kuliah/Semester 6/Pengolahan Citra/AI Virtual Mouse/src/` (akan diisi)

---

*Dokumen ini disusun sebagai panduan pengembangan AI Virtual Mouse. Revisi dan pembaruan akan dilakukan seiring progres implementasi.*
