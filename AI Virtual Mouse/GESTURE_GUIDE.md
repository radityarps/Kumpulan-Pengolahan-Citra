# AI Virtual Mouse - Gesture Guide

Panduan ini mengikuti konfigurasi gesture aktif saat ini (`GESTURE_STYLE = "legacy"`) di `src/gesture_profiles.py`.

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
| Move | `[0,1,1,0,0]` | Cursor mengikuti index finger |
| Stop Move | `[1,1,1,0,0]` | Menghentikan mode gerak seketika |
| Left Click | `[1,0,1,0,0]` | Satu kali klik kiri saat masuk gesture |
| Right Click | `[1,1,0,0,0]` | Satu kali klik kanan saat masuk gesture |
| Drag | `[0,0,0,0,0]` | Menahan klik kiri; gerakan tetap bisa mengikuti tangan |
| Scroll | `[1,1,1,1,1]` | Scroll berdasarkan perubahan vertikal jari index |

## Cara Pakai Tiap Gesture

### 1. Move

- Bentuk pattern `[0,1,1,0,0]`.
- Gerakkan tangan untuk memindahkan cursor.
- Mode ini dibuat responsif (tanpa delay debounce mode lain).

### 2. Stop Move

- Ubah ke pattern `[1,1,1,0,0]`.
- Sistem langsung mengembalikan mode ke `None`.
- Jika sedang drag, gesture ini juga akan mengakhiri drag.

### 3. Left Click

- Bentuk pattern `[1,0,1,0,0]`.
- Klik terjadi saat transisi masuk gesture (edge-triggered).
- Tahan gesture tidak akan klik berulang.

### 4. Right Click

- Bentuk pattern `[1,1,0,0,0]`.
- Sama seperti klik kiri: trigger saat entry gesture.

### 5. Drag

- Bentuk pattern `[0,0,0,0,0]` untuk `drag_start`.
- Selama mode drag aktif, gerakan tangan tetap menggeser cursor.
- Lepaskan drag dengan berpindah ke gesture lain atau saat hand lost.

### 6. Scroll

- Bentuk pattern `[1,1,1,1,1]`.
- Gerak tangan ke atas/bawah untuk menghasilkan scroll up/down.
- Nilai scroll dipengaruhi `SCROLL_SENSITIVITY` dan `SCROLL_DEAD_ZONE_PX`.

## Parameter Konfigurasi Penting

Atur di `src/config.py`:

```python
DEBOUNCE_TIME_MS = 300
SCROLL_SENSITIVITY = 2
SCROLL_DEAD_ZONE_PX = 5
HAND_LOST_GRACE_FRAMES = 4
SMOOTHING_FACTOR = 5.0
```

## Catatan Runtime

- Jika `autopy.mouse.scroll` tidak tersedia pada environment tertentu, aplikasi akan menampilkan warning dan aksi scroll diabaikan.
- Gesture click/right-click menggunakan mekanisme anti-repeat (`click_ready`).
- Sistem default hanya memproses satu tangan (`MAX_NUM_HANDS = 1`).

## Quick Test Checklist

- [ ] Move: `[0,1,1,0,0]` menggerakkan cursor
- [ ] Stop Move: `[1,1,1,0,0]` menghentikan mode gerak
- [ ] Left Click: `[1,0,1,0,0]` memicu klik kiri sekali
- [ ] Right Click: `[1,1,0,0,0]` memicu klik kanan sekali
- [ ] Drag: `[0,0,0,0,0]` menahan klik kiri dan bisa geser objek
- [ ] Scroll: `[1,1,1,1,1]` scroll naik/turun (jika backend mendukung)
