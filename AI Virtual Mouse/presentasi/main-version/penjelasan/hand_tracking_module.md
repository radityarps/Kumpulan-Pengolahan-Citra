# hand_tracking_module.py — Penjelasan untuk Pemula

## Tujuan

Modul yang menangani semua interaksi dengan MediaPipe. Deteksi tangan, ekstrak 21 landmark, cek jari naik/turun, hitung jarak antar landmark.

## Perbedaan dari Video Version

| Aspek | Video Version | Main Version |
|---|---|---|
| Thumb detection | x-coordinate (handedness-dependent) | Distance-based (MCP ke tip) |
| Drawing | Cyan (255,255,0) | Cyan dari config |
| Import | Relative path ke model | Model di folder `src/` |
| Config | Hardcoded | Import dari `src/config.py` |

## Kenapa Kode Ditulis Begini?

### Kenapa thumb detection pakai distance?

Di video version, thumb detection pakai x-coordinate: `if tip[4].x > tip[3].x`. Ini cuma berfungsi buat tangan kanan.

Di main version, kita ukur **jarak Euclidean** antara MCP (landmark 2, pangkal jempol) dan TIP (landmark 4, ujung jempol). Jempol naik → jaraknya besar. Jempol turun → jaraknya kecil. Ini handedness-independent — berfungsi buat tangan kiri maupun kanan.

### Kenapa ada `THUMB_SENSITIVITY`?

Karena threshold "35 pixel" itu subjektif. Tangan orang dewasa vs anak-anak beda ukuran. Jarak kamera juga pengaruh.

`THUMB_SENSITIVITY = 1.5` artinya threshold jadi `35 * 1.5 = 52.5px`. Lebih tinggi = lebih strict (jempol harus lebih jauh buat dianggap naik). Bisa di-tuning di `config.py`.

## Per-Fungsi

Sama seperti video version (`findHands`, `findPosition`, `fingersUp`, `findDistance`, `_draw_landmarks`). Yang berbeda hanya `fingersUp()` bagian thumb:

```python
# Main version: distance-based
thumb_tip = self.lmList[4]   # ujung jempol
thumb_mcp = self.lmList[2]   # pangkal jempol
thumb_dist = math.hypot(tip[1]-mcp[1], tip[2]-mcp[2])
threshold = 35.0 * THUMB_SENSITIVITY  # default: 52.5px
if thumb_dist > threshold:
    fingers.append(1)  # naik
```

## Istilah Teknis

- **MCP (Metacarpophalangeal):** sendi pangkal jari, dekat telapak tangan. Landmark 2 untuk jempol.
- **TIP:** ujung jari. Landmark 4 untuk jempol.
- **Distance-based detection:** deteksi berdasarkan jarak Euclidean dua titik. Lebih robust dari x-coordinate comparison.
- **Sensitivity:** faktor pengali threshold. Memungkinkan tuning tanpa ganti kode.
