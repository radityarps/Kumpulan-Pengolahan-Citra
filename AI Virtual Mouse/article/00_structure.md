# Struktur Artikel Ilmiah AI Virtual Mouse

Diadaptasi dari format jurnal *Smart Agricultural Technology* (Elsevier) pada contoh PDF YOLO-ECN.

## Judul

**AI Virtual Mouse: Real-Time Hand Gesture-Based Cursor Control Menggunakan OpenCV dan MediaPipe**

*(Alternatif: AI Virtual Mouse for Touchless Human-Computer Interaction using Hand Landmark Detection)*

---

## Abstract

- **Latar belakang**: Kebutuhan antarmuka *touchless* dan *hands-free* untuk berbagai aplikasi (presentasi, gaming, aksesibilitas).
- **Tujuan**: Merancang sistem kontrol kursor berbasis gestur tangan secara *real-time*.
- **Metode**: Deteksi 21 *hand landmark* via MediaPipe → identifikasi jari (fingersUp) → pemetaan koordinat ke layar (NumPy interp) → kontrol mouse (Autopy) + *smoothing filter*.
- **Hasil utama**: Akurasi pengenalan gestur X%, *latency* Y ms, *usability score* Z.
- **Kesimpulan**: Sistem efektif sebagai alternatif *touchless mouse* dengan potensi pengembangan ke *multi-gesture*.

---

## Keywords

`virtual mouse`, `hand gesture recognition`, `MediaPipe`, `OpenCV`, `human-computer interaction`, `real-time hand tracking`

---

## 1. Introduction

### Latar Belakang
- Perkembangan *Human-Computer Interaction* (HCI) menuntut antarmuka yang lebih natural dan *intuitive*.
- Mouse/kibor konvensional memiliki keterbatasan: perlu permukaan datar, tidak ergonomis untuk penggunaan jangka panjang, tidak cocok untuk presentasi jarak jauh.
- *Hand gesture recognition* menawarkan alternatif *touchless* yang sudah banyak diteliti.

### State-of-the-Art
- Sebutkan paper terkait gesture recognition (P3, P4, P5) dan HCI (P7, P8).
- Referensi utama: *MediaPipe Hands* (Zhang et al., 2020) untuk deteksi *landmark* real-time.

### Gap Penelitian
- Kebanyakan sistem fokus pada pengenalan gestur saja, bukan integrasi langsung ke kontrol kursor.
- Belum banyak yang mengaplikasikan *smoothing filter* pada pemetaan koordinat.

### Kontribusi
1. Sistem *pipeline* lengkap: deteksi tangan → klasifikasi gestur → kontrol mouse.
2. Implementasi *smoothing* berbasis *weighted moving average* untuk mengurangi *jitter*.
3. Evaluasi kuantitatif dengan metrik akurasi, *latency*, dan *usability*.

---

## 2. Related Work

| Kategori | Paper | Ringkasan |
|----------|-------|-----------|
| **Hand Detection** | MediaPipe Hands (Zhang 2020) | Pipeline 2-model (palm detector + landmark) |
| | Hand Tracking Validation (Amprimo 2023) | Validasi akurasi MediaPipe |
| **Gesture Recognition** | Real-time Hand Gesture Detection (Köpüklü 2019) | CNN untuk deteksi gestur real-time |
| | HaGRIDv2 (Nuzhdin 2024) | Dataset 1M gambar gesture |
| | MediaPipe + CNN ASL (Kumar 2023) | Aplikasi MediaPipe untuk gesture |
| **Virtual Mouse & HCI** | **Hand Gesture HCI System (Xu 2017)** | Sistem kontrol mouse & keyboard via gesture — **paling mirip** |
| | Vision Based Game HCI (Sumathi 2010) | Contoh awal HCI vision-based |

---

## 3. Methodology

### 3.1 System Overview
```
[Webcam] → [Frame Capture] → [Hand Detection]
     → [Landmark Extraction] → [Finger State Analysis]
     → [Gesture Classification] → [Coordinate Mapping + Smoothing]
     → [Mouse Control (move, click, drag, scroll)]
```

### 3.2 Hand Landmark Detection
- **MediaPipe Hands**: 21 titik *landmark* per tangan.
- Class `HandDetector` dari modul `HandTrackingModule` menyediakan method:
  - `findHands()`: deteksi tangan pada frame.
  - `findPosition()`: koordinat (x, y, z) tiap *landmark*.
  - `fingersUp()`: menentukan jari mana yang terangkat berdasarkan posisi ujung vs punggung jari.
  - `findDistance()`: jarak Euclidean antar dua *landmark*.

### 3.3 Gesture Classification
- **Mode Gerak**: Telunjuk & jari tengah terangkat → kursor mengikuti ujung telunjuk.
- **Mode Klik**: Hanya telunjuk terangkat → siap klik. Klik terdeteksi saat jarak telunjuk–tengah < *threshold*.
- **Mode Drag/Scroll**: (opsional) jarak ibu jari–telunjuk, atau tiga jari.

### 3.4 Coordinate Mapping & Smoothing
- Interpolasi linear dari resolusi kamera (640×480) ke resolusi layar (1920×1080) menggunakan `numpy.interp()`.
- *Smoothing*: *weighted moving average* dengan faktor `smoothening` (biasanya 7–9) untuk mengurangi *jitter*.

### 3.5 Mouse Control
- Library **Autopy**: `mouse.move()`, `mouse.click()`, `mouse.toggle()`.
- Mapping: posisi ujung telunjuk yang sudah di-smooth → koordinat layar → `mouse.move()`.

---

## 4. Experiments & Results

### 4.1 Setup
- **Hardware**: Laptop (spesifikasi), webcam (resolusi).
- **Software**: Python 3.x, OpenCV, MediaPipe, Autopy.
- **Lingkungan**: Pencahayaan normal, jarak 30–80 cm dari kamera, background netral.

### 4.2 Metrics
- **Akurasi Gesture**: Rasio gesture yang dikenali benar.
- **Latency**: Waktu dari frame capture → mouse response.
- **FPS**: Frame per second pipeline.
- **User Experience**: Skor *System Usability Scale* (SUS) dari kuesioner.

### 4.3 Quantitative Results
- Tabel akurasi per gesture (klik, drag, dll).
- Confusion matrix gesture classification.
- Perbandingan FPS *dengan* vs *tanpa* smoothing.

### 4.4 Qualitative Analysis
- Screenshot visualisasi *landmark*.
- Testimoni pengguna.

---

## 5. Discussion
- Analisis kelebihan: *real-time performance* ringan, akurasi tinggi pada kondisi ideal.
- Keterbatasan: sensitif terhadap pencahayaan, okulasi jari, background kompleks.
- Perbandingan dengan existing work (Xu 2017, dll).

---

## 6. Conclusion & Future Work
- Ringkasan temuan.
- Future work: *multi-hand* support, *dynamic gesture*, integrasi *deep learning*, *mobile deployment*.

---

## Referensi (IEEE style — lihat `../literature/bibtex/references.bib`)
- [1] F. Zhang et al., "MediaPipe Hands: On-device Real-time Hand Tracking," 2020.
- [2] P. Xu, "A Real-time Hand Gesture Recognition and HCI System," 2017.
- [dst.]
