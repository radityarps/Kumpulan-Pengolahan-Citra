# Paket Produksi Video Tutorial AI Virtual Mouse

## Fokus Revisi

- Demo ditampilkan di awal, bukan di akhir.
- Requirement dan cara menjalankan dijelaskan sebelum demo.
- Baseline dijelaskan dengan dua konteks:
  1. **Baseline asli**: `src/video version/AiVirtualMouseProject.py`, tempat kode masalah terlihat.
  2. **Baseline runtime**: `--condition baseline`, pembanding perilaku lewat runtime baru.
- Cara kerja sistem dijelaskan dari letak kode, bukan hanya konsep.
- Kesimpulan wajib menunjukkan bukti kenapa improved lebih baik dari baseline.

## Requirement Untuk Menjalankan

Sebelum rekaman, pastikan:

1. Python environment sudah tersedia.
2. Webcam aktif.
3. Lighting cukup dan satu tangan terlihat jelas.
4. Folder kerja berada di `AI Virtual Mouse/`.
5. Dependencies improved sudah terpasang di `.venv-improved`.
6. Model MediaPipe tersedia di `models/hand_landmarker.task`.
7. Terminal, editor, dan screen recorder sudah siap.

Teknologi yang digunakan:

- Python: bahasa program.
- OpenCV: membaca frame webcam dan menampilkan window kamera.
- MediaPipe: mendeteksi hand landmarks.
- NumPy: mapping koordinat kamera ke layar.
- AutoPy: menggerakkan mouse sistem operasi.

## Command Demo

Jalankan dari folder `AI Virtual Mouse/`.

```bash
source .venv-improved/Scripts/activate
PYTHONPATH=src python -m ai_virtual_mouse_experimental --download-model
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Jika memakai PowerShell Windows, gunakan pola ini:

```powershell
$env:PYTHONPATH='src'; .venv-improved\Scripts\python.exe -m ai_virtual_mouse_experimental --download-model
$env:PYTHONPATH='src'; .venv-improved\Scripts\python.exe -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Baseline pembanding:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition baseline --allow-real-mouse
```

Jika backend gagal:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --smoke-backend
```

## Timeline 8-10 Menit

| Waktu | Tampilan | Tujuan |
|---|---|---|
| 00:00-00:35 | Presenter + title | Opening: demo akan ditunjukkan di awal |
| 00:35-01:25 | README + terminal | Requirement dan cara menjalankan |
| 01:25-02:45 | Improved demo window | Demo move, click, pause, quit |
| 02:45-03:40 | Baseline context | Bedakan baseline asli dan baseline runtime |
| 03:40-05:00 | `AiVirtualMouseProject.py` | Tunjukkan letak kode bermasalah |
| 05:00-06:30 | `ARCHITECTURE.md` + code files | Cara kerja sistem dari webcam ke cursor |
| 06:30-08:00 | `gesture_engine.py` + `hand_control_pipeline.py` | Improved fix: stable pinch + debounce |
| 08:00-09:10 | Benchmark/result note | Bukti improved lebih baik |
| 09:10-10:00 | Presenter closing | Kesimpulan dan limitation |

## Script Narasi Lengkap

### 00:00-00:35 — Opening

Halo, saya Raditya. Pada video ini saya akan mendemonstrasikan dan menjelaskan program AI Virtual Mouse.

Program ini mengubah gesture tangan dari webcam menjadi kontrol cursor dan click pada komputer. Supaya penjelasannya langsung jelas, demo akan saya tunjukkan di awal. Setelah itu baru saya jelaskan requirement, versi baseline, letak kode yang bermasalah, dan bagaimana versi improved memperbaikinya.

Fokus video ini bukan instalasi dari nol, tetapi cara menjalankan program dan memahami cara kerja sistem dari kode.

### 00:35-01:25 — Requirement dan Cara Menjalankan

Sebelum program dijalankan, ada beberapa requirement. Kita membutuhkan Python environment, webcam yang aktif, lighting yang cukup, dan dependencies project yang sudah terpasang.

Untuk demo improved, environment yang dipakai adalah `.venv-improved`. Program juga membutuhkan model MediaPipe, yaitu `models/hand_landmarker.task`. Jika model belum ada, kita jalankan command download model.

Saya menjalankan semua command dari folder `AI Virtual Mouse/`. Pertama environment diaktifkan:

```bash
source .venv-improved/Scripts/activate
```

Lalu model dipastikan tersedia:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --download-model
```

Setelah itu demo improved dijalankan dengan command:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Flag `--allow-real-mouse` penting karena mode ini benar-benar mengontrol mouse sistem operasi. Jadi program meminta izin eksplisit sebelum menggerakkan cursor asli.

### 01:25-02:45 — Demo Improved di Awal

Sekarang saya tunjukkan demo improved.

Pertama, untuk menggerakkan cursor, saya mengangkat jari telunjuk saja. Gesture ini disebut move. Cursor mengikuti ujung jari telunjuk, tetapi pergerakannya dibuat lebih halus dengan smoothing.

Kedua, untuk click, saya mengangkat jari telunjuk dan jari tengah, lalu mendekatkan kedua ujung jari. Ini disebut stable pinch click. Satu pinch yang stabil menghasilkan satu left click.

Hal yang penting: jika pinch saya tahan, program tidak melakukan click berulang-ulang. Program menunggu pinch dilepas terlebih dahulu sebelum click berikutnya bisa terjadi.

Ketiga, untuk pause, saya tahan open palm sekitar 0,3 detik. Saat paused, gerakan tangan tidak menggerakkan cursor dan tidak melakukan click. Ini safety control agar user bisa menghentikan kontrol sementara.

Untuk keluar dari program, saya tekan `q` pada window kamera. Ada juga corner failsafe: jika cursor ditahan di tepi atau sudut layar sekitar 0,8 detik, runtime otomatis pause.

### 02:45-03:40 — Konteks Baseline

Sekarang saya jelaskan baseline, karena ini penting untuk memahami kenapa versi improved dibuat.

Di project ini ada dua bentuk baseline. Pertama adalah baseline asli dari tutorial, filenya ada di:

```text
src/video version/AiVirtualMouseProject.py
```

File ini menunjukkan ide dasar AI Virtual Mouse: webcam membaca tangan, landmark dideteksi, telunjuk untuk move, dan pinch telunjuk-jari tengah untuk click.

Kedua adalah baseline runtime di sistem eksperimen baru, yang bisa dijalankan dengan:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition baseline --allow-real-mouse
```

Baseline runtime berguna sebagai pembanding perilaku. Tetapi untuk melihat letak masalah kode, yang paling jelas adalah baseline asli di `AiVirtualMouseProject.py`.

### 03:40-05:00 — Letak Kode Bermasalah di Baseline

Sekarang saya buka file baseline asli:

```text
src/video version/AiVirtualMouseProject.py
```

Di file ini, loop utama dimulai dari `while True`. Setiap frame kamera dibaca dengan `cap.read()`, lalu program mencari landmark tangan.

Bagian move ada saat jari telunjuk naik dan jari tengah turun. Program mengambil koordinat ujung telunjuk, melakukan mapping dari frame kamera ke ukuran layar, melakukan smoothing, lalu memanggil:

```python
autopy.mouse.move(wScr - clocX, clocY)
```

Masalah utama ada di bagian click, sekitar baris 63 sampai 71:

```python
if fingers[1] == 1 and fingers[2] == 1:
    length, img, lineInfo = detector.findDistance(8, 12, img)
    if length < 40:
        autopy.mouse.click()
```

Kode ini berarti: kalau telunjuk dan jari tengah naik, lalu jarak landmark 8 dan 12 kurang dari 40 pixel, program langsung melakukan mouse click.

Masalahnya, kode ini ada di dalam loop frame kamera. Kamera bisa membaca banyak frame per detik. Jadi kalau pinch ditahan selama beberapa frame, kondisi `length < 40` tetap true berkali-kali, dan `autopy.mouse.click()` bisa terpanggil berkali-kali.

Dengan kata lain, baseline menganggap setiap frame yang memenuhi syarat sebagai click baru. Belum ada state untuk membedakan:

- pinch baru dimulai,
- pinch sedang ditahan,
- pinch sudah dilepas,
- dan kapan click boleh keluar lagi.

Inilah sumber repeated click atau false click pada baseline.

### 05:00-06:30 — Cara Kerja Sistem dari Kode

Sekarang kita lihat cara kerja sistem secara runtut.

Alur besarnya adalah:

```text
webcam frame -> hand tracker -> gesture engine -> hand control pipeline -> mouse action
```

Pada baseline asli, banyak proses masih digabung dalam satu script. Webcam, gesture rule, coordinate mapping, smoothing, dan mouse action berada di `AiVirtualMouseProject.py`.

Pada versi improved, tanggung jawab dipisahkan menjadi beberapa file:

- `hand_tracker.py`: membaca frame dan mendapatkan hand landmarks dari MediaPipe.
- `gesture_engine.py`: menentukan gesture, misalnya move, click, atau pause.
- `hand_control_pipeline.py`: mengubah gesture menjadi output runtime seperti `cursor_target` dan `click_fired`.
- `real_mouse_runtime.py`: menerapkan output pipeline ke mouse sistem operasi.

Jadi perbedaan pentingnya bukan hanya fitur lebih banyak, tetapi struktur program lebih jelas. Deteksi tangan, klasifikasi gesture, dan aksi mouse tidak dicampur dalam satu blok besar.

Untuk move, sistem membaca ujung jari telunjuk, memetakan koordinat kamera ke layar, lalu membuat target cursor. Untuk click, sistem tidak langsung click dari raw gesture. Sistem melewati pipeline dan debounce dulu.

### 06:30-08:00 — Improved Fix: Stable Pinch dan Debounce

Sekarang saya buka file:

```text
src/ai_virtual_mouse_experimental/gesture_engine.py
```

Di sini ada konfigurasi debounce:

```python
class ClickDebounceConfig:
    stable_frames_required: int = 2
    release_frames_required: int = 2
    cooldown_seconds: float = 0.35
```

Artinya, click tidak langsung keluar dari satu frame saja. Pinch harus stabil minimal beberapa frame, harus ada release sebelum click berikutnya, dan ada cooldown waktu.

Fungsi pentingnya adalah `update_click_debounce`, mulai sekitar baris 175. Di dalam fungsi ini, ketika raw click aktif, program menghitung `pressed_frames`. Lalu program mengecek tiga hal:

```python
next_state.armed
stable
cooldown_elapsed
```

Click baru benar-benar keluar hanya jika state masih armed, pinch sudah stable, dan cooldown sudah lewat. Jika click keluar, hasilnya:

```python
emit_click=True
```

lalu state dibuat tidak armed:

```python
armed=False
```

Agar bisa click lagi, raw click harus berhenti dulu. Bagian release menghitung `released_frames`, lalu state baru armed lagi setelah release cukup.

Di file:

```text
src/ai_virtual_mouse_experimental/hand_control_pipeline.py
```

output final pipeline punya field:

```python
click_fired: bool = False
```

Ini penting. Runtime tidak memakai raw gesture click secara langsung. Runtime menunggu `click_fired`. Jadi alurnya berubah dari baseline:

```text
pinch true -> autopy.mouse.click()
```

menjadi:

```text
pinch true -> debounce -> click_fired -> mouse click
```

Perubahan inilah yang membuat satu pinch yang ditahan tidak menjadi banyak click.

### 08:00-09:10 — Bukti Improved Lebih Baik dari Baseline

Sekarang bagian penting: apa buktinya improved lebih baik dari baseline?

Buktinya bukan sekadar karena kode terlihat lebih rapi. Bukti utamanya berasal dari perilaku click dan hasil benchmark.

Pada baseline, kode `if length < 40: autopy.mouse.click()` berada di dalam loop frame. Jadi satu pinch yang ditahan bisa menjadi banyak click. Itu secara langsung menjelaskan kenapa false click bisa tinggi.

Pada improved, click melewati stable pinch dan debounce. Program hanya mengeluarkan click saat kondisi sudah stable, masih armed, dan cooldown sudah lewat. Setelah click keluar, gesture harus dilepas sebelum click berikutnya.

Hasil benchmark mendukung penjelasan ini. Baseline dan improved sama-sama bisa mencapai 100% hit rate, artinya target tetap bisa diklik. Tetapi improved jauh mengurangi click yang tidak diinginkan:

- false clicks turun dari 192,8 menjadi 4,2.
- total clicks turun dari 212,8 menjadi 24,2.
- hit rate tetap 100% pada kedua kondisi.

Jadi improvement yang paling kuat bukan klaim bahwa program selalu lebih cepat, atau sudah menggantikan mouse fisik sepenuhnya. Klaim yang aman adalah: improved pipeline lebih baik karena mengurangi repeated click dan false click secara besar, sambil tetap mempertahankan keberhasilan klik target.

### 09:10-10:00 — Closing

Sebagai kesimpulan, AI Virtual Mouse bekerja dengan membaca frame webcam, mendeteksi hand landmarks memakai MediaPipe, mengenali gesture, lalu menerjemahkannya menjadi aksi cursor.

Baseline membuktikan konsep dasarnya berhasil: telunjuk untuk move, pinch untuk click. Tetapi baseline punya masalah karena click langsung dipanggil dari kondisi jarak jari pada setiap frame. Letak masalahnya ada di `src/video version/AiVirtualMouseProject.py`, terutama bagian `if length < 40:` lalu `autopy.mouse.click()`.

Versi improved memperbaiki masalah itu dengan memisahkan sistem menjadi hand tracker, gesture engine, pipeline, dan runtime. Click tidak lagi keluar dari raw gesture, tetapi dari `click_fired` setelah melewati stable pinch, debounce, release state, dan cooldown.

Bukti perbaikannya terlihat dari penurunan false clicks dari 192,8 menjadi 4,2, sementara hit rate tetap 100%. Jadi versi improved lebih baik bukan karena lebih kompleks saja, tetapi karena desain event click-nya lebih aman dan lebih terkontrol.

Sekian demo dan penjelasan program AI Virtual Mouse dari saya. Terima kasih.

## Shot Detail Kode yang Wajib Ditunjukkan

### 1. Baseline asli

File:

```text
src/video version/AiVirtualMouseProject.py
```

Sorot:

```python
if length < 40:
    autopy.mouse.click()
```

Penjelasan wajib:

- Kode berada di dalam `while True`.
- `while True` berjalan per frame kamera.
- Jika pinch ditahan, kondisi bisa true berkali-kali.
- Tidak ada debounce, cooldown, atau release state.

### 2. Improved gesture engine

File:

```text
src/ai_virtual_mouse_experimental/gesture_engine.py
```

Sorot:

```python
stable_frames_required: int = 2
release_frames_required: int = 2
cooldown_seconds: float = 0.35
```

Sorot juga:

```python
if next_state.armed and stable and cooldown_elapsed:
    ...
    emit_click=True
```

Penjelasan wajib:

- Click perlu stable.
- State harus armed.
- Cooldown harus lewat.
- Setelah click, state tidak armed sampai gesture dilepas.

### 3. Improved pipeline

File:

```text
src/ai_virtual_mouse_experimental/hand_control_pipeline.py
```

Sorot:

```python
click_fired: bool = False
```

Penjelasan wajib:

- Runtime memakai `click_fired`, bukan raw click.
- Ini batas antara gesture detection dan mouse action.

## Cue Editing

- Opening text: `AI Virtual Mouse — Demo, Baseline Problem, dan Improved Fix`.
- Saat requirement: tampilkan checklist ringkas.
- Saat command: zoom ke terminal.
- Saat demo gesture: beri label `Move`, `Stable Pinch Click`, `Pause`, `Quit`.
- Saat baseline code: highlight `while True`, `if length < 40`, dan `autopy.mouse.click()`.
- Saat improved code: highlight `stable_frames_required`, `armed`, `cooldown_elapsed`, `emit_click`, dan `click_fired`.
- Saat bukti: tampilkan angka `192.8 -> 4.2 false clicks` dan `100% hit rate`.

## Checklist Rekaman Final

1. Demo improved berhasil sebelum recording.
2. Baseline file sudah dibuka di editor.
3. `gesture_engine.py` sudah dibuka di editor.
4. `hand_control_pipeline.py` sudah dibuka di editor.
5. Terminal berada di folder `AI Virtual Mouse/`.
6. Webcam overlay presenter hanya opening dan closing.
7. Tidak ada file penting terbuka saat real mouse demo.
8. Siap tekan `q` untuk keluar.

---

# Revisi Tambahan — Penjelasan Kode dan Benchmark Lebih Dalam

Bagian ini boleh dipakai sebagai pengganti bagian `05:00-09:10` pada script lama. Karena durasi tidak dibatasi, bagian ini dibuat lebih lengkap.

## Timeline Baru Tanpa Batas Durasi

| Urutan | Tampilan | Fokus |
|---|---|---|
| 1 | Opening + terminal | Tujuan video, requirement, command run |
| 2 | Demo improved | Tunjukkan program bekerja dari awal |
| 3 | `AiVirtualMouseProject.py` | Import, konfigurasi, webcam open, loop frame |
| 4 | `HandTrackingModule.py` | MediaPipe process, landmarks, fingersUp, distance |
| 5 | `AiVirtualMouseProject.py` | Move flow: landmark -> mapping -> smoothing -> `autopy.mouse.move` |
| 6 | `AiVirtualMouseProject.py` | Click problem: `length < 40` -> `autopy.mouse.click()` per frame |
| 7 | Improved files | `gesture_engine.py`, `hand_control_pipeline.py`, `real_mouse_runtime.py` |
| 8 | Benchmark files | `benchmark_shell.py`, `benchmark_grid.py`, `benchmark_report.py` |
| 9 | Conclusion | Bukti improved lebih baik dari baseline |

## Narasi Detail — Cara Kerja Baseline dari Kode

Sekarang saya jelaskan alur program dari kode baseline asli. File yang dibuka adalah:

```text
src/video version/AiVirtualMouseProject.py
```

### 1. Import Library

Di bagian paling atas ada beberapa import:

```python
import time
import autopy
import cv2
import HandTrackingModule as htm
import numpy as np
```

Fungsi masing-masing import:

- `time` dipakai untuk menghitung FPS. Program mencatat waktu frame sebelumnya dan frame sekarang, lalu menghitung frame rate.
- `autopy` dipakai untuk mengontrol mouse sistem operasi. Dari library ini program mengambil ukuran layar dengan `autopy.screen.size()`, menggerakkan cursor dengan `autopy.mouse.move()`, dan melakukan click dengan `autopy.mouse.click()`.
- `cv2` adalah OpenCV. Di program ini OpenCV dipakai untuk membuka webcam, membaca frame kamera, menggambar overlay seperti rectangle dan circle, menampilkan window kamera, dan membaca tombol keyboard seperti `q`.
- `HandTrackingModule as htm` adalah modul buatan project sendiri. Modul ini membungkus MediaPipe Hands supaya script utama tidak perlu langsung menulis semua kode MediaPipe.
- `numpy as np` dipakai terutama untuk `np.interp`, yaitu mengubah koordinat dari ruang kamera menjadi koordinat layar.

Jadi sejak awal, pembagian tugasnya sudah terlihat: OpenCV untuk input visual, MediaPipe lewat `HandTrackingModule` untuk deteksi tangan, NumPy untuk transformasi koordinat, dan AutoPy untuk output ke mouse.

### 2. Konfigurasi Awal

Setelah import, ada konfigurasi:

```python
wCam, hCam = 640, 480
frameR = 100
smoothening = 7
```

`wCam` dan `hCam` menentukan resolusi webcam, yaitu 640 x 480. `frameR` adalah frame reduction, yaitu margin area kerja di dalam frame kamera. Cursor hanya dipetakan dari area dalam rectangle, bukan seluruh frame, supaya tangan tidak perlu sampai benar-benar ke tepi kamera. `smoothening` mengatur seberapa halus pergerakan cursor.

Lalu ada variabel posisi:

```python
plocX, plocY = 0, 0
clocX, clocY = 0, 0
```

`ploc` berarti previous location, posisi cursor sebelumnya. `cloc` berarti current location, posisi cursor saat ini setelah smoothing. Dua nilai ini dipakai supaya cursor tidak langsung melompat ke titik baru, tetapi bergerak bertahap.

### 3. Webcam Dibuka

Bagian ini membuka kamera:

```python
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
```

`cv2.VideoCapture(0)` berarti program membuka kamera index 0, biasanya webcam utama laptop. Setelah itu `cap.set(3, wCam)` mengatur lebar frame, dan `cap.set(4, hCam)` mengatur tinggi frame.

Kalau kamera tidak terbuka atau frame tidak bisa dibaca, nanti `cap.read()` akan gagal dan program berhenti dengan pesan error.

### 4. Hand Detector dan Ukuran Layar

Setelah kamera dibuka, program membuat detector:

```python
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
```

`handDetector(maxHands=1)` berarti program hanya fokus pada satu tangan. Ini penting karena kalau dua tangan dibaca sekaligus, gesture bisa ambigu.

`autopy.screen.size()` mengambil ukuran layar komputer. Misalnya layar 1920 x 1080. Nilai ini dibutuhkan karena koordinat kamera 640 x 480 harus diubah menjadi koordinat layar yang ukurannya berbeda.

### 5. Loop Utama per Frame

Program berjalan di dalam:

```python
while True:
```

Artinya semua proses di dalamnya terjadi berulang-ulang selama program belum dihentikan. Setiap putaran loop mewakili satu frame dari webcam.

Frame dibaca dengan:

```python
success, img = cap.read()
```

Kalau `success` bernilai `True`, frame berhasil dibaca dan disimpan ke variabel `img`. Kalau gagal, program memberi pesan bahwa frame kamera tidak bisa dibaca, lalu `break`.

Setelah frame dibaca, frame dikirim ke detector:

```python
img = detector.findHands(img)
lmList, bbox = detector.findPosition(img)
```

`findHands(img)` menjalankan proses deteksi tangan dan menggambar landmark di gambar. `findPosition(img)` mengambil daftar posisi landmark dalam bentuk pixel. Hasilnya disimpan di `lmList`.

### 6. Cara `HandTrackingModule.py` Bekerja

Sekarang kita lihat file:

```text
src/video version/HandTrackingModule.py
```

Di dalam class `handDetector`, MediaPipe Hands dibuat lewat:

```python
self.mpHands = import_module("mediapipe.python.solutions.hands")
self.hands = self.mpHands.Hands(...)
```

Kemudian pada fungsi `findHands`, OpenCV frame diubah dari BGR ke RGB:

```python
imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
self.results = self.hands.process(imgRGB)
```

Perubahan BGR ke RGB perlu karena OpenCV membaca warna sebagai BGR, sedangkan MediaPipe memproses gambar RGB.

Jika tangan terdeteksi, MediaPipe menghasilkan `multi_hand_landmarks`. Landmark itu digambar ke frame dengan `draw_landmarks`.

Pada fungsi `findPosition`, landmark yang awalnya bernilai normalisasi 0 sampai 1 diubah menjadi koordinat pixel:

```python
cx, cy = int(lm.x * w), int(lm.y * h)
self.lmList.append([id, cx, cy])
```

Jadi `lmList` berisi daftar seperti:

```text
[id landmark, x pixel, y pixel]
```

Contoh penting:

- landmark 8 = ujung jari telunjuk.
- landmark 12 = ujung jari tengah.

Fungsi `fingersUp()` menentukan jari mana yang sedang naik. Untuk jari selain ibu jari, logikanya membandingkan posisi y ujung jari dengan posisi y sendi di bawahnya. Jika ujung jari lebih tinggi, jari dianggap naik.

Fungsi `findDistance(8, 12, img)` menghitung jarak antara landmark 8 dan 12 menggunakan:

```python
length = math.hypot(x2 - x1, y2 - y1)
```

Inilah nilai jarak yang dipakai untuk menentukan apakah telunjuk dan jari tengah sedang pinch.

## Narasi Detail — Alur Move dari Kode

Setelah landmark didapat, script utama mengecek apakah ada tangan:

```python
if len(lmList) != 0:
```

Jika ada tangan, program mengambil ujung telunjuk dan jari tengah:

```python
x1, y1 = lmList[8][1:]
x2, y2 = lmList[12][1:]
```

Lalu program mengecek jari mana yang naik:

```python
fingers = detector.fingersUp()
```

Untuk move mode, kondisinya:

```python
if fingers[1] == 1 and fingers[2] == 0:
```

Artinya jari telunjuk naik dan jari tengah turun. Jika kondisi ini terpenuhi, koordinat ujung telunjuk diubah dari koordinat kamera ke koordinat layar:

```python
x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
```

Penjelasannya:

- `x1, y1` adalah posisi telunjuk pada frame kamera.
- `(frameR, wCam - frameR)` adalah batas area aktif kamera.
- `(0, wScr)` adalah lebar layar.
- `np.interp` memetakan nilai dari range kamera ke range layar.

Setelah mapping, program melakukan smoothing:

```python
clocX = plocX + (x3 - plocX) / smoothening
clocY = plocY + (y3 - plocY) / smoothening
```

Ini berarti posisi cursor baru tidak langsung sama dengan target `x3, y3`, tetapi bergerak sebagian dari posisi lama menuju target. Semakin besar `smoothening`, gerakan makin halus tetapi lebih lambat.

Cursor akhirnya digerakkan dengan:

```python
autopy.mouse.move(wScr - clocX, clocY)
```

`wScr - clocX` dipakai untuk mirror horizontal. Tanpa mirror, gerak
an tangan kanan bisa terasa terbalik di layar. Setelah cursor digerakkan, posisi lama diperbarui dengan `plocX, plocY = clocX, clocY`.

## Narasi Detail — Alur Click dan Masalah Baseline

Untuk click mode, baseline memakai kondisi:

```python
if fingers[1] == 1 and fingers[2] == 1:
```

Artinya telunjuk dan jari tengah sama-sama naik. Lalu program menghitung jarak landmark 8 dan 12:

```python
length, img, lineInfo = detector.findDistance(8, 12, img)
```

Jika jaraknya kurang dari 40 pixel, program langsung click:

```python
if length < 40:
    autopy.mouse.click()
```

Masalahnya bukan threshold 40 saja. Masalahnya: click langsung dipanggil dari kondisi frame. Selama pinch masih terbaca dan loop terus berjalan, `autopy.mouse.click()` bisa dipanggil berkali-kali.

Contoh:

```text
Frame 1: length = 35 -> click
Frame 2: length = 34 -> click
Frame 3: length = 33 -> click
Frame 4: length = 36 -> click
```

Padahal user hanya menahan satu gesture pinch. Ini sumber repeated click dan false click baseline.

## Narasi Detail — Cara Kerja Improved dari Kode

Pada improved version, sistem dipisah:

- `hand_tracker.py`: deteksi tangan dan landmarks, bukan langsung mouse action.
- `gesture_engine.py`: menentukan gesture: pause, move, click, idle.
- `hand_control_pipeline.py`: menggabungkan gesture, mapping, smoothing, debounce menjadi output `HandControlFrame`.
- `real_mouse_runtime.py`: menerapkan output pipeline ke mouse sistem operasi.

Di `gesture_engine.py`, pinch dicek dengan ide yang sama: jarak ujung jari dibanding threshold.

```python
hand.pinch_distance_px is not None
and hand.pinch_distance_px < config.click_threshold_px
```

Bedanya, improved tidak langsung mengirim click. Gesture pinch masuk ke `update_click_debounce`.

Fungsi `update_click_debounce` menerima `raw_click_active`, lalu menghasilkan `emit_click`. Saat raw click aktif, program menambah `pressed_frames`, lalu mengecek:

- `stable`: pinch sudah aktif cukup frame.
- `cooldown_elapsed`: jeda dari click terakhir sudah cukup.
- `armed`: sistem siap mengeluarkan click baru.

Click hanya keluar jika:

```python
next_state.armed and stable and cooldown_elapsed
```

Setelah click keluar, state menjadi `armed=False`. Artinya sistem tidak boleh click lagi sampai pinch dilepas cukup lama. Saat raw click tidak aktif, program menambah `released_frames`. Jika release cukup, state kembali armed.

Jadi improved mengubah click dari:

```text
kondisi frame -> langsung click
```

menjadi:

```text
kondisi frame -> state machine -> click jika valid
```

Di `hand_control_pipeline.py`, output pentingnya:

```python
cursor_target
click_fired
paused
```

Runtime memakai `click_fired`, bukan raw click. Ini batas penting antara gesture detection dan mouse action.

## Narasi Detail — Cara Benchmark Bekerja

Sekarang benchmark. Benchmark dipakai supaya baseline dan improved tidak dibandingkan hanya dari perasaan, tetapi dari tugas point-and-click yang sama.

### 1. Benchmark Aman: Simulated Cursor

File utama:

```text
src/ai_virtual_mouse_experimental/benchmark_shell.py
```

Di benchmark ada `SimulatedCursor`. Ini cursor buatan di window Pygame, bukan cursor sistem operasi. Jadi benchmark tidak menggerakkan mouse asli.

Tujuannya: input tangan tetap diuji, tetapi efek click hanya dicatat di window benchmark. Ini aman untuk eksperimen.

### 2. Target Benchmark

File:

```text
src/ai_virtual_mouse_experimental/benchmark_grid.py
```

Benchmark membuat target dengan `generate_grid_targets(settings)`. Target punya:

- index.
- posisi x dan y.
- radius.

Urutan target diacak dengan `random_seed`, sehingga baseline dan improved bisa diberi target yang sama. Ini membuat perbandingan lebih adil.

### 3. Satu Target = Satu Trial

Benchmark menyimpan target aktif. Saat target mulai, waktu start dicatat. User menggerakkan simulated cursor ke target, lalu melakukan click.

Saat click terjadi, benchmark memanggil `register_click`.

### 4. Hit dan False Click

Click dianggap hit jika jarak posisi click ke pusat target masih di dalam radius:

```python
hit = distance(click_x, click_y, target.x, target.y) <= target.radius
```

Jika hit, trial selesai dan `completion_time_s` dicatat.

Jika click di luar target, itu false click. Target tidak berubah, dan `false_clicks_current_trial` bertambah.

Jadi benchmark bisa menangkap masalah baseline: jika pinch ditahan dan click keluar berkali-kali sebelum cursor tepat di target, semua click di luar target dihitung false click.

### 5. Hand Input Masuk Lewat Pipeline

Di `benchmark_shell.py`, fungsi `apply_hand_frame_to_benchmark` menghubungkan pipeline ke benchmark.

Jika pipeline memberi `cursor_target`, simulated cursor dipindahkan:

```python
state = set_simulated_cursor(state, mirrored_x, hand_frame.cursor_target.y)
```

Jika pipeline memberi `click_fired`, benchmark mencatat click:

```python
benchmark = register_click(benchmark, state.cursor.x, state.cursor.y, now_s)
```

Ini penting: benchmark improved memakai output yang sama dengan runtime, yaitu `click_fired`. Jadi debounce benar-benar memengaruhi jumlah click yang masuk ke data.

### 6. Report dan Metrics

File:

```text
src/ai_virtual_mouse_experimental/benchmark_report.py
```

Fungsi `compute_metrics` membaca trial rows dan metadata. Metrics penting:

- `hit_rate`: berapa target berhasil diklik.
- `false_clicks`: jumlah click di luar target sebelum hit.
- `click_count`: hit + false clicks.
- `mean_completion_time_s`: rata-rata waktu selesai target.
- `median_completion_time_s`: median waktu selesai.
- `jitter_estimate_px`: jarak click dari pusat target.

Bagian hitung false click:

```python
false_clicks = sum(int(float(row.get("false_clicks_before_hit") or 0)) for row in rows)
click_count = hit_count + false_clicks
hit_rate = hit_count / expected_trials
```

Jadi angka hasil bukan asumsi. Angka berasal dari click event yang dicatat selama benchmark.

### 7. Cara Membandingkan

Benchmark dijalankan untuk dua condition:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition improved
```

Lalu session dibandingkan:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --compare-sessions outputs/sessions/session-a outputs/sessions/session-b
```

Karena tugasnya sama, perbedaan false clicks dan total clicks bisa dipakai sebagai bukti perbedaan perilaku baseline vs improved.

## Kesimpulan Versi Detail

Dari kode baseline, sumber masalahnya jelas: `autopy.mouse.click()` dipanggil langsung di dalam loop frame ketika `length < 40`. Karena loop berjalan berkali-kali per detik, satu pinch yang ditahan bisa menjadi banyak click.

Dari kode improved, click tidak langsung keluar. Gesture masuk ke gesture engine dan pipeline, lalu melewati debounce. Click baru keluar sebagai `click_fired` jika stable, armed, dan cooldown sudah lewat. Setelah itu gesture harus release sebelum click berikutnya.

Dari benchmark, perbandingan dilakukan dengan tugas point-and-click yang sama. Click di dalam radius target dihitung hit. Click di luar target dihitung false click. Completion time juga dicatat.

Hasilnya:

- baseline dan improved sama-sama mencapai 100% hit rate.
- false clicks turun dari 192,8 menjadi 4,2.
- total clicks turun dari 212,8 menjadi 24,2.

Jadi improved lebih baik karena mengurangi click yang tidak disengaja secara besar, bukan hanya karena kode lebih panjang atau memakai backend baru. Perbaikan utamanya ada pada desain event click: dari frame-based click menjadi intention-based click dengan state, release, dan cooldown.

---

# Revisi Tambahan — Peta Kode per Alur Sistem

Tidak ada pertanyaan. Bagian ini menjawab langsung: kode mana yang menjalankan setiap alur, fungsi apa yang dipanggil, dan logic apa yang terjadi.

## Peta Alur Besar Improved Runtime

Gunakan urutan ini saat menjelaskan kode:

```text
run_real_mouse_runtime()
    -> cv2.VideoCapture(...)
    -> cap.read()
    -> pipeline.process_frame(image)
        -> HandTracker.track(image)
        -> hand_input_from_tracking(...)
        -> classify_simple_real_mouse_gesture(...)
        -> map_point_to_output(...)
        -> apply_smoothing(...)
        -> update_click_debounce(...)
        -> HandControlFrame(...)
    -> mouse.move(...)
    -> mouse.click()
    -> cv2.imshow(...)
    -> cv2.waitKey(...)
```

Kalimat narasi:

> Kalau diringkas, file `real_mouse_runtime.py` adalah loop utama. File ini membuka webcam, membaca frame, mengirim frame ke pipeline, lalu menerapkan hasil pipeline ke mouse. Pipeline sendiri memanggil hand tracker, gesture engine, mapping, smoothing, debounce, lalu mengembalikan `HandControlFrame`.

## 1. Kode untuk Membuka Webcam

File:

```text
src/ai_virtual_mouse_experimental/real_mouse_runtime.py
```

Kode:

```python
def run_real_mouse_runtime(config: ExperimentalConfig, plan: RuntimePlan) -> int:
    cv2 = import_module("cv2")
    mouse = _create_mouse_controller()
    ...
    cap = cv2.VideoCapture(config.backend.camera_index)
    cap.set(3, config.backend.camera_width)
    cap.set(4, config.backend.camera_height)
```

Fungsi kode:

- `import_module("cv2")`: memuat OpenCV.
- `_create_mouse_controller()`: menyiapkan backend mouse, biasanya AutoPy.
- `cv2.VideoCapture(...)`: membuka webcam.
- `cap.set(3, ...)`: mengatur lebar kamera.
- `cap.set(4, ...)`: mengatur tinggi kamera.

Kalimat narasi:

> Webcam dibuka di `real_mouse_runtime.py`, bukan di gesture engine. Jadi tanggung jawab file ini adalah runtime loop: membuka kamera, membaca frame, dan menerapkan output ke mouse.

## 2. Kode untuk Membaca Frame Webcam

File:

```text
src/ai_virtual_mouse_experimental/real_mouse_runtime.py
```

Kode:

```python
while True:
    success, image = cap.read()
    if not success:
        print("Camera frame could not be read.")
        break

    frame_result: HandControlFrame = pipeline.process_frame(image)
```

Fungsi kode:

- `while True`: loop berjalan terus selama program aktif.
- `cap.read()`: mengambil satu frame dari webcam.
- `success`: status apakah frame berhasil dibaca.
- `image`: frame kamera yang akan diproses.
- `pipeline.process_frame(image)`: frame dikirim ke pipeline untuk dianalisis.

Kalimat narasi:

> Setiap putaran loop membaca satu frame kamera. Frame ini belum berarti apa-apa sampai dikirim ke `pipeline.process_frame(image)`. Di situlah gambar mulai diubah menjadi data gesture dan aksi mouse.

## 3. Kode untuk Hand Tracker

File:

```text
src/ai_virtual_mouse_experimental/hand_tracker.py
```

Kode struktur:

```python
@dataclass(frozen=True)
class HandTrackingResult:
    landmarks: list[Point] | None = None
    fingers_up: list[int] | None = None
    pinch_distance_px: float | None = None
    index_middle_vertical_delta_px: float | None = None
    success: bool = False
    backend_used: str = "unknown"
    fallback_reason: str | None = None
```

Fungsi kode:

`HandTrackingResult` adalah output hand tracker. Isinya:

- `landmarks`: titik-titik tangan hasil deteksi.
- `fingers_up`: status jari naik/turun.
- `pinch_distance_px`: jarak telunjuk dan jari tengah.
- `index_middle_vertical_delta_px`: selisih vertikal telunjuk dan jari tengah.
- `success`: apakah tangan berhasil dideteksi.
- `backend_used`: backend MediaPipe yang dipakai.

Kode backend:

```python
class HandTracker:
    """Unified hand tracker: Tasks primary, Solutions fallback."""

    def _setup_backend(self) -> None:
        if self.prefer_tasks:
            try:
                self._setup_tasks_backend()
                self._backend_used = "mediapipe_tasks"
                return
            except Exception as exc:
                self._fallback_reason = str(exc)
                ...
                self._setup_solutions_backend()
                self._backend_used = "mediapipe_solutions"
                return
        self._setup_solutions_backend()
        self._backend_used = "mediapipe_solutions"
```

Fungsi kode:

- Jika `prefer_tasks=True`, sistem mencoba MediaPipe Tasks dulu.
- Jika gagal, sistem fallback ke MediaPipe Solutions.
- Backend yang dipakai dicatat di `backend_used`.

Kalimat narasi:

> Hand tracker tidak menggerakkan mouse. Tugasnya hanya mengubah frame gambar menjadi data tangan: landmark, jari mana yang naik, dan jarak pinch. Data inilah yang nanti dikirim ke gesture engine.

## 4. Kode untuk Mengubah Tracking Result menjadi Gesture Input

File:

```text
src/ai_virtual_mouse_experimental/hand_control_pipeline.py
```

Kode:

```python
def hand_input_from_tracking(
    result: HandTrackingResult, config: GestureEngineConfig
) -> GestureInput:
    fingers = result.fingers_up or []
    if len(fingers) < 5:
        return GestureInput()
    return GestureInput(
        thumb=bool(fingers[0]),
        index=bool(fingers[1]),
        middle=bool(fingers[2]),
        ring=bool(fingers[3]),
        pinky=bool(fingers[4]),
        pinch_distance_px=result.pinch_distance_px,
        pinch_duration_s=0.0,
        index_middle_vertical_delta_px=result.index_middle_vertical_delta_px or 0.0,
    )
```

Fungsi kode:

- `HandTrackingResult` masih berupa data tracking.
- `GestureInput` adalah data yang siap dipakai gesture engine.
- List `fingers_up` diubah menjadi boolean: `thumb`, `index`, `middle`, `ring`, `pinky`.
- `pinch_distance_px` diteruskan untuk click detection.

Kalimat narasi:

> Bagian ini adalah jembatan antara hand tracker dan gesture engine. Tracker memberi data mentah, lalu pipeline mengubahnya menjadi format gesture: apakah index naik, middle naik, dan berapa jarak pinch.

## 5. Kode Gesture Engine

File:

```text
src/ai_virtual_mouse_experimental/gesture_engine.py
```

Kode input-output:

```python
@dataclass(frozen=True)
class GestureInput:
    thumb: bool = False
    index: bool = False
    middle: bool = False
    ring: bool = False
    pinky: bool = False
    pinch_distance_px: float | None = None
    pinch_duration_s: float = 0.0
    index_middle_vertical_delta_px: float = 0.0
```

```python
@dataclass(frozen=True)
class GestureResult:
    name: GestureName
    reason: str
    cursor_enabled: bool = False
    click: bool = False
    paused: bool = False
    feedback_label: str = "Idle"
```

Fungsi kode:

- `GestureInput`: kondisi tangan.
- `GestureResult`: arti gesture.
- Gesture engine tidak menggerakkan mouse. Ia hanya memberi keputusan: move, click, pause, atau idle.

Kode simple real mouse profile:

```python
def classify_simple_real_mouse_gesture(
    hand: GestureInput,
    config: GestureEngineConfig | None = None,
) -> GestureResult:
    cfg = config or GestureEngineConfig()

    if is_open_palm(hand):
        return _pause_result()

    if hand.index and hand.middle and not hand.ring and not hand.pinky:
        if is_pinching(hand, cfg):
            return _click_result("index_middle_stable_pinch")
        return GestureResult(name="idle", reason="index_middle_without_pinch")

    if hand.index and not hand.middle and not hand.ring and not hand.pinky:
        return _move_result()

    return GestureResult(name="idle", reason="no_supported_real_mouse_gesture")
```

Logic:

- Open palm → pause.
- Index + middle naik, ring + pinky turun, dan pinch aktif → click.
- Index saja naik → move.
- Selain itu → idle.

Kode pinch:

```python
def is_pinching(hand: GestureInput, config: GestureEngineConfig) -> bool:
    return (
        hand.pinch_distance_px is not None
        and hand.pinch_distance_px < config.click_threshold_px
    )
```

Logic:

- Pinch valid jika jarak telunjuk dan jari tengah ada.
- Jarak itu harus lebih kecil dari `click_threshold_px`.

Kalimat narasi:

> Gesture engine adalah tempat aturan gesture ditulis. Di sini program memutuskan
: tangan ini berarti move, click, pause, atau idle. Tapi hasilnya masih berupa keputusan, belum mouse action.

## 6. Kode Debounce Click

File:

```text
src/ai_virtual_mouse_experimental/gesture_engine.py
```

Kode konfigurasi:

```python
@dataclass(frozen=True)
class ClickDebounceConfig:
    stable_frames_required: int = 2
    release_frames_required: int = 2
    cooldown_seconds: float = 0.35
```

Kode state:

```python
@dataclass(frozen=True)
class ClickDebounceState:
    pressed_frames: int = 0
    released_frames: int = 0
    armed: bool = True
    last_click_time_s: float = -9999.0
```

Logic inti:

```python
cooldown_elapsed = now_s - state.last_click_time_s >= cfg.cooldown_seconds
stable = next_state.pressed_frames >= cfg.stable_frames_required
if next_state.armed and stable and cooldown_elapsed:
    return ClickDebounceResult(..., emit_click=True, reason="stable_click_emitted")
```

Fungsi kode:

- `pressed_frames`: menghitung berapa frame pinch aktif.
- `stable`: true jika pinch cukup stabil.
- `cooldown_elapsed`: true jika jeda click terakhir cukup.
- `armed`: true jika sistem siap click.
- `emit_click=True`: tanda click final boleh dikeluarkan.

Kode release:

```python
released_frames = state.released_frames + 1
armed = state.armed or released_frames >= cfg.release_frames_required
```

Logic:

- Jika pinch dilepas, `released_frames` naik.
- Setelah release cukup, sistem kembali `armed`.
- Ini mencegah satu pinch tahan menghasilkan banyak click.

## 7. Kode Hand Control Pipeline

File:

```text
src/ai_virtual_mouse_experimental/hand_control_pipeline.py
```

Output per frame:

```python
@dataclass(frozen=True)
class HandControlFrame:
    cursor_target: Point | None = None
    click_fired: bool = False
    paused: bool = False
    gesture_name: str = "idle"
    feedback_label: str = "Idle"
    backend_used: str = "unknown"
    fps: float = 0.0
    safety_triggered: bool = False
    hand_detected: bool = False
    landmarks_image: np.ndarray | None = None
```

Fungsi kode:

- `cursor_target`: posisi cursor hasil mapping.
- `click_fired`: click final setelah debounce.
- `paused`: apakah runtime sedang pause.
- `gesture_name`: nama gesture.
- `landmarks_image`: frame kamera dengan overlay landmark.

Kode import penting:

```python
from .cursor_mapping import apply_smoothing, map_point_to_output
from .gesture_engine import classify_simple_real_mouse_gesture, update_click_debounce
from .hand_tracker import HandTracker, HandTrackingResult
```

Logic pipeline:

- `HandTracker` membaca tangan.
- `hand_input_from_tracking` membuat `GestureInput`.
- `classify_simple_real_mouse_gesture` menentukan gesture.
- `map_point_to_output` mapping koordinat kamera ke layar.
- `apply_smoothing` menghaluskan cursor.
- `update_click_debounce` menentukan click final.
- Output akhir: `HandControlFrame`.

Kalimat narasi:

> Pipeline adalah pusat penggabungan. Ia menerima image dari runtime, memanggil hand tracker, mengubah hasil tracking menjadi gesture input, memanggil gesture engine, menjalankan debounce, menghitung cursor target, lalu mengembalikan `HandControlFrame`.

## 8. Kode Mouse Action

File:

```text
src/ai_virtual_mouse_experimental/real_mouse_runtime.py
```

Kode controller:

```python
def _create_mouse_controller() -> MouseController:
    try:
        autopy = import_module("autopy")
        width, height = autopy.screen.size()
        return MouseController(
            width=int(width),
            height=int(height),
            backend="autopy",
            move=autopy.mouse.move,
            click=autopy.mouse.click,
        )
    except (ImportError, ModuleNotFoundError):
        pyautogui = import_module("pyautogui")
        ...
```

Fungsi kode:

- Sistem mencoba AutoPy dulu.
- Jika AutoPy tidak ada, fallback ke PyAutoGUI.
- `move` dan `click` disimpan sebagai fungsi di `MouseController`.

Kode menerapkan mouse action:

```python
if frame_result.cursor_target is not None and not frame_result.paused:
    mouse.move(frame_result.cursor_target.x, frame_result.cursor_target.y)

if frame_result.click_fired:
    mouse.click()
```

Logic:

- Mouse bergerak hanya jika ada `cursor_target` dan runtime tidak paused.
- Mouse click hanya terjadi jika `click_fired=True`.
- Raw gesture tidak langsung mengontrol mouse.

## 9. Kode Overlay dan Exit

File:

```text
src/ai_virtual_mouse_experimental/real_mouse_runtime.py
```

Kode overlay:

```python
display_image = frame_result.landmarks_image if frame_result.landmarks_image is not None else image
```

Fungsi:

- Jika pipeline menghasilkan image dengan landmark, itu yang ditampilkan.
- Jika tidak, frame kamera asli yang ditampilkan.

Kode exit:

```python
if cv2.waitKey(1) & 0xFF == ord("q"):
    break
```

Fungsi:

- `cv2.waitKey(1)` mengecek keyboard.
- Jika tombol `q` ditekan, loop berhenti.

## Narasi Final untuk Menjelaskan Semua Alur

Gunakan narasi ini setelah demo:

> Program dimulai dari `run_real_mouse_runtime`. Di sana OpenCV membuka webcam dengan `cv2.VideoCapture`, lalu setiap frame dibaca dengan `cap.read`. Frame tersebut tidak langsung menjadi mouse action. Frame dikirim dulu ke `HandControlPipeline`.
>
> Di dalam pipeline, `HandTracker` memproses image dengan MediaPipe dan menghasilkan `HandTrackingResult`: landmark tangan, status jari, jarak pinch, dan backend yang dipakai. Setelah itu `hand_input_from_tracking` mengubah data tracking menjadi `GestureInput`.
>
> `GestureInput` masuk ke `gesture_engine.py`. Di sini aturan gesture ditentukan: open palm menjadi pause, index only menjadi move, index-middle pinch menjadi click, dan gesture lain menjadi idle. Untuk click, sistem belum langsung menekan mouse. Raw click masih melewati `update_click_debounce`.
>
> Debounce mengecek stable frames, armed state, release frames, dan cooldown. Jika valid, hasilnya menjadi `click_fired=True`. Kalau belum valid, click tidak dikeluarkan.
>
> Pipeline lalu menghasilkan `HandControlFrame`. Isinya antara lain `cursor_target`, `click_fired`, `paused`, `gesture_name`, dan `landmarks_image`. Setelah itu baru `real_mouse_runtime.py` membaca output tersebut. Jika ada cursor target dan tidak paused, `mouse.move` dipanggil. Jika `click_fired=True`, `mouse.click` dipanggil.
>
> Jadi alurnya jelas: webcam menghasilkan frame, hand tracker menghasilkan data tangan, gesture engine menghasilkan keputusan gesture, pipeline menghasilkan output kontrol, dan runtime menerapkan output itu ke mouse.

---

# Revisi Struktur — Timeline Video Fleksibel Lebih dari 10 Menit

Catatan produksi:

- Video tidak wajib 10 menit.
- Durasi boleh lebih panjang jika penjelasan kode dan benchmark membutuhkan waktu.
- Fokus utama: penonton paham demo, alur sistem, fungsi kode, benchmark, dan bukti improved lebih baik dari baseline.
- Timeline di bawah bisa dipakai sebagai struktur utama saat rekaman.

## Timeline Utama Video Tutorial

### 00:00–00:30 — Opening dan Tujuan Video

Visual:

- Presenter kecil di pojok.
- Tampilkan judul project: AI Virtual Mouse.
- Tampilkan layar desktop sebelum demo.

Narasi:

> Halo, saya Raditya. Di video ini saya akan mendemokan dan menjelaskan project AI Virtual Mouse. Fokus video ini bukan instalasi dari awal, tetapi bagaimana program dijalankan, bagaimana sistem bekerja dari kode, bagaimana baseline dibandingkan dengan versi improved, dan bagaimana benchmark digunakan untuk membuktikan hasil perbaikannya.

Cue editing:

- Tambahkan title overlay: `AI Virtual Mouse — Demo, Code Flow, Benchmark`.
- Jangan terlalu lama di opening. Langsung masuk demo.

---

### 00:30–02:30 — Demo Awal Versi Improved

Visual:

- Jalankan program improved.
- Tampilkan webcam preview.
- Tampilkan cursor bergerak dengan gesture index finger.
- Tampilkan click dengan gesture index-middle pinch.
- Tampilkan pause dengan open palm.

Command Bash:

```bash
source .venv-improved/Scripts/activate
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Command PowerShell:

```powershell
$env:PYTHONPATH='src'; .venv-improved\Scripts\python.exe -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

Narasi:

> Pertama saya tunjukkan dulu hasil akhirnya. Program ini membaca gerakan tangan dari webcam, lalu mengubahnya menjadi kontrol mouse. Untuk versi improved, gesture utamanya dibuat lebih sederhana: telunjuk saja untuk menggerakkan cursor, pinch telunjuk dan jari tengah untuk click, dan telapak terbuka untuk pause.
>
> Perhatikan bahwa cursor tidak bergerak langsung dari gambar webcam begitu saja. Di belakangnya ada pipeline: webcam membaca frame, hand tracker mendeteksi landmark tangan, gesture engine menentukan gesture, pipeline menghitung target cursor dan click, lalu runtime menjalankan mouse action.

Safety cue:

- Sebutkan tombol `q` untuk keluar.
- Sebutkan open palm untuk pause.
- Jangan arahkan cursor ke tombol berbahaya seperti delete, close, atau submit.

---

### 02:30–03:30 — Requirement dan Cara Menjalankan

Visual:

- Tampilkan terminal.
- Tampilkan struktur folder project.
- Tampilkan command run.

Narasi:

> Requirement utama program ini adalah Python environment yang sudah berisi OpenCV, MediaPipe, NumPy, dan backend mouse seperti AutoPy atau PyAutoGUI. OpenCV digunakan untuk membuka webcam dan membaca frame. MediaPipe digunakan untuk mendeteksi tangan. NumPy digunakan untuk perhitungan koordinat. AutoPy atau PyAutoGUI digunakan untuk menggerakkan mouse sistem operasi.
>
> Karena video ini adalah tutorial program, bukan tutorial instalasi, environment diasumsikan sudah siap. Untuk menjalankan versi improved, saya memakai module `ai_virtual_mouse_experimental` dengan mode demo, condition improved, dan flag `--allow-real-mouse` agar program boleh menggerakkan mouse asli.

Command model:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --download-model
```

Command smoke test:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --smoke-backend
```

Command demo:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition improved --allow-real-mouse
```

---

### 03:30–05:30 — Baseline Asli dan Masalah Kodenya

Visual:

- Buka file:

```text
src/video version/AiVirtualMouseProject.py
```

Tampilkan import:

```python
import time
import autopy
import cv2
import HandTrackingModule as htm
import numpy as np
```

Narasi:

> Sebelum menjelaskan versi improved, saya jelaskan dulu baseline asli. Baseline asli ada di file `src/video version/AiVirtualMouseProject.py`. Ini adalah versi awal AI Virtual Mouse. Di sini import yang digunakan cukup langsung: `cv2` untuk webcam, `HandTrackingModule` untuk deteksi tangan, `numpy` untuk mapping koordinat, `autopy` untuk mouse, dan `time` untuk menghitung FPS.

Tampilkan kode webcam:

```python
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
```

Narasi:

> Bagian ini membuka webcam, mengatur ukuran kamera, membuat detector tangan, dan mengambil ukuran layar. Jadi dari awal baseline sudah langsung menghubungkan webcam, detector, dan mouse screen.

Tampilkan loop:

```python
while True:
    success, img = cap.read()
```

Narasi:

> Setelah itu program masuk loop tanpa henti. Setiap iterasi membaca satu frame dari webcam. Frame ini kemudian diproses untuk mencari posisi tangan dan gesture.

Tampilkan click baseline:

```python
if fingers[1] == 1 and fingers[2] == 1:
    length, img, lineInfo = detector.findDistance(8, 12, img)
    if length < 40:
        autopy.mouse.click()
```

Narasi:

> Masalah utama baseline ada di bagian click. Jika telunjuk dan jari tengah terdeteksi naik, program menghitung jarak landmark 8 dan 12. Jika jaraknya kurang dari 40 pixel, program langsung memanggil `autopy.mouse.click()`. Tidak ada debounce, tidak ada cooldown, tidak ada stable frame, dan tidak ada armed state. Akibatnya satu gerakan yang sedikit tidak stabil bisa menghasilkan banyak click.

---

### 05:30–06:30 — Baseline Runtime untuk Perbandingan

Visual:

- Tampilkan command baseline runtime.

Command:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode demo --condition baseline --allow-real-mouse
```

Narasi:

> Selain baseline asli, project ini juga punya baseline runtime melalui `--condition baseline`. Ini bukan file baseline asli, tetapi mode runtime pembanding di sistem experimental. Mode ini digunakan agar baseline dan improved bisa dijalankan dalam kerangka yang sama. Dengan begitu perbandingan lebih adil, karena benchmark dan runtime memakai struktur yang sama, hanya condition yang berbeda.

---

### 06:30–08:30 — Alur Besar Sistem Improved

Visual:

- Tampilkan diagram teks.

```text
run_real_mouse_runtime()
    -> cv2.VideoCapture(...)
    -> cap.read()
    -> pipeline.process_frame(image)
        -> HandTracker.track(image)
        -> hand_input_from_tracking(...)
        -> classify_simple_real_mouse_gesture(...)
        -> map_point_to_output(...)
        -> apply_smoothing(...)
        -> update_click_debounce(...)
        -> HandControlFrame(...)
    -> mouse.move(...)
    -> mouse.click()
```

Narasi:

> Sekarang masuk ke versi improved. Alur besarnya seperti ini. Program dimulai dari `run_real_mouse_runtime`. Di sana webcam dibuka, frame dibaca, lalu frame dikirim ke pipeline. Pipeline memanggil hand tracker, mengubah tracking result menjadi gesture input, menjalankan gesture engine, mapping koordinat, smoothing, dan debounce. Hasil akhirnya adalah `HandControlFrame`. Setelah itu runtime baru memanggil `mouse.move` atau `mouse.click`.
>
> Jadi versi improved memisahkan tanggung jawab kode. Runtime mengurus kamera dan mouse. Hand tracker mengurus deteksi tangan. Gesture engine mengurus aturan gesture. Pipeline menggabungkan semuanya.

---

### 08:30–10:00 — Webcam dan Runtime Loop

Visual:

- Buka file:

```text
src/ai_virtual_mouse_experimental/real_mouse_runtime.py
```

Tampilkan kode:

```python
def run_real_mouse_runtime(config: ExperimentalConfig, plan: RuntimePlan) -> int:
    cv2 = import_module("cv2")
    mouse = _create_mouse_controller()
    cap = cv2.VideoCapture(config.backend.camera_index)
    cap.set(3, config.backend.camera_width)
    cap.set(4, config.backend.camera_height)
```

Narasi:

> Kode ini membuka runtime utama. `import_module("cv2")` memuat OpenCV. `_create_mouse_controller()` menyiapkan backend mouse. `cv2.VideoCapture` membuka webcam berdasarkan camera index. Lalu `cap.set` mengatur lebar dan tinggi kamera.

Ta
mpilkan kode:

```python
while True:
    success, image = cap.read()
    if not success:
        print("Camera frame could not be read.")
        break

    frame_result: HandControlFrame = pipeline.process_frame(image)
```

Narasi:

> Setelah kamera dibuka, program masuk loop. `cap.read()` membaca satu frame. Jika gagal, loop berhenti. Jika berhasil, frame dikirim ke `pipeline.process_frame(image)`. Di titik ini frame kamera mulai diproses menjadi gesture dan mouse command.

---

### 10:00–12:00 — Hand Tracker

Visual:

- Buka file:

```text
src/ai_virtual_mouse_experimental/hand_tracker.py
```

Tampilkan kode:

```python
@dataclass(frozen=True)
class HandTrackingResult:
    landmarks: list[Point] | None = None
    fingers_up: list[int] | None = None
    pinch_distance_px: float | None = None
    index_middle_vertical_delta_px: float | None = None
    success: bool = False
    backend_used: str = "unknown"
    fallback_reason: str | None = None
```

Narasi:

> Hand tracker menghasilkan `HandTrackingResult`. Data ini berisi landmark tangan, status jari, jarak pinch, status sukses, dan backend yang dipakai. Jadi output hand tracker belum berupa mouse action. Outputnya masih data tangan.

Tampilkan backend:

```python
class HandTracker:
    """Unified hand tracker: Tasks primary, Solutions fallback."""
```

Narasi:

> Hand tracker memakai MediaPipe. Sistem mencoba backend MediaPipe Tasks lebih dulu. Jika gagal, sistem fallback ke MediaPipe Solutions. Ini membuat runtime lebih tahan terhadap perbedaan environment.

---

### 12:00–13:30 — Hand Tracking Result ke Gesture Input

Visual:

- Buka file:

```text
src/ai_virtual_mouse_experimental/hand_control_pipeline.py
```

Tampilkan kode:

```python
def hand_input_from_tracking(
    result: HandTrackingResult, config: GestureEngineConfig
) -> GestureInput:
    fingers = result.fingers_up or []
    if len(fingers) < 5:
        return GestureInput()
    return GestureInput(
        thumb=bool(fingers[0]),
        index=bool(fingers[1]),
        middle=bool(fingers[2]),
        ring=bool(fingers[3]),
        pinky=bool(fingers[4]),
        pinch_distance_px=result.pinch_distance_px,
        pinch_duration_s=0.0,
        index_middle_vertical_delta_px=result.index_middle_vertical_delta_px or 0.0,
    )
```

Narasi:

> Setelah hand tracker selesai, pipeline mengubah `HandTrackingResult` menjadi `GestureInput`. List `fingers_up` diubah menjadi boolean seperti thumb, index, middle, ring, dan pinky. Jarak pinch juga diteruskan. Format ini lebih mudah dipakai gesture engine.

---

### 13:30–16:00 — Gesture Engine: Move, Click, Pause

Visual:

- Buka file:

```text
src/ai_virtual_mouse_experimental/gesture_engine.py
```

Tampilkan kode:

```python
def classify_simple_real_mouse_gesture(
    hand: GestureInput,
    config: GestureEngineConfig | None = None,
) -> GestureResult:
    cfg = config or GestureEngineConfig()

    if is_open_palm(hand):
        return _pause_result()

    if hand.index and hand.middle and not hand.ring and not hand.pinky:
        if is_pinching(hand, cfg):
            return _click_result("index_middle_stable_pinch")
        return GestureResult(name="idle", reason="index_middle_without_pinch")

    if hand.index and not hand.middle and not hand.ring and not hand.pinky:
        return _move_result()

    return GestureResult(name="idle", reason="no_supported_real_mouse_gesture")
```

Narasi:

> Gesture engine adalah bagian yang menentukan arti gerakan tangan. Jika telapak terbuka, hasilnya pause. Jika telunjuk dan jari tengah aktif lalu pinch valid, hasilnya click. Jika hanya telunjuk aktif, hasilnya move. Selain itu, gesture dianggap idle.

Tampilkan kode:

```python
def is_pinching(hand: GestureInput, config: GestureEngineConfig) -> bool:
    return (
        hand.pinch_distance_px is not None
        and hand.pinch_distance_px < config.click_threshold_px
    )
```

Narasi:

> Fungsi `is_pinching` mengecek apakah jarak pinch ada dan nilainya lebih kecil dari threshold. Ini yang membedakan gesture dua jari biasa dengan gesture click.

---

### 16:00–18:00 — Debounce Click

Visual:

- Tetap di `gesture_engine.py`.

Tampilkan kode:

```python
@dataclass(frozen=True)
class ClickDebounceConfig:
    stable_frames_required: int = 2
    release_frames_required: int = 2
    cooldown_seconds: float = 0.35
```

Tampilkan logic:

```python
cooldown_elapsed = now_s - state.last_click_time_s >= cfg.cooldown_seconds
stable = next_state.pressed_frames >= cfg.stable_frames_required
if next_state.armed and stable and cooldown_elapsed:
    return ClickDebounceResult(..., emit_click=True, reason="stable_click_emitted")
```

Narasi:

> Perbaikan penting ada di debounce. Baseline langsung click ketika jarak dua jari kurang dari threshold. Versi improved tidak begitu. Pinch harus stabil selama beberapa frame, sistem harus dalam kondisi armed, dan cooldown dari click sebelumnya harus sudah lewat. Baru setelah itu `emit_click=True`.
>
> Inilah alasan false click bisa turun besar. Program tidak lagi menganggap setiap frame pinch sebagai click baru.

---

### 18:00–20:00 — Hand Control Pipeline dan Mapping Cursor

Visual:

- Buka:

```text
src/ai_virtual_mouse_experimental/hand_control_pipeline.py
```

Tampilkan output:

```python
@dataclass(frozen=True)
class HandControlFrame:
    cursor_target: Point | None = None
    click_fired: bool = False
    paused: bool = False
    gesture_name: str = "idle"
    feedback_label: str = "Idle"
    backend_used: str = "unknown"
    fps: float = 0.0
    safety_triggered: bool = False
    hand_detected: bool = False
    landmarks_image: np.ndarray | None = None
```

Narasi:

> Pipeline menggabungkan semuanya menjadi `HandControlFrame`. Field `cursor_target` adalah posisi cursor final. Field `click_fired` adalah hasil click setelah debounce. Field `paused` memberi tahu runtime apakah mouse action perlu ditahan. Field `landmarks_image` dipakai untuk tampilan overlay.

Tampilkan import:

```python
from .cursor_mapping import apply_smoothing, map_point_to_output
from .gesture_engine import classify_simple_real_mouse_gesture, update_click_debounce
from .hand_tracker import HandTracker, HandTrackingResult
```

Narasi:

> Dari import ini terlihat pipeline memakai hand tracker, gesture engine, mapping, smoothing, dan debounce. Jadi pipeline adalah penghubung antar modul, bukan sekadar helper kecil.

---

### 20:00–21:30 — Mouse Action Nyata

Visual:

- Kembali ke:

```text
src/ai_virtual_mouse_experimental/real_mouse_runtime.py
```

Tampilkan controller:

```python
def _create_mouse_controller() -> MouseController:
    try:
        autopy = import_module("autopy")
        width, height = autopy.screen.size()
        return MouseController(
            width=int(width),
            height=int(height),
            backend="autopy",
            move=autopy.mouse.move,
            click=autopy.mouse.click,
        )
```

Tampilkan action:

```python
if frame_result.cursor_target is not None and not frame_result.paused:
    mouse.move(frame_result.cursor_target.x, frame_result.cursor_target.y)

if frame_result.click_fired:
    mouse.click()
```

Narasi:

> Mouse action benar-benar terjadi di runtime. Jika ada cursor target dan tidak pause, `mouse.move` dipanggil. Jika `click_fired=True`, `mouse.click` dipanggil. Jadi gesture tidak langsung mengklik mouse. Gesture harus melewati tracker, gesture engine, pipeline, dan debounce dulu.

---

### 21:30–24:00 — Benchmark: Cara Kerja dan Fungsi

Visual:

- Buka file:

```text
src/ai_virtual_mouse_experimental/benchmark_shell.py
src/ai_virtual_mouse_experimental/benchmark_grid.py
src/ai_virtual_mouse_experimental/benchmark_report.py
```

Command:

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition baseline
PYTHONPATH=src python -m ai_virtual_mouse_experimental --mode benchmark --condition improved
```

Narasi:

> Benchmark digunakan untuk membandingkan baseline dan improved secara lebih objektif. Benchmark tidak menggerakkan mouse sistem operasi. Benchmark memakai simulated cursor dan tar
get grid. Artinya sistem membuat target di layar benchmark, lalu menghitung apakah click mengenai target atau tidak. Jika click terjadi di dalam radius target, dihitung hit. Jika di luar radius, dihitung false click.

Detail konsep:

- `generate_grid_targets(settings)`: membuat target benchmark.
- `random_seed`: membuat urutan target konsisten.
- `register_click`: mencatat click.
- Hit: jarak click ke pusat target <= radius target.
- False click: click di luar target.
- `completion_time_s`: waktu menyelesaikan target.
- `false_clicks_before_hit`: jumlah false click sebelum hit.
- `compute_metrics`: menghitung ringkasan hasil.

Narasi lanjutan:

> Dengan cara ini baseline dan improved dibandingkan memakai kondisi yang sama. Perbedaannya bukan target, tetapi logic condition yang dipakai. Baseline cenderung menghasilkan click berlebih, sedangkan improved memakai debounce sehingga click lebih terkendali.

---

### 24:00–25:30 — Compare Sessions dan Hasil

Visual:

- Tampilkan command compare.

```bash
PYTHONPATH=src python -m ai_virtual_mouse_experimental --compare-sessions outputs/sessions/session-a outputs/sessions/session-b
```

Narasi:

> Setelah benchmark baseline dan improved dijalankan, hasil session dibandingkan. Dari perbandingan ini kita melihat metrik utama: hit rate, false click, dan total click.

Tampilkan evidence:

```text
Hit rate baseline : 100%
Hit rate improved : 100%
False clicks      : 192,8 -> 4,2
Total clicks      : 212,8 -> 24,2
```

Narasi:

> Hasilnya menunjukkan hit rate sama-sama 100 persen. Artinya kedua versi bisa menyelesaikan target. Perbedaan besar ada pada false click dan total click. False click turun dari 192,8 menjadi 4,2. Total click turun dari 212,8 menjadi 24,2. Jadi improved bukan hanya berhasil menjalankan fungsi yang sama, tetapi juga jauh lebih stabil dan lebih sedikit salah click.

---

### 25:30–27:00 — Kesimpulan Evidence-Based

Visual:

```text
1. Baseline bisa bekerja, tetapi click terlalu agresif.
2. Improved memisahkan tracker, gesture engine, pipeline, dan runtime.
3. Benchmark membuktikan false click dan total click turun besar.
```

Narasi:

> Kesimpulannya, baseline asli sudah bisa mengubah gesture tangan menjadi mouse virtual, tetapi logic click-nya terlalu langsung. Ketika jarak dua jari kurang dari threshold, mouse langsung click. Tanpa debounce dan cooldown, ini menyebabkan banyak false click.
>
> Versi improved memperbaiki masalah itu dengan struktur yang lebih jelas. Webcam dan mouse action ada di runtime. Deteksi tangan ada di hand tracker. Aturan gesture ada di gesture engine. Mapping, smoothing, dan debounce digabung di pipeline. Hasil akhirnya baru dikirim ke mouse action.
>
> Dari benchmark, improved terbukti lebih baik. Hit rate tetap 100 persen, false click turun dari 192,8 menjadi 4,2, dan total click turun dari 212,8 menjadi 24,2. Jadi improved lebih stabil, lebih terkendali, dan lebih layak digunakan sebagai AI Virtual Mouse.

---

### 27:00–Selesai — Closing

Visual:

- Tampilkan demo singkat lagi atau layar hasil benchmark.
- Presenter kecil muncul lagi.

Narasi:

> Itu penjelasan project AI Virtual Mouse dari demo, cara menjalankan, baseline, alur kode improved, sampai benchmark. Dengan struktur ini kita bisa melihat bukan hanya programnya berjalan, tetapi juga bagian kode mana yang bertanggung jawab untuk webcam, hand tracker, gesture engine, pipeline, mouse action, dan evaluasi benchmark.

Editing cue:

- Akhiri dengan freeze frame hasil benchmark atau cursor demo.
- Tambahkan teks: `Improved: same hit rate, far fewer false clicks`.
