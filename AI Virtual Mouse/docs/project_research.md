# Riset Proyek: AI Virtual Mouse

Berdasarkan video tutorial Murtaza's Workshop: [youtu.be/8gPONnGIPgw](https://youtu.be/8gPONnGIPgw)

---

## Ringkasan Proyek

Membuat **mouse virtual berbasis AI** yang bisa menggerakkan kursor dan melakukan klik menggunakan gerakan tangan di depan kamera.

Video: **39 menit 38 detik**, diunggah 3 Mei 2021, 843K+ views.
Channel: **Murtaza's Workshop - Robotics and AI** (449K subscribers).

---

## Teknologi

| Library | Fungsi |
|---------|--------|
| OpenCV (cv2) | Capture webcam, tampilkan hasil |
| MediaPipe | Deteksi 21 landmark tangan real-time |
| HandTrackingModule (custom) | Modul custom Murtaza, method: fingersUp(), findDistance(), dll |
| Autopy | Menggerakkan dan klik mouse via script |
| NumPy | Interpolasi koordinat kamera → layar |

---

## Workflow Sistem

1. **Webcam Capture** — `cv2.VideoCapture(0)`, resolusi tetap 640×480.
2. **Hand Detection** — `HandDetector` dari `HandTrackingModule`.
3. **Finger Identification** — `fingersUp()` tentukan jari mana yang terangkat.
4. **Gesture Mode**:
   - Telunjuk + tengah terangkat → **Mode Gerak**.
   - Hanya telunjuk terangkat → **Mode Klik**.
5. **Coordinate Mapping** — `numpy.interp()` dari 640×480 ke resolusi layar.
6. **Smoothing** — *Weighted moving average* untuk mengurangi getaran.
7. **Mouse Control** — `autopy.mouse.move()`, `autopy.mouse.click()`.

---

## Kode & Resource

- **Source Code**: [computervision.zone/courses/ai-virtual-mouse/](https://www.computervision.zone/courses/ai-virtual-mouse/) (gratis, perlu enroll).
- **File Utama**: `AIVirtualMouse.py` + `HandTrackingModule.py`.
- **Dependencies**: `opencv-python`, `mediapipe`, `numpy`, `autopy`.

---

## Catatan Penting

- Webcam ID: pastikan pakai 0 (default) atau 1 (jika multi kamera).
- Autopy vs PyAutoGUI: tutorial pakai Autopy, bisa diganti jika masalah kompatibilitas.
- Pencahayaan sangat memengaruhi akurasi deteksi.
- Video dibuat 2021 — versi library mungkin sudah berubah, sesuaikan saat instalasi.

---

*Last updated: 11 May 2026*
