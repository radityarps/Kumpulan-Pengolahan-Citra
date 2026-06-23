# 📚 Rangkuman UTS - Pengolahan Citra Digital

> Kisi-kisi: Piksel, Grayscale vs Berwarna, Sistem Koordinat (Scikit-image), Format File & Kompresi, Segmentasi Citra  
> Sumber: Jobsheet 01–04

---

## 1. KONSEP FUNDAMENTAL PIKSEL

### Apa itu Piksel?
- **Piksel** (*Picture Element*) = elemen terkecil penyusun citra digital
- Citra digital **bukan gambar kontinu**, melainkan **diskrit** (tersusun dari kotak-kotak piksel)
- Setiap piksel menyimpan **nilai numerik** yang merepresentasikan intensitas/warna
- Semakin banyak piksel dalam satu area → semakin halus detail gambar (resolusi tinggi)

### Representasi Piksel dalam NumPy
- Citra dimuat sebagai `numpy.ndarray` (matriks multidimensi)
- Tipe data piksel: `uint8` → rentang nilai **0–255** (8-bit per kanal)
- Contoh nilai piksel grayscale: `0` = hitam, `255` = putih

### Perhitungan Ukuran Citra
```
Total piksel = Height × Width
Grayscale: ukuran = Total piksel × 8 bit (1 byte/piksel)
RGB:       ukuran = Total piksel × 24 bit (3 byte/piksel)
```

---

## 2. PERBEDAAN CITRA GRAYSCALE VS BERWARNA (RGB)

| Aspek | Grayscale | Berwarna (RGB) |
|-------|-----------|----------------|
| **Dimensi Array** | 2D: `(H, W)` | 3D: `(H, W, 3)` |
| **Nilai per Piksel** | 1 nilai intensitas | 3 nilai (R, G, B) |
| **Kedalaman Bit** | 8 bit/piksel | 24 bit/piksel |
| **Ukuran File** | Lebih kecil | 3× lebih besar (resolusi sama) |
| **Rentang Nilai** | 0–255 (tingkat keabuan) | 0–255 per kanal (16 juta+ kombinasi) |
| **Contoh Shape** | `(303, 384)` | `(512, 512, 3)` |

### Model Warna Aditif RGB
- **Warna Primer**: R=(255,0,0), G=(0,255,0), B=(0,0,255)
- **Warna Sekunder (Campuran 2 primer)**:
  - Kuning = R+G = (255,255,0)
  - Cyan = G+B = (0,255,255)
  - Magenta = R+B = (255,0,255)
- **Putih** = R+G+B = (255,255,255)
- **Hitam** = (0,0,0) → ketiadaan semua warna

### Urutan Kanal dalam Scikit-image
- `image[:, :, 0]` → **Red** (Merah)
- `image[:, :, 1]` → **Green** (Hijau)
- `image[:, :, 2]` → **Blue** (Biru)
- Citra berwarna = "tumpukan" 3 citra grayscale (masing-masing mewakili intensitas warna primer)

---

## 3. SISTEM KOORDINAT GAMBAR (Scikit-image)

### Perbedaan dengan Koordinat Kartesius

```
Citra Digital:              Kartesius (Matematika):
(0,0) ────────→ X           ↑ Y
  │                         │
  │                         │
  │                         │
  ↓ Y                  (0,0)────→ X
```

### Karakteristik Sistem Koordinat Citra
- **Titik asal (0,0)** berada di **pojok kiri atas** (BUKAN kiri bawah)
- **Sumbu X** → ke arah kanan (lebar/kolom)
- **Sumbu Y** → ke arah bawah (tinggi/baris)
- **Titik maksimum** = `(Width-1, Height-1)`
- Contoh citra Coins (303×384): titik terjauh = `(383, 302)`

### Akses Piksel dalam NumPy
```python
# Format: image[y, x] atau image[baris, kolom]
image[0, 0]      # piksel pojok kiri atas
image[H-1, W-1]  # piksel pojok kanan bawah
image[y, x, 0]   # kanal Red pada koordinat (x,y)
```

> ⚠️ **PENTING**: Dalam NumPy, indeks pertama = baris (Y), indeks kedua = kolom (X).  
> Jadi `image[y, x]` BUKAN `image[x, y]`!

---

## 4. FORMAT FILE CITRA & PRINSIP KOMPRESI

### Perbandingan Format

| Format | Kompresi | Ukuran File | Kualitas | Kegunaan |
|--------|----------|-------------|----------|----------|
| **BMP** | Tidak terkompresi | Sangat besar (~768 KB) | Sempurna (lossless) | Pengolahan citra presisi tinggi |
| **JPEG** | Lossy | Paling kecil (~27–97 KB) | Berkurang (ada artefak) | Fotografi, web, media sosial |
| **TIFF** | Lossy atau Lossless | Besar (~768 KB) | Sangat baik | Percetakan, citra medis |
| **PNG** | Lossless | Sedang (~414 KB) | Sempurna | Web, ilmiah, data piksel utuh |

### Kompresi Lossy vs Lossless

| Aspek | Lossy (JPEG) | Lossless (PNG/BMP) |
|-------|-------------|-------------------|
| **Prinsip** | Membuang data yang tidak tertangkap mata | Kompres tanpa menghapus data |
| **Ukuran** | Jauh lebih kecil | Lebih besar |
| **Kualitas** | Ada artefak (kotak-kotak halus) | 100% utuh, piksel tidak berubah |
| **Reversibel?** | TIDAK — data hilang permanen | YA — bisa dikembalikan ke asli |
| **Parameter** | Quality (1–100): makin tinggi → makin besar & bagus | Tidak ada parameter kualitas |

### Dampak Parameter Quality pada JPEG
- **Q=50**: Ukuran sangat kecil (~27 KB), artefak jelas terlihat, detail hilang
- **Q=90**: Ukuran sedang (~66 KB), artefak minim, mata sulit bedakan dengan asli
- **Q=95**: Ukuran lebih besar (~97 KB), kualitas hampir sempurna

### Kapan Pakai Apa?
- **Analisis citra ilmiah/medis** → BMP/TIFF/PNG (tiap piksel penting!)
- **Web/media sosial** → JPEG (hemat memori)
- **Perlu transparansi** → PNG

---

## 5. DETEKSI TEPI (Jobsheet 2)

### Operator Deteksi Tepi

| Operator | Kernel | Karakteristik |
|----------|--------|---------------|
| **Sobel** | 3×3 | Garis tepi tebal & halus, ada arah X dan Y |
| **Roberts** | 2×2 | Garis paling tipis & tajam, sangat sensitif noise |
| **Prewitt** | 3×3 | Mirip Sobel, sedikit lebih kasar |
| **Kirsch** | Kompas 8 arah | Kontras sangat tajam, deteksi multi-arah |
| **Canny** | Multi-step | **Paling bersih & presisi**, garis 1 piksel, noise suppression |

### Detail Algoritma Canny
1. **Smoothing** — Gaussian blur untuk reduksi noise
2. **Gradien** — Hitung magnitude & arah gradien (Sobel)
3. **Non-maximum suppression** — Tipiskan garis tepi menjadi 1 piksel
4. **Double thresholding** — Klasifikasi piksel: strong, weak, non-edge
5. **Hysteresis** — Hubungkan weak edge yang terhubung ke strong edge

### Sobel: Gradien X vs Y
- `sobel_h` → **gradien horizontal** → sensitif garis vertikal
- `sobel_v` → **gradien vertikal** → sensitif garis horizontal
- `sobel` → kombinasi keduanya

### Deteksi Tepi pada Citra Berwarna
- Proses tiap kanal R, G, B secara terpisah
- Gabungkan hasil dengan `np.stack()`
- Lebih komprehensif daripada konversi ke grayscale dulu

---

## 6. PERBAIKAN CITRA DOMAIN SPASIAL (Jobsheet 3)

### Transformasi Intensitas

| Metode | Formula | Efek |
|--------|---------|------|
| **Negatif** | `s = 1.0 - r` (float) atau `s = 255 - r` (uint8) | Balik warna: gelap↔terang |
| **Logaritmik** | `s = c × log(1 + r)` | Perluas area gelap, mampat area terang |
| **Gamma** | `s = c × r^γ` | γ<1 → lebih terang; γ>1 → lebih gelap |

### Peningkatan Kontras

| Metode | Prinsip | Karakteristik |
|--------|---------|---------------|
| **Contrast Stretching** | Tarik histogram ke rentang penuh secara linear | Alami, mempertahankan hubungan kecerahan |
| **Histogram Equalization** | Ratakan distribusi intensitas | Kontras kuat, bisa terlihat "dipaksakan" |

- Stretching: bentuk histogram mirip asli, hanya diperlebar
- Equalization: histogram jadi datar/uniform

### Filtering

| Filter | Cara Kerja | Kelebihan | Kekurangan |
|--------|-----------|-----------|------------|
| **Rata-rata (Mean)** | Ganti piksel dengan rata-rata tetangga | Menghaluskan noise halus | Blur tepi, noise S&P jadi bercak abu-abu |
| **Median** | Ganti piksel dengan nilai tengah tetangga | **Hapus noise S&P sempurna**, jaga tepi tetap tajam | Lebih lambat |

> **Untuk noise salt-and-pepper → selalu pakai Median!**  
> Mean filter gagal karena nilai ekstrem (0/255) ikut dihitung rata-rata.

---

## 7. SEGMENTASI CITRA (Jobsheet 4)

### Metode Segmentasi

#### A. Thresholding
| Jenis | Prinsip | Kelebihan | Kekurangan |
|-------|---------|-----------|------------|
| **Manual** | Tentukan nilai T sendiri | Simpel | T harus tepat, mudah salah |
| **Otsu** | Minimasi varians dalam-kelas otomatis | Otomatis, optimal untuk histogram bimodal | Gagal jika pencahayaan tidak merata |
| **Yen** | Metode global lain | Kadang lebih baik dari Otsu | Tetap kesulitan bayangan |
| **Local/Adaptive** | Hitung T per area tetangga | **Terbaik untuk dokumen/cahaya tidak merata** | Lebih lambat |

```python
# Otsu
thresh = filters.threshold_otsu(image)
binary = image > thresh

# Local
binary_local = filters.threshold_local(image, block_size=35, offset=10)
result = image > binary_local
```

#### B. Region-Based (Flood Fill)
- Mulai dari **seed point** → "isi" area terhubung yang mirip intensitas
- Parameter `tolerance` → ambang perbedaan intensitas agar masuk 1 region
- **Sensitif terhadap posisi seed & nilai tolerance**
- Cocok untuk isolasi area yang seragam & terhubung spasial

#### C. Clustering (K-Means)
- Kelompokkan piksel berdasarkan kemiripan warna/intensitas
- Gunakan **ruang warna Lab** (bukan RGB) → lebih sesuai persepsi manusia
- Parameter `K` = jumlah kluster → makin besar makin detail
- **Tidak mempertimbangkan posisi spasial** → bisa muncul noise/bintik kecil
- Cocok untuk **color quantization** & segmentasi multi-level

#### D. Watershed
- Anggap gradien citra sebagai **permukaan topografi**
- Air "mengalir" dari **markers** → mengisi cekungan → bertemu di watershed lines
- **Penting**: Gunakan Sobel untuk elevation map + tentukan markers yang tepat
- Tanpa marker tepat → **over-segmentation** (objek pecah jadi banyak bagian)
- **Terbaik untuk memisahkan objek yang bersentuhan/berhimpitan**

### Perbandingan Metode Segmentasi

| Metode | Keunggulan | Kelemahan | Cocok Untuk |
|--------|-----------|-----------|-------------|
| **Otsu** | Cepat, sederhana, otomatis | Hanya biner, gagal jika cahaya tidak merata | Citra kontras tinggi, histogram bimodal |
| **K-Means** | Multi-level (K>2), berbasis warna | Abaikan posisi spasial, ada noise bintik | Color quantization, variasi intensitas |
| **Watershed** | Batas objek paling presisi | Rentan over-segmentation tanpa marker tepat | Objek bersentuhan/berhimpitan |
| **Flood Fill** | Isolasi area spesifik | Sangat sensitif seed point & tolerance | Area seragam yang terhubung |
| **Local Threshold** | Handle cahaya tidak merata | Lebih lambat | Dokumen, teks |

---

## ⚡ POINTERS UNTUK UJIAN

1. **Piksel = elemen terkecil**, citra = diskrit (bukan kontinu), nilai 0–255 (uint8)
2. **Grayscale**: shape (H,W), 1 nilai/piksel, 8-bit. **RGB**: shape (H,W,3), 3 nilai/piksel, 24-bit
3. **Koordinat**: (0,0) = kiri atas, X→kanan, Y→bawah. Akses: `image[y,x]` (baris,kolom)
4. **BMP** = lossless besar. **JPEG** = lossy kecil ada artefak. **PNG** = lossless sedang. **TIFF** = fleksibel
5. **Lossy** = data hilang permanen (JPEG). **Lossless** = data utuh (PNG/BMP)
6. **Median filter** > Mean filter untuk noise salt-and-pepper (jaga tepi tajam)
7. **Canny** = deteksi tepi terbaik (bersih, presisi). **Roberts** = paling tipis tapi sensitive noise
8. **Otsu** = threshold otomatis (minimasi varians dalam-kelas), cocok histogram bimodal
9. **Local threshold** = solusi pencahayaan tidak merata (dokumen)
10. **Watershed** = pisahkan objek bersentuhan, perlu marker tepat, pakai Sobel untuk elevation map
11. **K-Means** = segmentasi multi-level berbasis warna, pakai ruang Lab, tidak spasial
12. **Flood fill** = region-based, butuh seed point + tolerance
