# AI Virtual Mouse - Gesture Guide

Panduan ini mengikuti konfigurasi gesture aktif saat ini (`GESTURE_STYLE = "practical_no_thumb"`) di `src/gesture_profiles.py`.

## Menjalankan Aplikasi

```bash
python src/ai_virtual_mouse.py
```

Overlay debug akan menampilkan:

- `Fingers`: vektor jari `[thumb,index,middle,ring,pinky]`
- `Mode`: mode gesture aktif
- `Action`: aksi terakhir
- `FPS`: frame rate

## Mapping Gesture Aktif

| Fungsi | Pattern Jari | Keterangan |
| --- | --- | --- |
| Move | `[*,1,0,0,0]` | Cursor mengikuti index finger (thumb diabaikan) |
| Left Click | `[*,1,1,0,0]` + pinch index-middle | Klik kiri dengan hysteresis + hold-time |
| Right Click | `[*,1,1,1,0]` + pinch index-ring | Klik kanan dengan hysteresis + hold-time |
| Drag | `[*,0,0,0,0]` | Menahan klik kiri dan tetap menggerakkan cursor |
| Scroll | `[*,1,1,1,1]` | Scroll berdasarkan posisi jari index terhadap garis tengah kamera |

## Cara Pakai Tiap Gesture

Keterangan: `*` berarti nilai thumb diabaikan (0 atau 1 sama-sama valid).

### 1. Move

- Bentuk pattern `[*,1,0,0,0]`.
- Gerakkan tangan untuk memindahkan cursor.
- Mode ini dibuat responsif (tanpa delay debounce mode lain).

### 2. Left Click

- Bentuk pattern `[*,1,1,0,0]`.
- Klik terjadi saat pinch index-middle cukup dekat dan stabil.
- Tahan gesture tidak akan klik berulang.

### 3. Right Click

- Bentuk pattern `[*,1,1,1,0]`.
- Sama seperti klik kiri: trigger saat pinch index-ring stabil.

### 4. Drag

- Bentuk pattern `[*,0,0,0,0]` untuk `drag_start`.
- Selama mode drag aktif, gerakan tangan tetap menggeser cursor.
- Lepaskan drag dengan berpindah ke gesture lain atau saat hand lost.

### 5. Scroll

- Bentuk pattern `[*,1,1,1,1]`.
- Jika jari index berada **di atas** batas tengah kamera → scroll up.
- Jika jari index berada **di bawah** batas tengah kamera → scroll down.
- Jika jari index berada di zona tengah (dead zone) → tidak scroll.
- Respons scroll dipengaruhi `SCROLL_CENTER_DEAD_ZONE_PX`, `SCROLL_STEP_AMOUNT`, dan `SCROLL_REPEAT_MS`.

## Parameter Konfigurasi Penting

Atur di `src/config.py`:

```python
DEBOUNCE_TIME_MS = 300
CLICK_HOLD_TIME_MS = 100
MOVE_FREEZE_AFTER_CLICK_MS = 200
LEFT_CLICK_PINCH_ON_PX = 28
LEFT_CLICK_PINCH_OFF_PX = 38
RIGHT_CLICK_PINCH_ON_PX = 34
RIGHT_CLICK_PINCH_OFF_PX = 44
SCROLL_CENTER_DEAD_ZONE_PX = 35
SCROLL_STEP_AMOUNT = 2
SCROLL_REPEAT_MS = 120
HAND_LOST_GRACE_FRAMES = 4
SMOOTHING_FACTOR = 5.0
```

## Catatan Runtime

- Jika `autopy.mouse.scroll` tidak tersedia pada environment tertentu, aplikasi akan menampilkan warning dan aksi scroll diabaikan.
- Gesture click/right-click menggunakan mekanisme anti-repeat (`click_ready`).
- Sistem default hanya memproses satu tangan (`MAX_NUM_HANDS = 1`).

## Quick Test Checklist

- [ ] Move: `[*,1,0,0,0]` menggerakkan cursor
- [ ] Left Click: `[*,1,1,0,0]` + pinch memicu klik kiri sekali
- [ ] Right Click: `[*,1,1,1,0]` + pinch memicu klik kanan sekali
- [ ] Drag: `[*,0,0,0,0]` menahan klik kiri dan bisa geser objek
- [ ] Scroll: `[*,1,1,1,1]` scroll naik/turun (jika backend mendukung)
