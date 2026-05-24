# HandTrackingModule.py — Penjelasan untuk Pemula

## Tujuan File Ini

File ini bertugas mendeteksi tangan di gambar dari webcam. Dia "membungkus" (wrap) library MediaPipe supaya lebih mudah dipakai. Output-nya: posisi 21 titik landmark tangan dan status jari (naik/turun).

## Kenapa Kode Ditulis Begini?

### Kenapa pakai Tasks API, bukan Solutions API?

Tutorial asli pakai `mp.solutions.hands` (Solutions API). Tapi API ini udah **dihapus total** dari MediaPipe versi 0.10.30 ke atas. Jadi nggak bisa dipakai lagi.

Tasks API (`mediapipe.tasks.vision.HandLandmarker`) adalah penggantinya. Cara pakainya beda:
- Solutions API: `hands = mp.solutions.hands.Hands(); results = hands.process(img)`
- Tasks API: perlu file model `.task` terpisah, perlu konversi gambar ke `mp.Image`, perlu handle hasil deteksi secara manual

Tapi **public interface** (cara manggil dari luar) saya buat persis sama. Jadi file lain nggak perlu tahu API mana yang dipakai.

### Kenapa gambar harus di-convert?

```python
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_rgb = np.ascontiguousarray(img_rgb, dtype=np.uint8)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
```

Tiga langkah ini wajib karena:
1. OpenCV baca gambar dalam format **BGR** (Blue-Green-Red). MediaPipe maunya **RGB**.
2. Tasks API perlu array yang **contiguous** di memori (nggak boleh ada gap antar byte).
3. Tasks API perlu gambar dibungkus dalam objek `mp.Image` khusus.

## Per-Fungsi

### `__init__(self, mode, max_hands, detection_con, track_con)`

**Input:** parameter konfigurasi (max_hands=1 artinya deteksi maksimal 1 tangan, detection_con=0.5 artinya confidence minimal 50% buat deteksi).

**Logic:** bikin objek `HandLandmarker` dari MediaPipe Tasks API. Load file model `hand_landmarker.task`.

**Output:** objek `HandDetector` siap pakai.

### `findHands(self, img, draw=True)`

**Input:** gambar BGR dari webcam. `draw=True` artinya gambar landmark di atas gambar.

**Logic:** convert gambar, deteksi tangan, kalau `draw=True` → gambar garis landmark.

**Output:** gambar yang sama (dengan atau tanpa overlay landmark).

### `findPosition(self, img, hand_no=0, draw=True)`

**Input:** gambar (buat dimensi), indeks tangan ke berapa (0 = tangan pertama), `draw=True` buat gambar titik landmark.

**Logic:** ambil hasil deteksi, convert 21 landmark dari koordinat normal (0.0-1.0) ke koordinat pixel (0-640, 0-480). Hitung bounding box (kotak pembatas) tangan.

**Output:** dua hal:
- `lmList`: list of `[id, x, y]` — id landmark (0-20), koordinat x, koordinat y
- `bbox`: `(xmin, ymin, xmax, ymax)` — kotak yang membungkus tangan

### `fingersUp(self)`

**Input:** nggak ada (pakai internal `self.lmList` yang udah diisi `findPosition()`).

**Logic Deteksi Jari:**

- **Jempol:** x-coordinate comparison. `if tip[4].x > tip[3].x` → jempol naik.
  - ⚠️ Ini cuma berfungsi buat tangan kanan. Tangan kiri hasilnya kebalik.
  - Di sistem gesture, jempol sengaja **diabaikan** (`None` wildcard).

- **4 jari lain (telunjuk, tengah, manis, kelingking):** y-coordinate comparison.
  - `if tip.y < PIP.y` → jari naik.
  - Kenapa? Karena di gambar, titik (0,0) ada di pojok kiri atas. Jadi semakin ke atas = nilai y semakin kecil.
  - Ujung jari yang naik → posisinya lebih atas → y lebih kecil dari sendi PIP.

**Output:** list 5 angka biner. Contoh: `[1, 1, 0, 0, 0]` artinya jempol naik, telunjuk naik, tiga lainnya turun.

### `findDistance(self, p1, p2, img, draw, r, t)`

**Input:** dua ID landmark (misal 8 dan 12 buat telunjuk-tengah), gambar opsional buat drawing.

**Logic:** hitung jarak Euclidean (teorema Pythagoras) antara dua titik.

```python
length = math.hypot(x2 - x1, y2 - y1)
```

**Output:** tiga hal — jarak (float), gambar yang udah di-gambar, dan list koordinat `[x1, y1, x2, y2, cx, cy]`.

### `_draw_landmarks(self, img, hand_landmarks)`

Fungsi internal (private, diawali `_`). Gambar garis-garis koneksi landmark tangan. Garis cyan di antara titik-titik jari.

## Istilah Teknis

- **Landmark**: titik referensi. MediaPipe punya 21 landmark per tangan (pergelangan, sendi, ujung jari).
- **Contiguous array**: array yang elemen-elemennya tersimpan berurutan di memori. Syarat teknis MediaPipe Tasks API.
- **Normalized coordinates**: koordinat 0.0-1.0 (proporsi dari lebar/tinggi gambar). Dikonversi ke pixel dengan `int(lm.x * w)`.
- **Bounding box**: kotak terkecil yang membungkus semua titik landmark.
