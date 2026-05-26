# 🎯 PANDUAN BELAJAR UTS - PENGOLAHAN CITRA DIGITAL

> **Kisi-kisi**: Piksel, Grayscale vs Berwarna, Sistem Koordinat Scikit-image, Format File & Kompresi, Segmentasi Citra  
> **Format Ujian**: 30 PG + 3 Essay  
> **Sumber**: Jobsheet 01–04

---

## 🔰 STRATEGI BELAJAR

### Prioritas Belajar (dari yang paling sering keluar)

| Prioritas | Topik | Bobot Perkiraan | Alasan |
|-----------|-------|-----------------|--------|
| ⭐⭐⭐ | Piksel & Representasi Grayscale vs RGB | ~25% | Fundamental, muncul di setiap jobsheet |
| ⭐⭐⭐ | Format File & Kompresi (Lossy vs Lossless) | ~20% | Sering jadi bahan PG analitis |
| ⭐⭐⭐ | Segmentasi Citra (Thresholding, Watershed, K-Means) | ~25% | Topik terberat, kandidat essay |
| ⭐⭐ | Sistem Koordinat Citra | ~10% | Cenderung soal PG konseptual |
| ⭐⭐ | Deteksi Tepi (Sobel, Canny, dll) | ~10% | Bisa jadi essay perbandingan |
| ⭐ | Perbaikan Citra (Filtering, Histogram) | ~10% | Pendukung, bisa masuk essay |

### Cara Belajar per Topik

1. **Piksel & Representasi** → Hafalkan rumus ukuran, bedakan shape, pahami per kanal RGB
2. **Koordinat** → Gambar sumbu X-Y, latih soal `image[y,x]` vs `image[x,y]`
3. **Format File**→ Buat tabel perbandingan, pahami konep lossy vs lossless
4. **Segmentasi** → Pahami kapan pakai metode apa, latih coding Otsu & Watershed
5. **Deteksi Tepi** → Bandingkan karakteristik 5 operator, fokus Canny vs Roberts
6. **Perbaikan Citra** → Fokus Median vs Mean untuk noise S&P

---

## 📖 SILABUS DETAIL: APA YANG HARUS DIKUASAI

### MODUL 1: PIKSEL & REPRESENTASI DATA

#### Yang HARUS dihafal
- Piksel = *picture element* = elemen terkecil citra digital
- Citra digital bersifat **diskrit** (bukan kontinu)
- Tipe data piksel: `uint8` → rentang **0–255**
- Rumus ukuran citra:
  ```
  Grayscale: ukuran = H × W × 1 byte
  RGB:       ukuran = H × W × 3 byte
  ```
- Contoh: citra 512×512 grayscale = 512×512×1 = 262.144 byte ≈ 256 KB
- Contoh: citra 512×512 RGB = 512×512×3 = 786.432 byte ≈ 768 KB

#### Yang HARUS dipahami (bukan dihafal)
- Citra grayscale: array 2D `(H, W)`, tiap piksel 1 nilai intensitas
- Citra RGB: array 3D `(H, W, 3)`, tiap piksel 3 nilai (R, G, B)
- Urutan kanal scikit-image: `[:,:,0]`=R, `[:,:,1]`=G, `[:,:,2]`=B
- Model warna aditif RGB: campuran cahaya, bukan pigmen
  - R+G=Kuning, G+B=Cyan, R+B=Magenta, R+G+B=Putih, (0,0,0)=Hitam
- Citra RGB = tumpukan 3 citra grayscale → ukuran 3× lipat

#### Cara belajar
- Buka Jobsheet 1, kode 1 & 3 → pahami output `shape` dan `dtype`
- Latihan: jika citra 256×256 RGB, berapa ukurannya dalam MB?
- Latihan: apa bedanya `image.shape` grayscale vs RGB?

---

### MODUL 2: SISTEM KOORDINAT CITRA

#### Yang HARUS dihafal
- Titik asal `(0,0)` = **pojok kiri atas** (BUKAN kiri bawah!)
- Sumbu X → arah kanan (kolom/width)
- Sumbu Y → arah bawah (baris/height)
- Titik terjauh = `(W-1, H-1)` BUKAN `(W, H)`
- Akses piksel: **`image[baris, kolom]` = `image[y, x]`** (baris dulu!)

#### Yang HARUS dipahami
- BEDA dengan koordinat Kartesius (matematika): Y terbalik!
- Di matplotlib/scikit-image, `x` adalah kolom (horizontal), `y` adalah baris (vertikal)
- Cropping: `image[y1:y2, x1:x2]` — urutan y dulu baru x
- Contoh: Coins 303×384 → titik kanan bawah = `(383, 302)` bukan `(302, 383)`

#### Cara belajar
- Gambar sendiri diagram sumbu X-Y citra digital vs Kartesius
- Kerjakan: dimana piksel `image[100, 200]`? (baris 100, kolom 200)
- Kerjakan: jika ingin piksel di baris 50 kolom 150, tulis `image[50, 150]`

---

### MODUL 3: FORMAT FILE & KOMPRESI

#### Yang HARUS dihafal — Tabel Perbandingan

| Format | Kompresi | Ukuran | Kualitas | Kegunaan |
|--------|----------|--------|----------|----------|
| **BMP** | Tidak terkompresi | Sangat besar | Sempurna (lossless) | Pengolahan presisi tinggi |
| **JPEG** | Lossy | Paling kecil | Berkurang (artefak) | Web, fotografi |
| **PNG** | Lossless | Sedang | Sempurna | Web, ilmiah |
| **TIFF** | Lossy ATAU Lossless | Besar | Sangat baik | Medis, percetakan |

#### Yang HARUS dipahami
- **Lossy** = kompresi yang MENGHAPUS data secara permanen
  - Contoh: JPEG — makin rendah quality, makin kecil file, makin banyak artefak
  - TIDAK bisa dikembalikan ke asli (irreversible)
- **Lossless** = kompresi yang TIDAK menghapus data
  - Contoh: PNG, BMP — setiap piksel tetap utuh
  - Bisa dikembalikan ke asli (reversible)
- Dampak quality pada JPEG:
  - Q=50 → ukuran sangat kecil, artefak jelas terlihat
  - Q=90 → ukuran sedang, mata sulit bedakan dengan asli
  - Q=95 → ukuran lebih besar, kualitas hampir sempurna

#### Kapan pakai apa?
- Analisis citra ilmiah/medis → BMP, TIFF, PNG (setiap piksel penting!)
- Web/media sosial → JPEG (hemat memori, kualitas cukup)
- Perlu transparansi → PNG

#### Cara belajar
- Hafalkan tabel perbandingan
- Pahami mengapa JPEG tidak cocok untuk analisis medis
- Latihan: jika disimpan sebagai JPEG Q=50 lalu dibuka dan disimpan lagi, apa yang terjadi? (degradasi kumulatif)

---

### MODUL 4: DETEKSI TEPI

#### Tabel Perbandingan Operator

| Operator | Ukuran Kernel | Karakteristik Utama |
|----------|--------------|---------------------|
| **Sobel** | 3×3 | Tepi halus & tebal, ada arah X dan Y |
| **Roberts** | 2×2 | Tepi paling tipis & tajam, sensitif noise |
| **Prewitt** | 3×3 | Mirip Sobel, sedikit lebih kasar |
| **Kirsch** | 8 arah kompas | Kontras tajam, deteksi multi-arah |
| **Canny** | Multi-step | Paling bersih & presisi, garis 1 piksel |

#### Poin penting untuk ujian
- Sobel punya 2 kernel: horizontal (`sobel_h`) dan vertikal (`sobel_v`)
  - `sobel_h` → deteksi garis **vertikal** (perubahan intensitas horizontal)
  - `sobel_v` → deteksi garis **horizontal** (perubahan intensitas vertikal)
- Canny = Gold Standard — hasil paling bersih karena ada noise suppression + non-max suppression
- Roberts = kernel terkecil (2×2) → paling cepat tapi paling sensitif terhadap noise
- Untuk citra berwarna: proses tiap kanal RGB terpisah, lalu gabungkan

#### Cara belajar
- Hafalkan perbedaan 5 operator di atas
- Pahami kenapa Canny dianggap terbaik (3 langkah kuncinya)
- Latihan: soal "operator mana yang paling cocok untuk foto dengan noise?"

---

### MODUL 5: PERBAIKAN CITRA DOMAIN SPASIAL

#### Transformasi Intensitas

| Transformasi | Formula | Efek |
|-------------|---------|------|
| Negatif | `s = L-1 - r` atau `s = 1 - r` (float) | Balik: gelap↔terang |
| Logaritmik | `s = c × log(1 + r)` | Perluas area gelap, mampat area terang |
| Gamma | `s = c × r^γ` | γ<1 → terang; γ>1 → gelap |

#### Perbandingan Peningkatan Kontras

| Metode | Cara Kerja | Bentuk Histogram Hasil |
|--------|-----------|----------------------|
| Contrast Stretching | Tarik histogram ke rentang penuh secara **linear** | Mirip asli, hanya diperlebar |
| Histogram Equalization | Ratakan distribusi secara **non-linear** | Datar/uniform |

#### Filter

| Filter | Cara Kerja | Noise S&P | Pelestarian Tepi |
|--------|-----------|-----------|-------------------|
| Mean (Rata-rata) | Rata-rata tetangga | Gagal (jadi bercak abu) | Blur/mengaburkan |
| Median | Nilai tengah tetangga | **Berhasil hapus sempurna** | **Tetap tajam** |

> ⚡ WAJIB TAHU: Untuk noise salt-and-pepper → SELALU pakai **Median Filter**!

#### Cara belajar
- Hafalkan efek gamma: γ<1=cerah, γ>1=gelap
- Pahami kenapa median lebih baik dari mean untuk noise impuls
- Latihan: jika citra terlalu gelap, gamma berapa yang dipakai? (γ<1)

---

### MODUL 6: SEGMENTASI CITRA ⭐ (PALING PENTING UNTUK ESSAY)

#### Metode-Metode Segmentasi

**A. Thresholding**
| Jenis | Prinsip | Kapan Terbaik |
|-------|---------|---------------|
| Manual | Tentukan T sendiri | Kontras tinggi, T sudah diketahui |
| Otsu | Minimasi varians dalam-kelas secara otomatis | Histogram bimodal |
| Yen | Metode global lain, kadang lebih baik | Kasus tertentu |
| Local/Adaptive | Hitung T per blok tetangga | **Cahaya tidak merata / dokumen** |

**B. Region-Based (Flood Fill)**
- Mulai dari seed point → isi area terhubung
- Parameter `tolerance` → semakin besar = semakin luas area
- Kelebihan: isolasi area spesifik
- Kelemahan: sensitif terhadap posisi seed & nilai tolerance
- Bisa "bocor" ke area tidak diinginkan jika tolerance terlalu besar

**C. K-Means Clustering**
- Kelompokkan piksel berdasarkan kemiripan warna/intensitas
- Parameter K = jumlah kluster/segment
- Gunakan ruang warna **Lab** (bukan RGB) → lebih sesuai persepsi manusia
- Kelebihan: bisa segmentasi multi-level (K>2)
- Kelemahan: **tidak mempertimbangkan posisi spasial** → muncul noise/bintik

**D. Watershed**
- Anggap gradien sebagai topografi → air mengisi dari marker
- Perlu: **elevation map** (dari Sobel) + **markers** (penanda latar & objek)
- Kelebihan: pisahkan objek bersentuhan paling presisi
- Kelemahan: tanpa marker tepat → **over-segmentation**
- Pipeline: Sobel → markers → watershed → mark_boundaries

#### Pemilihan Metode (SANGAT PENTING!)

| Kebutuhan | Metode Terbaik |
|-----------|----------------|
| Pisahkan objek & latar sederhana | Otsu |
| Dokumen dengan bayangan | Local Threshold |
| Pisahkan berdasarkan warna | K-Means |
| Pisahkan objek bersentuhan | Watershed |
| Isolasi area spesifik yang terhubung | Flood Fill |
| Citra medis/sel mikroskop | K-Means atau Watershed |

#### Cara belajar
- Buat peta pikiran: kapan pakai metode apa
- Pahami kelemahan setiap metode (ini sering jadi soal essay)
- Latih coding: threshold_otsu, flood, KMeans, watershed
- Hafalkan: Otsu gagal pada pencahayaan tidak merata → solusi: local threshold

---

## 📝 PREDIKSI SOAL PG (30 SOAL)

### Topik 1: Piksel & Representasi Data (~7 soal)

**1.** Piksel merupakan singkatan dari...  
a) Picture Element ✅  
b) Pixel Element  
c) Photo Element  
d) Picture Encode

**2.** Citra grayscale berukuran 512×512 disimpan dalam format NumPy. Berapa ukuran file dalam byte?  
a) 262.144 ✅ (512×512×1 byte)  
b) 786.432  
c) 524.288  
d) 131.072

**3.** Tipe data piksel pada citra 8-bit adalah...  
a) int8  
b) uint8 ✅  
c) float8  
d) int16

**4.** Rentang nilai piksel pada citra 8-bit grayscale adalah...  
a) -128 s.d. 127  
b) 0 s.d. 255 ✅  
c) 0 s.d. 512  
d) 0 s.d. 1

**5.** Pada model warna RGB, warna hitam direpresentasikan oleh...  
a) (255, 255, 255)  
b) (0, 0, 255)  
c) (0, 0, 0) ✅  
d) (255, 0, 255)

**6.** Apa perbedaan utama citra grayscale dan berwarna dalam representasi array?  
a) Grayscale 1D, RGB 2D  
b) Grayscale 2D, RGB 3D ✅  
c) Grayscale 3D, RGB 4D  
d) Keduanya 2D

**7.** Pada citra RGB berukuran 512×512, berapa total byte yang dibutuhkan?  
a) 262.144  
b) 512.000  
c) 786.432 ✅ (512×512×3)  
d) 1.048.576

### Topik 2: Sistem Koordinat (~3 soal)

**8.** Titik asal (0,0) pada sistem koordinat citra digital berada di...  
a) Pojok kiri bawah  
b) Pojok kanan atas  
c) Pojok kiri atas ✅  
d) Tengah gambar

**9.** Pada citra berukuran 512×384, piksel di pojok kanan bawah memiliki koordinat...  
a) (512, 384)  
b) (383, 511) ✅ (x=W-1=383, y=H-1=511)  
c) (511, 383)  
d) (384, 512)

**10.** Dalam Python NumPy, untuk mengakses piksel pada baris ke-50 dan kolom ke-100, penulisannya adalah...  
a) image[100, 50]  
b) image[50, 100] ✅  
c) image(x=50, y=100)  
d) image[100][50]

### Topik 3: Format File & Kompresi (~6 soal)

**11.** Format file yang TIDAK melakukan kompresi data disebut...  
a) Lossy  
b) Lossless  
c) Uncompressed ✅ (BMP adalah uncompressed)  
d) Compressed

**12.** Kompresi lossy memiliki karakteristik...  
a) Data piksel tetap utuh  
b) File bisa dikembalikan ke asli  
c) Terdapat kehilangan data yang permanen ✅  
d) Ukuran file lebih besar dari lossless

**13.** Format yang paling cocok untuk analisis citra medis yang membutuhkan akurasi piksel 100% adalah...  
a) JPEG  
b) BMP ✅ (atau TIFF/PNG)  
c) GIF  
d) JPEG2000

**14.** Apa yang terjadi jika citra disimpan sebagai JPEG dengan quality=50?  
a) Ukuran file sangat besar  
b) Tidak ada perubahan kualitas  
c) Muncul artefak kompresi dan detail berkurang ✅  
d) File menjadi format PNG

**15.** Format PNG menggunakan kompresi bertipe...  
a) Lossy  
b) Lossless ✅  
c) Tidak terkompresi  
d) Hybrid

**16.** Jika JPEG disimpan berulang kali (save-reload), kualitas citra akan...  
a) Tetap sama  
b) Semakin membaik  
c) Semakin menurun (degradasi kumulatif) ✅  
d) Berubah menjadi lossless

### Topik 4: Deteksi Tepi (~5 soal)

**17.** Operator deteksi tepi yang menggunakan kernel berukuran 2×2 adalah...  
a) Sobel  
b) Prewitt  
c) Roberts ✅  
d) Canny

**18.** Algoritma Canny menghasilkan garis tepi setebal...  
a) 2 piksel  
b) 1 piksel ✅  
c) 3 piksel  
d) Tergantung parameter

**19.** Filter `sobel_h` pada scikit-image mendeteksi...  
a) Tepi horizontal  
b) Tepi vertikal ✅ (gradien horizontal → sensitif terhadap garis vertikal)  
c) Tepi diagonal  
d) Semua arah

**20.** Operator yang paling sensitif terhadap noise adalah...  
a) Canny  
b) Sobel  
c) Prewitt  
d) Roberts ✅

**21.** Langkah yang TIDAK merupakan bagian dari algoritma Canny adalah...  
a) Smoothing dengan Gaussian  
b) Non-maximum suppression  
c) Konvolusi dengan kernel 5×5 untuk deteksi semua tepi sekaligus ✅  
d) Hysteresis thresholding

### Topik 5: Perbaikan Citra (~4 soal)

**22.** Filter yang paling efektif untuk menghilangkan noise salt-and-pepper adalah...  
a) Mean filter  
b) Gaussian filter  
c) Median filter ✅  
d) High-pass filter

**23.** Transformasi negatif pada citra grayscale 8-bit menggunakan formula...  
a) s = r  
b) s = 255 - r ✅  
c) s = r + 255  
d) s = r / 255

**24.** Jika parameter gamma (γ) kurang dari 1 pada transformasi gamma, maka citra akan menjadi...  
a) Lebih gelap  
b) Lebih terang ✅  
c) Tetap sama  
d) Terbalik

**25.** Perbedaan utama antara contrast stretching dan histogram equalization adalah...  
a) Stretching mempertahankan bentuk histogram asli ✅  
b) Equalization menghasilkan histogram yang sama dengan asli  
c) Stretching selalu menghasilkan histogram datar  
d) Equalization hanya bekerja pada citra berwarna

### Topik 6: Segmentasi Citra (~5 soal)

**26.** Metode thresholding Otsu bekerja dengan cara...  
a) Menentukan nilai ambang secara manual  
b) Meminimalkan varians dalam-kelas (intra-class variance) ✅  
c) Menghitung rata-rata tetangga setiap piksel  
d) Mengelompokkan piksel berdasarkan jarak Euclidean

**27.** Metode segmentasi yang paling sesuai untuk memisahkan objek yang saling bersentuhan adalah...  
a) Otsu thresholding  
b) K-Means  
c) Watershed ✅  
d) Flood fill

**28.** Pada algoritma Watershed, yang berfungsi sebagai "permukaan topografi" adalah...  
a) Citra asli  
b) Hasil thresholding  
c) Peta gradien (elevation map dari Sobel) ✅  
d) Label kluster

**29.** K-Means clustering pada citra TIDAK mempertimbangkan...  
a) Nilai intensitas piksel  
b) Warna piksel  
c) Posisi spasial piksel ✅  
d) Jarak antar piksel

**30.** Thresholding lokal/adaptive paling cocok digunakan untuk...  
a) Citra dengan pencahayaan merata  
b) Citra dengan histogram bimodal sempurna  
c) Citra dokumen dengan pencahayaan tidak merata ✅  
d) Citra dengan noise salt-and-pepper

---

## 📝 PREDIKSI SOAL ESSAY (3 SOAL)

### ESSAY 1: Perbandingan Format File & Kompresi (Topik 3)
**Prediksi soal**: *Jelaskan perbedaan antara kompresi lossy dan lossless. Berikan contoh masing-masing format dan kapan sebaiknya menggunakan masing-masing jenis kompresi. Apa yang terjadi jika citra JPEG disimpan berulang kali?*

**Kerangka jawaban**:
1. **Lossy**: Menghapus sebagian data yang dianggap tidak penting oleh algoritma kompresi. Contoh: JPEG. File kecil tapi kualitas menurun. Terjadi artefak (kotak-kotak halus). Tidak reversibel — sekali disimpan, data asli hilang.
2. **Lossless**: Menyimpan semua data piksel tanpa penghapusan. Contoh: PNG, BMP, TIFF. File lebih besar tapi kualitas 100% utuh. Reversibel — bisa dikembalikan ke asli.
3. **Kapan pakai**: Lossy (JPEG) → web, media sosial, fotografi umum. Lossless (PNG/BMP) → analisis ilmiah, citra medis, pengolahan citra yang memerlukan presisi piksel.
4. **Penyimpanan berulang JPEG**: Terjadi degradasi kumulatif — setiap kali disimpan ulang, kualitas semakin menurun karena data yang hilang tidak bisa dipulihkan.

---

### ESSAY 2: Perbandingan Metode Segmentasi (Topik 6)
**Prediksi soal**: *Bandingkan empat metode segmentasi citra: Otsu thresholding, Flood Fill, K-Means, dan Watershed. Untuk setiap metode, jelaskan prinsip kerja, kelebihan, kekurangan, dan berikan contoh kasus penggunaan yang tepat.*

**Kerangka jawaban**:
1. **Otsu Thresholding**:
   - Prinsip: Mencari nilai ambang T optimal secara otomatis dengan meminimalkan varians dalam-kelas (intra-class variance)
   - Kelebihan: Sederhana, cepat, otomatis (tidak perlu input manual)
   - Kekurangan: Hanya menghasilkan segmentasi biner, gagal jika pencahayaan tidak merata
   - Cocok untuk: Citra dengan kontras tinggi dan histogram bimodal (contoh: koin di latar belakang gelap)

2. **Flood Fill**:
   - Prinsip: Mulai dari seed point, "mengisi" area yang terhubung dan memiliki intensitas mirip (dalam batas tolerance)
   - Kelebihan: Efektif mengisolasi area spesifik yang seragam
   - Kekurangan: Sangat sensitif terhadap posisi seed dan nilai tolerance, bisa "bocor" ke area yang tidak diinginkan
   - Cocok untuk: Isolasi area tertentu yang seragam dan terhubung (contoh: langit pada foto)

3. **K-Means Clustering**:
   - Prinsip: Mengelompokkan piksel berdasarkan kemiripan warna/intensitas dalam ruang warna Lab ke dalam K kluster
   - Kelebihan: Segmentasi multi-level (K>2), bisa membedakan variasi intensitas
   - Kekurangan: Tidak mempertimbangkan posisi spasial → menghasilkan noise/bintik, perlu tentukan K manual
   - Cocok untuk: Color quantization, citra sel mikroskop, segmentasi berbasis warna

4. **Watershed**:
   - Prinsip: Menganggap gradien citra sebagai topografi, air mengalir dari marker dan bertemu di watershed lines
   - Kelebihan: Paling presisi dalam menentukan batas objek (boundaries), mampu memisahkan objek bersentuhan
   - Kekurangan: Rentan over-segmentation tanpa marker tepat, butuh elevation map (Sobel) & markers yang baik
   - Cocok untuk: Memisahkan objek-objek yang bersentuhan/berhimpitan (contoh: koin yang tumpang tindih)

---

### ESSAY 3: Studi Kasus / Perbandingan Teknik (Topik 5 atau 6)
**Prediksi soal alternatif A**: *Sebuah citra mengandung noise salt-and-pepper. Jelaskan mengapa filter median lebih unggul dibanding filter rata-rata (mean) untuk mengatasi jenis noise tersebut. Apa yang akan terjadi pada tepi objek jika digunakan masing-masing filter?*

**Kerangka jawaban**:
- Noise salt-and-pepper memiliki nilai ekstrem (0 atau 255 untuk uint8)
- **Mean filter**: Menghitung rata-rata tetangga → nilai ekstrem ikut dihitung → noise tidak hilang, hanya berubah jadi bercak abu-abu yang kabur. Tepi objek juga ikut ter-blur karena rata-rata mengaburkan transisi tajam.
- **Median filter**: Mengambil nilai tengah → nilai ekstrem (noise) diabaikan karena tidak akan menjadi median → noise benar-benar terhapus. Tepi tetap tajam karena median mempertahankan transisi intensitas, tidak mengaburkan batas objek.
- **Kesimpulan**: Median selalu lebih baik untuk noise impuls (S&P), baik untuk penghapusan noise maupun pelestarian tepi.

**Prediksi soal alternatif B**: *Jelaskan perbedaan sistem koordinat citra digital dengan koordinat Kartesius. Jika sebuah citra berukuran 400×300 piksel, tentukan koordinat piksel di: (a) pojok kiri atas, (b) pojok kanan bawah, (c) piksel pada baris ke-50 dan kolom ke-200. Tunjukkan cara mengaksesnya dalam Python.*

**Kerangka jawaban**:
- Koordinat Kartesius: origin (0,0) di kiri bawah, Y naik ke atas
- Koordinat Citra: origin (0,0) di **kiri atas**, Y naik ke **bawah**
- Ukuran 400×300 → Width=400, Height=300
  - (a) Pojok kiri atas: `(0, 0)` → akses `image[0, 0]`
  - (b) Pojok kanan bawah: `(399, 299)` atau `(W-1, H-1)` → akses `image[299, 399]`
  - (c) Baris 50, kolom 200: koordinat `(200, 50)` → akses `image[50, 200]`
- Dalam NumPy: `image[baris, kolom]` = `image[y, x]`

---

## ✅ CHECKLIST SEBELUM UJIAN

- [ ] Hafal rumus ukuran citra: H×W×kedalaman_bit
- [ ] Hafal bedanya shape grayscale `(H,W)` vs RGB `(H,W,3)`
- [ ] Pahami koordinat: (0,0) kiri atas, akses `image[y,x]`
- [ ] Hafal tabel format file (BMP, JPEG, PNG, TIFF)
- [ ] Bisa jelaskan lossy vs lossless + contoh
- [ ] Hafal 5 operator deteksi tepi + karakteristik masing-masing
- [ ] Pahami kenapa Canny dianggap terbaik
- [ ] Bisa jelaskan median > mean untuk noise S&P
- [ ] Hafal efek gamma: γ<1=terang, γ>1=gelap
- [ ] Hafal 4 metode segmentasi + kapan pakai yang mana
- [ ] Pahami kelemahan Otsu → solusi: local threshold
- [ ] Pahami kelemahan Watershed → solusi: marker tepat
- [ ] Pahami kelemahan K-Means → tidak spasial