# mouse_controller.py — Penjelasan untuk Pemula

## Tujuan

Thin wrapper (pembungkus tipis) di atas library Autopy. Menerjemahkan action string dari GestureClassifier jadi pemanggilan fungsi mouse yang sebenarnya.

## Kenapa Kode Ditulis Begini?

### Kenapa perlu modul terpisah? Kan cuma wrapper?

Dua alasan:
1. **Abstraksi:** GestureClassifier dan CoordinateMapper nggak perlu tahu cara manggil Autopy. Mereka cuma output string action. Kalau suatu hari ganti library mouse (dari Autopy ke pynput), cuma file ini yang berubah.
2. **Cleanup:** Drag state dilacak di sini. Kalau program crash atau exit, `cleanup()` memastikan tombol mouse nggak tertinggal dalam keadaan "ditahan".

### Kenapa scroll ada fallback?

`autopy.mouse.scroll()` nggak tersedia di versi 4.0.1. Jadi kita cek dulu — kalau ada, pakai. Kalau nggak, fallback ke Windows API via `ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL)`.

Ini pattern yang bagus: **graceful degradation**. Fitur tetap berfungsi walaupun nggak optimal.

### Kenapa koordinat di-clamp?

`screen_x = max(0.0, min(float(screen_x), max_x - 1))`

Koordinat hasil smoothing kadang bisa di luar batas layar (misal -10 atau 1930 di layar 1920px). Kalau nggak di-clamp, Autopy bisa error atau kursor bisa "menghilang" di luar layar.

## Per-Fungsi

### `execute(action, screen_x, screen_y)`

Fungsi utama. Dispatch action string ke operasi mouse yang sesuai.

| action | Yang terjadi |
|---|---|
| `"move"` | `autopy.mouse.move(x, y)` |
| `"click"` | `autopy.mouse.click()` + sleep 100ms |
| `"right_click"` | `autopy.mouse.click(RIGHT)` + sleep |
| `"drag_start"` | `autopy.mouse.toggle(LEFT, down=True)` |
| `"drag_end"` | `autopy.mouse.toggle(LEFT, down=False)` |
| `("scroll", N)` | Scroll N unit (positif ke atas) |

### `cleanup()`

Dipanggil saat program exit. Kalau lagi Drag, lepas tombol mouse. Penting — kalau nggak, mouse bakal stuck dalam keadaan "menahan" sampai di-restart.

### `_scroll(amount)`

Internal. Coba `autopy.mouse.scroll()` dulu. Kalau nggak tersedia → Windows API. Kalau di OS lain tanpa Autopy scroll → print warning dan skip.

## Istilah Teknis

- **Wrapper / thin wrapper:** kode yang "membungkus" library lain. Fungsinya: menyederhanakan interface, menambah error handling, atau menyediakan fallback.
- **Graceful degradation:** fitur tetap berfungsi (walaupun dengan keterbatasan) meskipun dependensi nggak lengkap.
- **Clamping:** membatasi nilai dalam rentang tertentu. `clamp(x, 0, max)` → x dipaksa antara 0 dan max.
- **Toggle (mouse):** tahan atau lepas tombol mouse. Beda dengan click (klik = tekan + lepas cepat). Dipakai buat Drag.
- **MOUSEEVENTF_WHEEL:** konstanta Windows API (`0x0800`) untuk event scroll wheel.
- **Wheel delta:** satuan scroll di Windows. `120` = 1 "notch" scroll. Dikali jumlah unit yang diminta.
