# config.py — Penjelasan Konstanta

## Tujuan

Semua "magic numbers" dikumpulkan di satu file. Mau ganti threshold? Ubah di sini. Nggak perlu cari-cari di dalam kode.

## Kenapa Dipisah?

Di tutorial asli, threshold dan parameter ditulis langsung di dalam kode (hardcoded). Ini bikin tuning susah — harus buka file utama, cari angka yang tersebar di berbagai baris.

Dengan config terpisah, semua parameter dalam satu tempat. Plus, kalau nanti butuh bikin versi dengan setting berbeda, tinggal ganti config.

## Daftar Konstanta

### Kamera
| Konstanta | Nilai | Artinya |
|---|---|---|
| `FRAME_WIDTH` | 640 | Lebar gambar kamera (pixel) |
| `FRAME_HEIGHT` | 480 | Tinggi gambar kamera (pixel) |
| `CAMERA_ID` | 0 | Webcam default (0 = built-in, 1 = external) |

### MediaPipe
| Konstanta | Nilai | Artinya |
|---|---|---|
| `MIN_DETECTION_CONFIDENCE` | 0.5 | Confidence minimal buat deteksi tangan (50%) |
| `MIN_TRACKING_CONFIDENCE` | 0.5 | Confidence minimal buat tracking |
| `MAX_NUM_HANDS` | 1 | Maksimal tangan yang dideteksi |

### Koordinat & Smoothing
| Konstanta | Nilai | Artinya |
|---|---|---|
| `FRAME_REDUCTION` | 100 | Margin dead zone di pinggir frame (pixel) |
| `SMOOTHING` | 7 | Faktor smoothing EMA — makin besar = makin smooth tapi makin lag |

### Threshold Gesture
| Konstanta | Nilai | Artinya |
|---|---|---|
| `LEFT_CLICK_PINCH_PX` | 28 | Jarak maksimal telunjuk-tengah buat trigger klik kiri |
| `RIGHT_CLICK_PINCH_PX` | 34 | Jarak maksimal telunjuk-manis buat trigger klik kanan |

### Scroll
| Konstanta | Nilai | Artinya |
|---|---|---|
| `SCROLL_CENTER_DEAD_ZONE_PX` | 35 | Area no-scroll (±35px dari garis tengah kamera) |
| `SCROLL_STEP_AMOUNT` | 2 | Seberapa jauh scroll per trigger |
| `SCROLL_REPEAT_MS` | 120 | Interval minimal antar scroll (milidetik) |

## Tips Tuning

- **Kursor terlalu sensitif?** Naikkan `SMOOTHING` (7 → 10) atau `FRAME_REDUCTION` (100 → 150).
- **Klik susah trigger?** Naikkan threshold pinch (`LEFT_CLICK_PINCH_PX` 28 → 35).
- **Klik terlalu mudah?** Turunkan threshold pinch (28 → 22).
- **Scroll terlalu cepat?** Naikkan `SCROLL_REPEAT_MS` (120 → 200) atau turunkan `SCROLL_STEP_AMOUNT` (2 → 1).
