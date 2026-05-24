# Glosarium — Main Version

Istilah teknis yang muncul di kode main version. Kalau baru pertama kali lihat proyek ini, baca glosarium dulu.

## A

**Anchor (Drag Anchor):** titik referensi yang direkam saat Drag dimulai. Terdiri dari dua koordinat: posisi jari di kamera dan posisi kursor di layar. Selama Drag, kursor bergerak relatif dari anchor.

**Autopy:** library Python untuk kontrol mouse/keyboard. Digunakan untuk `move()`, `click()`, `toggle()`.

## B

**BGR:** format warna default OpenCV. Urutannya Blue-Green-Red, bukan Red-Green-Blue seperti umumnya.

**Bounding Box:** kotak terkecil yang membungkus semua landmark tangan.

## C

**Clamping:** membatasi nilai dalam rentang tertentu. `max(0, min(x, max_x))` → x dipaksa antara 0 dan max_x.

**Click Delay:** jeda (detik) setelah klik untuk mencegah double-click tidak sengaja.

**Confidence:** tingkat keyakinan MediaPipe bahwa yang dideteksi benar-benar tangan. 0.0 = nggak yakin, 1.0 = sangat yakin.

**Convergence Lag:** jeda dari nilai awal (0) menuju nilai stabil. Dihindari dengan inisialisasi langsung.

**Coordinator:** design pattern di mana satu komponen mengatur alur kerja komponen lain tanpa berisi business logic. Main loop adalah coordinator.

**ctypes:** modul Python untuk memanggil fungsi dari DLL/shared library. Dipakai untuk Windows API scroll wheel fallback.

## D

**Dead Zone:** area di mana input diabaikan. Dua jenis: (1) pinggir frame kamera, (2) tengah kamera untuk scroll.

**Debounce:** menunggu sinyal stabil selama periode tertentu (300ms) sebelum bereaksi. Menghilangkan flicker 1-2 frame.

**Drag Sensitivity:** multiplier untuk kecepatan drag. 1.0 = sama dengan Move. <1.0 = lebih lambat. >1.0 = lebih cepat.

## E

**Edge-Triggered:** action dipicu saat transisi (false → true), bukan selama kondisi true. Dipakai untuk clicks.

**EMA (Exponential Moving Average):** teknik smoothing. `new = old + (raw - old) / factor`. Bobot lebih ke data baru.

## F

**Frame Reduction:** margin dead zone di pinggir frame kamera (100px). Mencegah kursor mentok ujung layar.

**Freeze (Post-Click):** jeda 200ms setelah klik di mana kursor tidak bergerak. Mencegah drift.

## G

**Gesture Profile:** satu set definisi pola jari untuk setiap gesture. `practical_no_thumb` dan `legacy`.

**Graceful Degradation:** fitur tetap berfungsi (dengan keterbatasan) meski dependensi tidak lengkap.

## H

**Hand Landmarks:** 21 titik referensi di tangan (0 = pergelangan, 4 = ujung jempol, 8 = ujung telunjuk, dst).

**Hand-Lost Grace:** toleransi beberapa frame (4) sebelum reset state saat tangan hilang dari deteksi.

**Handedness:** tangan kiri atau kanan. Thumb detection di video version hanya berfungsi untuk tangan kanan.

**Hold-Time:** durasi minimal (100ms) kondisi harus bertahan sebelum dianggap valid. Dipakai untuk click.

**Hysteresis:** batas ON (28px) berbeda dengan batas OFF (38px). Mencegah osilasi di sekitar threshold.

## I

**Interpolation (`np.interp`):** mapping linear dari satu rentang ke rentang lain. Koordinat kamera → koordinat layar.

## L

**Landmark:** lihat Hand Landmarks.

## M

**MCP (Metacarpophalangeal):** sendi pangkal jari. Landmark 2 (jempol), 5 (telunjuk), 9 (tengah), 13 (manis), 17 (kelingking).

**MediaPipe:** framework computer vision dari Google untuk deteksi tangan, wajah, pose, dll.

**MOUSEEVENTF_WHEEL:** konstanta Windows API (`0x0800`) untuk event scroll wheel.

## N

**None Wildcard:** dalam pattern matching, `None` = nilai di posisi ini diabaikan. Dipakai untuk mengabaikan jempol.

**Normalized Coordinates:** koordinat 0.0-1.0 (proporsi dimensi gambar). Dikonversi ke pixel.

## O

**Orchestrator:** lihat Coordinator.

## P

**Pattern Matching:** membandingkan state jari aktual `[1,1,0,0,0]` dengan pola yang diharapkan. Posisi `None` diabaikan.

**Pinch:** gerakan menjepit dua jari. Jarak pinch diukur dengan Euclidean distance.

**PIP (Proximal Interphalangeal):** sendi tengah jari. Landmark 2 tingkat di bawah TIP (misal landmark 6 untuk telunjuk).

**Post-Click Freeze:** lihat Freeze.

## R

**Rate Limiting:** membatasi frekuensi aksi. Scroll max tiap 120ms, click delay 100ms.

**RGB:** format warna Red-Green-Blue. Diharapkan MediaPipe. Berbeda dengan BGR (OpenCV).

## S

**Scale Factor:** rasio pixel layar vs pixel kamera. Tiap 1px gerakan tangan = N pixel gerakan kursor.

**Sensitivity (Thumb):** multiplier threshold deteksi jempol. 1.5 = perlu jarak 52.5px.

**Smoothing:** teknik mengurangi jitter/goyangan kursor. Pakai EMA.

**State Machine:** sistem dengan state (kondisi saat ini) dan aturan transisi. Lebih robust dari if-else.

**Stop Pattern:** pola jari yang memaksa mode `"None"`. Dipakai untuk gesture "berhenti".

## T

**Tasks API:** API terbaru MediaPipe. Pengganti Solutions API yang deprecated.

**Threshold:** nilai batas pemicu aksi.

**TIP:** ujung jari. Landmark 4, 8, 12, 16, 20.

**Toggle (Mouse):** tahan/lepas tombol. Dipakai untuk Drag.

## W

**Wheel Delta:** satuan scroll Windows. 120 = 1 notch. Dikali jumlah unit scroll.

**Wildcard:** lihat None Wildcard.

**Wrapper:** kode pembungkus library lain. Menyederhanakan interface atau menambah fallback.
