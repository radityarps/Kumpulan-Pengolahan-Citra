# config.py — Penjelasan Konstanta (Main Version)

## Tujuan

Sentralisasi semua parameter yang bisa di-tuning. Satu tempat untuk ganti threshold, smoothing, warna, dan behavior sistem.

## Kenapa Lebih Banyak dari Video Version?

Video version cuma punya 15 konstanta. Main version punya ~40+. Kenapa? Karena setiap fitur baru (hysteresis, debounce, hold-time, hand-lost grace, freeze, debug) butuh parameter sendiri.

## Kategori Konstanta

### Kamera
| Konstanta | Default | Efek kalau diubah |
|---|---|---|
| `FRAME_WIDTH` | 640 | Resolusi — lebih besar = lebih akurat tapi lebih berat |
| `FRAME_HEIGHT` | 480 | |
| `CAMERA_ID` | 0 | Ganti ke 1 kalau pakai external webcam |

### MediaPipe
| Konstanta | Default | Efek |
|---|---|---|
| `MIN_DETECTION_CONFIDENCE` | 0.5 | Lebih rendah = lebih mudah deteksi tapi lebih banyak false positive |
| `MIN_TRACKING_CONFIDENCE` | 0.5 | |
| `MAX_NUM_HANDS` | 1 | Jangan ganti kecuali butuh dua tangan |
| `HAND_LOST_GRACE_FRAMES` | 4 | Lebih besar = lebih tahan tapi lebih lama stuck kalau tangan beneran hilang |

### Klasifikasi Gesture
| Konstanta | Default | Efek |
|---|---|---|
| `GESTURE_STYLE` | `"practical_no_thumb"` | Ganti profile gesture |
| `DEBOUNCE_TIME_MS` | 300 | Lebih kecil = lebih responsif tapi lebih banyak flicker |
| `LEFT_CLICK_PINCH_ON_PX` | 28 | Threshold ON — lebih besar = lebih mudah klik |
| `LEFT_CLICK_PINCH_OFF_PX` | 38 | Threshold OFF — harus lebih besar dari ON |
| `RIGHT_CLICK_PINCH_ON_PX` | 34 | |
| `RIGHT_CLICK_PINCH_OFF_PX` | 44 | |
| `CLICK_HOLD_TIME_MS` | 100 | Lebih besar = harus tahan pinch lebih lama |
| `MOVE_FREEZE_AFTER_CLICK_MS` | 200 | Lebih besar = freeze lebih lama setelah klik |
| `THUMB_SENSITIVITY` | 1.5 | >1.0 = lebih strict, <1.0 = lebih mudah |

### Koordinat & Smoothing
| Konstanta | Default | Efek |
|---|---|---|
| `FRAME_REDUCTION` | 100 | Dead zone pinggir frame |
| `SMOOTHING_FACTOR` | 5.0 | Lebih besar = lebih smooth tapi lebih lag |
| `DRAG_SENSITIVITY` | 1.0 | <1.0 = drag lebih lambat dari move |
| `CLICK_DELAY` | 0.1 | Jeda setelah klik (detik) |

### Scroll
| Konstanta | Default | Efek |
|---|---|---|
| `SCROLL_CENTER_DEAD_ZONE_PX` | 35 | Lebih besar = area no-scroll lebih lebar |
| `SCROLL_STEP_AMOUNT` | 2 | Lebih besar = scroll lebih cepat |
| `SCROLL_REPEAT_MS` | 120 | Lebih besar = scroll lebih lambat |

### Warna (BGR)
| Konstanta | Nilai | Warna |
|---|---|---|
| `COLOR_GREEN` | (0, 255, 0) | Hijau |
| `COLOR_BLUE` | (255, 0, 0) | Biru |
| `COLOR_RED` | (0, 0, 255) | Merah |
| `COLOR_YELLOW` | (0, 255, 255) | Kuning |
| `COLOR_PURPLE` | (255, 0, 255) | Ungu |
| `COLOR_CYAN` | (255, 255, 0) | Cyan |

## Tips Tuning

**Kursor goyang-goyang (jitter)?**
→ Naikkan `SMOOTHING_FACTOR` (5 → 7).

**Kursor terlalu lambat?**
→ Turunkan `SMOOTHING_FACTOR` (5 → 3) atau `FRAME_REDUCTION` (100 → 70).

**Klik susah (harus pinch rapet banget)?**
→ Naikkan `LEFT_CLICK_PINCH_ON_PX` (28 → 35).

**Spam klik (klik dua kali tanpa sengaja)?**
→ Naikkan `LEFT_CLICK_PINCH_OFF_PX` (38 → 48) — beda ON-OFF lebih besar.

**Gesture sering ganti-ganti sendiri?**
→ Naikkan `DEBOUNCE_TIME_MS` (300 → 500).

**Drag sering putus?**
→ Naikkan `HAND_LOST_GRACE_FRAMES` (4 → 8).

**Jempol susah kebaca naik?**
→ Turunkan `THUMB_SENSITIVITY` (1.5 → 1.0).
