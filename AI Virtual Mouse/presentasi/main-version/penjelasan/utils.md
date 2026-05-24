# utils.py — Penjelasan untuk Pemula

## Tujuan

Fungsi-fungsi kecil untuk overlay teks dan gambar di frame OpenCV. Dipisah biar main loop nggak penuh dengan `cv2.putText()` berulang-ulang.

## Kenapa Kode Ditulis Begini?

### Kenapa fungsi overlay dipisah?

Di video version, semua `cv2.putText()` langsung di main loop. Ini bikin main loop penuh dengan boilerplate: posisi teks, font, ukuran, warna.

Dengan utils, main loop cukup panggil `put_fps(img, fps)` atau `put_mode_text(img, mode)`. Bersih.

### Kenapa mode punya warna sendiri?

`MODE_COLORS` mapping: setiap mode gesture punya warna display berbeda.
- Move = hijau
- Click = biru
- RightClick = oranye
- Drag = merah
- Scroll = kuning

Ini membantu visual debugging — lihat warna teks langsung tahu mode apa.

## Per-Fungsi

### `put_fps(img, fps)`
Tampilkan FPS di pojok kiri atas. Default posisi: `(20, 50)`. Warna hijau.

### `put_mode_text(img, mode)`
Tampilkan mode gesture sekarang. Warna otomatis dari `MODE_COLORS`. Default posisi: `(20, 100)`.

### `put_bounding_box(img, bbox)`
Gambar kotak pembatas di sekitar tangan. Dipakai untuk visual debugging.

### `put_status_text(img, text, pos)`
Fungsi generik untuk teks apa pun. Flexible — bisa dipakai untuk debug message custom.

## Istilah Teknis

- **Overlay:** teks atau gambar yang ditampilkan di atas frame video. Tidak mempengaruhi logic program.
- **Boilerplate:** kode berulang yang strukturnya sama tapi nilainya beda. Diekstrak ke fungsi biar nggak duplikat.
- **BGR tuple:** format warna OpenCV `(Blue, Green, Red)`. `(0, 255, 0)` = hijau (green maksimal, blue/red nol).
