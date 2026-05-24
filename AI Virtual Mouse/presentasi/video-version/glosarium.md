# Glosarium — Video Version

## A

**Anchor (Drag Anchor):** titik referensi yang direkam saat Drag dimulai. Posisi kursor selama Drag dihitung relatif dari anchor ini, bukan dari posisi absolut jari.

**autopy:** library Python untuk kontrol mouse dan keyboard. Cross-platform (Windows, Mac, Linux). Digunakan untuk `move()`, `click()`, dan `toggle()`.

## B

**BGR (Blue-Green-Red):** format warna default OpenCV. Berbeda dengan RGB (Red-Green-Blue) yang lebih umum. Perlu konversi `cv2.COLOR_BGR2RGB` sebelum dikasih ke MediaPipe.

**Bounding Box:** kotak terkecil yang membungkus semua titik landmark tangan. Berguna untuk tahu area tangan di frame.

## C

**Contiguous Array:** array NumPy yang elemennya tersimpan berurutan di memori. Syarat teknis MediaPipe Tasks API.

**ctypes:** modul Python untuk manggil fungsi dari DLL/shared library (C/C++). Di sini dipakai buat manggil Windows API `mouse_event`.

## D

**Dead Zone:** area di mana input diabaikan. Ada dua dead zone: (1) pinggir frame kamera (`FRAME_REDUCTION = 100px`) biar kursor nggak mentok ke ujung layar, (2) tengah kamera (`SCROLL_CENTER_DEAD_ZONE_PX = 35px`) biar nggak scroll tanpa sengaja.

## E

**Edge-Triggered:** aksi dipicu hanya saat transisi (false → true), bukan selama kondisi true. Dipakai untuk click supaya nggak spam tiap frame.

**Exponential Moving Average (EMA):** teknik smoothing yang memberi bobot lebih ke data terbaru. Formula: `new = old + (raw - old) / factor`. Semakin besar factor, semakin smooth.

## F

**Frame Reduction:** lihat Dead Zone.

**fingersUp():** fungsi yang mengembalikan status 5 jari (1 = naik, 0 = turun) sebagai list `[thumb, index, middle, ring, pinky]`.

## H

**Hand Landmarks:** 21 titik referensi di tangan yang dideteksi MediaPipe. Dari pergelangan (landmark 0) sampai ujung jari (landmark 4, 8, 12, 16, 20).

**Handedness:** tangan mana yang dipakai (kiri atau kanan). Deteksi jempol berbasis x-coordinate cuma berfungsi untuk tangan kanan.

## I

**Interpolation (`np.interp`):** mapping nilai dari satu rentang ke rentang lain secara linear. Misal: koordinat x di kamera (100-540) → koordinat x di layar (0-1920).

## L

**Landmark:** lihat Hand Landmarks.

**Landmark ID:** nomor 0-20 yang mengidentifikasi titik spesifik di tangan. 0 = pergelangan, 4 = ujung jempol, 8 = ujung telunjuk, 12 = ujung tengah, 16 = ujung manis, 20 = ujung kelingking.

## M

**Magic Number:** angka yang ditulis langsung di kode tanpa penjelasan. Contoh: `if length < 28`. Di proyek ini, semua magic number dipindahkan ke `config.py`.

**MediaPipe:** framework computer vision dari Google. Di sini dipakai untuk hand tracking (deteksi dan tracking tangan).

**Mirror:** membalik gambar secara horizontal (`cv2.flip(img, 1)`) supaya gerakan tangan terasa natural (tangan kiri = kiri layar).

## N

**None wildcard:** dalam pattern matching gesture, `None` berarti "nilai di posisi ini diabaikan". Dipakai untuk mengabaikan jempol.

**Normalized Coordinates:** koordinat 0.0-1.0 yang menyatakan proporsi dari lebar/tinggi gambar. Harus dikonversi ke pixel dengan `int(lm.x * width)`.

**np.interp:** lihat Interpolation.

## P

**PIP (Proximal Interphalangeal):** sendi tengah jari. Dalam deteksi jari naik/turun, posisi y ujung jari dibandingkan dengan posisi y PIP. Ujung jari di atas PIP → jari naik.

**Pinch:** gerakan menjepit dua jari. Jarak pinch diukur dengan `findDistance()`.

## R

**Rate Limiting:** membatasi seberapa sering suatu aksi bisa terjadi. Scroll dibatasi minimal 120ms antar trigger.

**RGB (Red-Green-Blue):** format warna yang diharapkan MediaPipe. Berbeda dengan BGR (OpenCV).

## S

**Smoothing:** teknik mengurangi jitter/goyangan. Di sini pakai Exponential Moving Average.

## T

**Tasks API:** API terbaru MediaPipe (`mediapipe.tasks.vision.HandLandmarker`). Pengganti Solutions API yang udah deprecated.

**Threshold:** nilai batas. Kalau nilai aktual melewati threshold, suatu aksi dipicu.

**Toggle:** fungsi mouse untuk tahan/lepas tombol. `toggle(LEFT, True)` = tahan klik kiri. `toggle(LEFT, False)` = lepas. Dipakai untuk Drag.

## W

**Wildcard:** lihat None wildcard.
