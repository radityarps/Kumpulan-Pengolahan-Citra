# AIVirtualMouse.py — Penjelasan untuk Pemula

## Tujuan File Ini

Ini file utama yang dijalankan. Dia yang ngatur webcam, panggil HandDetector, klasifikasi gestur, mapping koordinat, dan kontrol mouse. Semua logic dalam satu loop `while True`.

## Kenapa Kode Ditulis Begini?

### Kenapa semua dalam satu file?

Karena ini replikasi tutorial. Tutorial asli emang semua logic dalam satu file. Tujuannya: sederhana, gampang diikuti. Tapi ini juga kelemahannya — nggak modular, susah dites, susah diubah.

### Kenapa pakai autopy?

Autopy adalah library Python buat kontrol mouse/keyboard cross-platform. Alternatif lain: `pyautogui`, `pynput`, `mouse`. Autopy dipilih karena lebih ringan dan lebih cepat dari pyautogui.

### Kenapa scroll pakai ctypes?

`autopy.mouse.scroll()` ternyata nggak tersedia di versi 4.0.1 (bug/oversight). Jadi saya fallback ke Windows API langsung lewat `ctypes.windll.user32.mouse_event()`. Ini Windows-only — kalau jalan di Mac/Linux, scroll nggak akan berfungsi.

## Struktur Main Loop

```
while True:
    1. Capture frame dari webcam
    2. Mirror gambar (cv2.flip)
    3. Deteksi tangan (detector.findHands)
    4. Ekstrak posisi landmark (detector.findPosition)
    5. Cek jari naik/turun (detector.fingersUp)
    6. Klasifikasi gestur (if-elif block)
    7. Eksekusi action (autopy)
    8. Tampilkan FPS + mode
    9. Cek keyboard (q = quit)
```

## Per-Blok Gesture

### Move — `[*, 1, 0, 0, 0]`

- Kondisi: telunjuk naik, tiga jari lain turun. Jempol diabaikan.
- Ambil koordinat ujung telunjuk (landmark 8)
- Mapping dari koordinat kamera → koordinat layar pakai `np.interp()`
- Smoothing: Exponential Moving Average
- Gerakin kursor ke posisi hasil smoothing

### Left Click — `[*, 1, 1, 0, 0]`

- Kondisi: telunjuk + tengah naik
- Ukur jarak antara telunjuk (8) dan tengah (12)
- Kalau jarak < 28px DAN `click_ready = True` → klik kiri
- `click_ready` jadi False → mencegah spam click
- Begitu jarak > 28px → `click_ready` balik True (re-arm)

### Right Click — `[*, 1, 1, 1, 0]`

- Kondisi: telunjuk + tengah + manis naik
- Ukur jarak telunjuk (8) ke jari manis (16)
- Kalau jarak < 34px → klik kanan
- Sama seperti left click: edge-triggered dengan `click_ready`

### Drag — `[*, 0, 0, 0, 0]`

- Kondisi: kepalan (semua jari turun). Jempol diabaikan.
- Saat pertama masuk Drag: catat anchor (posisi jari di kamera + posisi kursor di layar)
- Selanjutnya: kursor bergerak relatif dari anchor
  - `dx = current_finger_x - anchor_finger_x`
  - `dy = current_finger_y - anchor_finger_y`
  - `new_cursor_x = anchor_cursor_x + dx * scale_x`
- Kenapa anchor-based? Biar kursor nggak loncat ke posisi jari saat masuk mode Drag. Natural.

### Scroll — `[*, 1, 1, 1, 1]`

- Kondisi: keempat jari naik semua
- Kamera dibagi 3 zona: atas (scroll up), tengah (dead zone), bawah (scroll down)
- Dead zone: ±35px dari garis tengah kamera — di area ini nggak scroll
- Scroll pakai `_scroll()` → `ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL)`
- Rate-limited: minimal 120ms antar scroll

## Fungsi Helper

### `_match_pattern(fingers, pattern)`

Membandingkan state jari dengan pola gesture. `None` berfungsi sebagai wildcard — nilai di posisi itu diabaikan.

Contoh: `_match_pattern([1, 1, 0, 0, 0], [None, 1, 0, 0, 1])` → False (kelingking beda)

### `_scroll(amount)`

Scroll mouse wheel. Coba `autopy.mouse.scroll()` dulu. Kalau nggak ada (AttributeError), fallback ke Windows API.

## Istilah Teknis

- **Edge-triggered**: aksi dipicu hanya saat transisi (dari kondisi false ke true), bukan selama kondisi true. Mencegah spam.
- **Exponential Moving Average (EMA)**: smoothing yang memberi bobot lebih ke data terbaru. Formula: `new = old + (raw - old) / factor`.
- **Anchor-based movement**: pergerakan relatif dari titik referensi, bukan absolut. Dipakai di Drag.
- **Dead zone**: area di mana input diabaikan. Dipakai di Scroll (tengah kamera) dan coordinate mapping (pinggir frame).
- **Rate limiting**: membatasi frekuensi aksi (misal scroll max tiap 120ms).
