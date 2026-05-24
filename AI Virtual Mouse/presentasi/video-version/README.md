# Video Version — Gambaran Umum

## Apa ini?

Video version adalah replikasi tutorial Murtaza's Workshop "AI Virtual Mouse | OpenCV Python" — dengan perbaikan bug dan penyesuaian gesture. Ini adalah **versi awal** dari proyek, sebelum rewrite modular.

## Kenapa ada dua versi?

| | Video Version | Main Version |
|---|---|---|
| **Arsitektur** | Single-loop, 2 file | 8 modul terpisah |
| **Gesture** | 6 gesture (sama dengan main) | 6 gesture |
| **Debounce** | Tidak ada | 300ms |
| **Hysteresis** | Tidak ada | ON/OFF thresholds |
| **Testing** | 3 file test manual | 33 unit tests |
| **Cocok buat** | Belajar dasar, lihat perbedaan | Production, sidang |

## Files

| File | Isi |
|---|---|
| `AIVirtualMouse.py` | Main loop — semua logic gesture + kontrol mouse |
| `HandTrackingModule.py` | Deteksi tangan pakai MediaPipe Tasks API |
| `config.py` | Semua konstanta yang bisa di-tuning |
| `requirements.txt` | Dependencies Python |

## Cara jalanin

```bash
# Install dependencies
pip install -r requirements.txt

# Jalanin (dari folder project root)
python video-version/AIVirtualMouse.py
```

Model file `hand_landmarker.task` harus ada di `src/hand_landmarker.task`. Kalau belum ada, download dari [MediaPipe Hand Landmarker](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker).

## Gesture

| Gesture | Pola Jari | Aksi |
|---|---|---|
| Move | Telunjuk naik | Kursor ikut telunjuk |
| Left Click | Telunjuk + tengah naik, pinch < 28px | Klik kiri sekali |
| Right Click | Telunjuk + tengah + manis naik, pinch telunjuk-manis < 34px | Klik kanan sekali |
| Drag | Kepalan (semua turun) | Tahan klik kiri, gerak relatif |
| Scroll | Semua 4 jari naik | Scroll up/down berdasarkan posisi tangan |

Jempol diabaikan (`*` wildcard) di semua pola gesture.
