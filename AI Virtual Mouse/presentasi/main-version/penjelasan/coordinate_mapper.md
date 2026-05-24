# coordinate_mapper.py — Penjelasan untuk Pemula

## Tujuan

Mapping koordinat dari kamera (640×480 pixel) ke layar (misal 1920×1080), plus smoothing untuk mengurangi getaran kursor.

## Kenapa Kode Ditulis Begini?

### Kenapa perlu modul terpisah?

Di video version, mapping dan smoothing dilakukan inline di main loop dengan `np.interp()` dan EMA manual. Dengan modul terpisah:
- Bisa dites: "apakah koordinat (320, 240) beneran ke tengah layar?"
- Bisa di-tuning: ganti `SMOOTHING_FACTOR` di config, nggak perlu sentuh kode mapper
- Drag anchor jadi lebih clean: anchor disimpan di mapper, bukan di main loop

### Kenapa pakai frame_reduction?

Tanpa frame reduction, tangan yang ada di pinggir frame bakal gerakin kursor ke ujung layar. Ini nggak nyaman — kita harus gerak tangan jauh-jauh.

Dengan `FRAME_REDUCTION = 100px`, area 100px di pinggir frame jadi dead zone. Kursor cuma gerak di 440px tengah frame. Ini bikin kontrol lebih nyaman.

### Kenapa smoothing pakai EMA?

Exponential Moving Average ngasih bobot lebih ke data terbaru:

```
smooth_new = smooth_old + (raw - smooth_old) / SMOOTHING_FACTOR
```

- `SMOOTHING_FACTOR = 1`: nggak ada smoothing (smooth = raw)
- `SMOOTHING_FACTOR = 5`: smoothing moderate (nilai sekarang = 80% lama + 20% baru)
- `SMOOTHING_FACTOR = 10`: smoothing agresif (lebih smooth tapi lebih lag)

### Kenapa drag pakai anchor-based movement?

Tanpa anchor, begitu masuk mode Drag, kursor langsung loncat ke posisi jari. Ini nggak natural — kita maunya kursor mulai dari posisi terakhir, terus gerak relatif dari situ.

Dengan anchor:
1. Saat Drag dimulai → catat: (posisi jari di kamera, posisi kursor di layar)
2. Selama Drag → `kursor_baru = kursor_anchor + (jari_sekarang - jari_anchor) * scale`
3. Kursor bergerak relatif dari anchor, bukan absolut dari jari

## Per-Fungsi

### `map_to_screen(cx, cy)`
Input: koordinat pixel kamera. Output: koordinat pixel layar (mentah, belum smoothing).
```python
x = np.interp(cx, [100, 540], [0, 1920])
```

### `smooth(raw_x, raw_y)`
Input: koordinat mentah. Output: koordinat yang udah di-smoothing.
First call langsung set ke raw (biar nggak ada convergence lag).

### `process(cx, cy)`
Convenience: `map_to_screen` + `smooth` dalam satu panggilan. Dipakai di mode Move.

### `set_drag_anchor(cam_x, cam_y, screen_x, screen_y)`
Catat anchor Drag. Dipanggil sekali pas Drag mulai.

### `process_drag(cx, cy)`
Hitung posisi kursor relatif dari anchor. Dipakai di mode Drag.

### `reset_smoothing()`
Reset state smoothing. Dipanggil pas tangan hilang — biar pas tangan muncul lagi, kursor nggak loncat dari posisi terakhir yang udah basi.

## Istilah Teknis

- **Linear Interpolation (`np.interp`):** mapping linear dari satu rentang ke rentang lain. `np.interp(320, [100,540], [0,1920])` → ~960 (tengah layar).
- **Scale factor:** rasio pixel layar vs pixel kamera. `1920 / 440 = 4.36` — artinya tiap 1 pixel gerakan tangan = 4.36 pixel gerakan kursor.
- **Convergence lag:** jeda waktu dari nilai awal (nol) menuju nilai stabil pertama. Dihindari dengan langsung set ke raw value pada first call.
- **Drag sensitivity:** multiplier buat delta drag. `1.0` = sama persis kayak mode Move. `<1.0` = lebih lambat. `>1.0` = lebih cepat.
