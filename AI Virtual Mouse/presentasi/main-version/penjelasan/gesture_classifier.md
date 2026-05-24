# gesture_classifier.py — Penjelasan untuk Pemula

## Tujuan

Modul paling penting di main version. Menggantikan if-elif block sederhana di video version dengan **state machine** yang punya memori. Output: mode gesture (`"Move"`, `"Click"`, dll) dan action (`"click"`, `"drag_start"`, dll).

## Kenapa Kode Ditulis Begini?

### Kenapa perlu state machine?

Video version: tiap frame diproses independen. Frame ini gesture Drag, frame berikutnya (flicker) → langsung ganti mode. Hasil: gesture nggak stabil.

State machine ingat gesture sebelumnya. Transisi antar gesture diproses dengan aturan: debounce, hysteresis, hold-time. Bukan cuma "jari lagi gimana sekarang".

### Kenapa debounce 300ms?

Gesture baru harus bertahan **300 milidetik** sebelum diakui sebagai mode stabil. Dalam 300ms di 30fps = 9 frame. Kalau flicker cuma 1-2 frame → diabaikan.

```python
if detected_mode != self.current_mode:
    self.current_mode = detected_mode
    self.mode_start_time = now       # catat waktu mulai
else:
    if now - self.mode_start_time >= self.debounce_ms:
        self.stable_mode = detected_mode  # baru diakui setelah 300ms
```

### Kenapa hysteresis?

Batas "mulai klik" (ON = 28px) beda sama batas "berhenti klik" (OFF = 38px). Tanpa hysteresis, di boundary 28-29px, klik bakal bolak-balik ON/OFF tiap frame.

Dengan hysteresis:
- Pinch turun ke 24px → klik (melewati ON threshold)
- Pinch naik ke 32px → masih dalam state klik (belum melewati OFF)
- Pinch naik ke 40px → baru lepas (melewati OFF threshold)

### Kenapa hold-time 100ms?

Klik kiri butuh pinch bertahan **100ms** di bawah threshold sebelum trigger. Mencegah klik nggak sengaja pas jari sekilas lewat.

### Kenapa post-click freeze 200ms?

Setelah klik, kursor di-freeze 200ms. Kenapa? Karena pas kita pinch, jari reflek gerak dikit. Tanpa freeze, kursor ikut gerak → klik di tempat yang salah.

### Kenapa hand-lost grace 4 frame?

Kalau tangan hilang dari frame (kedip, gerak terlalu cepat), state dipertahankan sampai 4 frame. Baru reset setelah frame ke-5. Mencegah Drag putus cuma karena tangan sebentar nggak kedeteksi.

## Flow Klasifikasi

```
fingers + distances
    │
    ▼
_detect_gesture()  ─── cek semua gesture pattern ─── return (mode, action)
    │
    ▼
classify()  ─── debounce check ─── return stable_mode, action
```

## Per-Gesture Handling

### Move
- Pattern matching dengan semua `move_patterns` di profile
- Release drag kalau sebelumnya lagi drag
- Clear click states

### Left Click (`_handle_left_click`)
- Pinch ≤ 28px (ON) → mulai timer hold-time
- Hold 100ms → trigger `"click"`, set `left_pinch_active = True`
- Pinch naik ≥ 38px (OFF) → release pinch state, re-arm click
- Selama pinch active, nggak trigger klik lagi

### Right Click (`_handle_right_click`)
- Sama seperti left click tapi pakai threshold 34px/44px dan jarak telunjuk-manis

### Drag
- Pattern: `[None, 0, 0, 0, 0]` (kepalan)
- Return `"Drag"` sebagai mode, `"drag_start"` sebagai action (pertama kali)
- Selanjutnya return `"move"` (koordinat di-handle oleh CoordinateMapper)

### Scroll
- Pattern: `[None, 1, 1, 1, 1]` (4 jari naik)
- Cek posisi y telunjuk relatif ke garis tengah kamera
- Di atas dead zone → scroll up. Di bawah → scroll down.
- Rate-limited: `SCROLL_REPEAT_MS` (120ms)

## Istilah Teknis

- **State Machine:** sistem yang punya state (kondisi saat ini) dan aturan transisi antar state. Lebih kompleks dari if-else tapi lebih robust.
- **Debounce:** menunggu sinyal stabil selama periode tertentu sebelum bereaksi. Menghilangkan noise/flicker.
- **Hysteresis:** batas ON dan OFF berbeda. Mencegah osilasi di sekitar threshold.
- **Hold-time:** durasi minimal suatu kondisi harus bertahan sebelum dianggap valid.
- **Post-click freeze:** jeda setelah klik di mana kursor tidak bergerak. Mencegah drift.
- **Hand-lost grace:** toleransi kehilangan deteksi tangan untuk beberapa frame.
