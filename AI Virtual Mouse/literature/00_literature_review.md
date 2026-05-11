# Literatur Review: AI Virtual Mouse

Dikumpulkan dari pencarian **arXiv API** (8 query, 37 paper) dan difilter manual.

---

## 1. Hand Tracking & Landmark Detection (WAJIB DIKUTIP)

### P1 — MediaPipe Hands: On-device Real-time Hand Tracking
- **Penulis**: Fan Zhang, Valentin Bazarevsky, Andrey Vakunov, et al. (Google Research)
- **Tahun**: 2020
- **arXiv**: [2006.10214](https://arxiv.org/abs/2006.10214)
- **Kategori**: cs.CV
- **Ringkasan**: Paper fundamental yang menjelaskan arsitektur *two-model pipeline* MediaPipe untuk hand tracking: (1) *palm detector* berbasis BlazePalm, (2) *hand landmark model* yang menghasilkan 21 koordinat 3D. Diimplementasikan via framework MediaPipe untuk mobile dan desktop.
- **Relevansi**: **Landmark paper** — sistem AI Virtual Mouse menggunakan MediaPipe Hands secara langsung. Wajib disitasi sebagai dasar metodologi.

### P2 — Hand tracking for clinical applications: validation of the Google MediaPipe Hand (GMH)
- **Penulis**: Gianluca Amprimo, Giulia Masi, et al.
- **Tahun**: 2023
- **arXiv**: [2308.01088](https://arxiv.org/abs/2308.01088)
- **Kategori**: cs.CV, cs.AI
- **Ringkasan**: Validasi kuantitatif akurasi pelacakan 3D tangan dan jari oleh Google MediaPipe Hands (GMH) dan versi *depth-enhanced* (GMH-D) untuk aplikasi klinis.
- **Relevansi**: Mendukung klaim bahwa MediaPipe memiliki akurasi yang memadai untuk kontrol presisi.

---

## 2. Hand Gesture Recognition (PENDUKUNG METHODOLOGY)

### P3 — Real-time Hand Gesture Detection and Classification Using CNNs
- **Penulis**: Okan Köpüklü, Ahmet Gunduz, Neslihan Kose, Gerhard Rigoll
- **Tahun**: 2019
- **arXiv**: [1901.10323](https://arxiv.org/abs/1901.10323)
- **Kategori**: cs.CV, cs.AI
- **Ringkasan**: Sistem deteksi dan klasifikasi *dynamic hand gesture* secara real-time menggunakan CNN ringan. Fokus pada *online detection* tanpa indikator mulai/berhenti eksplisit.
- **Relevansi**: Dapat dikutip sebagai *related work* dalam deteksi gesture real-time.

### P4 — HaGRIDv2: 1M Images for Static and Dynamic Hand Gesture Recognition
- **Penulis**: Anton Nuzhdin, Alexander Nagaev, et al.
- **Tahun**: 2024
- **arXiv**: [2412.01508](https://arxiv.org/abs/2412.01508)
- **Kategori**: cs.CV
- **Ringkasan**: Dataset besar berisi 1 juta gambar untuk 15 gesture statis dan dinamis, termasuk gesture kontrol dan percakapan.
- **Relevansi**: Dapat disebut sebagai contoh dataset gesture untuk training/evaluasi.

### P5 — Mediapipe and CNNs for Real-Time ASL Gesture Recognition
- **Penulis**: Rupesh Kumar, Ashutosh Bajpai, Ayush Sinha
- **Tahun**: 2023
- **arXiv**: [2305.05296](https://arxiv.org/abs/2305.05296)
- **Kategori**: cs.CV, cs.LG
- **Ringkasan**: Sistem *real-time* pengenalan American Sign Language menggunakan MediaPipe untuk ekstraksi fitur dan CNN untuk klasifikasi.
- **Relevansi**: Pipeline serupa — MediaPipe + klasifikasi. Bisa jadi referensi arsitektur.

### P6 — A Dynamic Modelling Framework for Human Hand Gesture Task Recognition
- **Penulis**: Sara Masoud, Bijoy Chowdhury, et al.
- **Tahun**: 2019
- **arXiv**: [1911.03923](https://arxiv.org/abs/1911.03923)
- **Kategori**: cs.LG, cs.CV, stat.ML
- **Ringkasan**: Framework pemodelan dinamis untuk pengenalan tugas berbasis gestur tangan menggunakan *data glove* dan *decision tree*.
- **Relevansi**: Pendekatan alternatif pengenalan gestur untuk perbandingan.

---

## 3. Virtual Mouse & HCI (PALING RELEVAN)

### P7 — A Real-time Hand Gesture Recognition and Human-Computer Interaction System
- **Penulis**: Pei Xu
- **Tahun**: 2017
- **arXiv**: [1704.07296](https://arxiv.org/abs/1704.07296)
- **Kategori**: cs.CV (deduced)
- **Ringkasan**: **SANGAT RELEVAN!** Paper ini menjelaskan sistem HCI berbasis gestur tangan yang dapat mengontrol *mouse* dan *keyboard* secara real-time. Sistem terdiri dari tiga komponen: deteksi tangan, pengenalan gesture, dan interaksi HCI.
- **Relevansi**: **Paper paling mirip dengan proyek AI Virtual Mouse.** Wajib dijadikan *primary reference* untuk *related work*. Bandingkan metodologi dan hasil.

### P8 — Vision Based Game Development Using Human Computer Interaction
- **Penulis**: S. Sumathi, S. K. Srivatsa, M. Uma Maheswari
- **Tahun**: 2010
- **arXiv**: [1002.2191](https://arxiv.org/abs/1002.2191)
- **Kategori**: cs.HC, cs.CV, cs.MM
- **Ringkasan**: Sistem HCI berbasis visi untuk bermain game menggunakan deteksi *eye blink* dan gestur. Contoh awal aplikasi HCI vision-based.
- **Relevansi**: Sebagai referensi historis evolusi HCI vision-based.

### P9 — Pen Spinning Hand Movement Analysis Using MediaPipe Hands
- **Penulis**: Tung-Lin Wu, Taishi Senda
- **Tahun**: 2021
- **arXiv**: [2108.10716](https://arxiv.org/abs/2108.10716)
- **Kategori**: cs.CV
- **Ringkasan**: Analisis gerakan tangan *pen spinning* menggunakan MediaPipe Hands dan OpenCV. Mendemostrasikan kemampuan tracking gerakan kompleks.
- **Relevansi**: Menunjukkan aplikasi tracking tangan dengan MediaPipe, mendukung metodologi.

---

## 4. Referensi Non-Paper

| No | Sumber | Deskripsi |
|----|--------|-----------|
| R1 | Bradski, G., & Kaehler, A. (2008). *Learning OpenCV*. O'Reilly Media. | Buku referensi OpenCV. |
| R2 | Lugaresi, C., et al. (2019). *MediaPipe: A Framework for Building Perception Pipelines*. Google AI. [arXiv:1906.08172](https://arxiv.org/abs/1906.08172) | Paper framework MediaPipe secara umum. |
| R3 | Murtaza's Workshop. *CVZone Library*. [computervision.zone](https://computervision.zone) | Library custom yang membungkus MediaPipe (HandTrackingModule). |
| R4 | Autopy Documentation. [pypi.org/project/autopy](https://pypi.org/project/autopy/) | Library kontrol mouse/keyboard via Python. |
| R5 | NumPy Documentation. [numpy.org](https://numpy.org) | Library komputasi numerik. |

---

## 5. Peta Konsep (Concept Map)

```
        AI Virtual Mouse
             |
   ┌─────────┼─────────┐
   |         |         |
Hand       Gesture    Mouse
Tracking   Recogn.   Control
   |         |         |
MediaPipe  fingersUp  Autopy
(P1, P2)   findDist   (R4)
   |       (P3-P6)    |
   +---> Coordinate Mapping (NumPy)
          +---> Smoothing Filter
```

---

## 6. Saran Pencarian Lanjutan

- **Google Scholar**: `"virtual mouse" "hand gesture" mediapipe`
- **arXiv**: `cat:cs.HC AND hand gesture mouse`
- **IEEE Xplore / Scopus**: `hand gesture controlled mouse` (mungkin butuh akses institusi)

---

*Last updated: 11 May 2026*
