# GLOSSARY — Image Processing & AI Virtual Mouse

A living reference of terms. Every lesson should **use these exact words** for these concepts. If you need a new term, add it here first, then use it in the lesson.

---

## Core concepts

**Citra (image)**
Tabel dua dimensi berisi angka, di mana tiap angka mewakili kecerahan atau warna di satu titik kecil (piksel). Bentuk storage: NumPy array dengan shape `(height, width, channels)`.

**Piksel (pixel)**
Satu titik dalam citra. Singkatan dari *picture element*. Citra 640×480 berarti 640 kolom × 480 baris piksel.

**Channel**
"Lapisan" warna dalam satu piksel. Citra RGB punya 3 channel: Red, Green, Blue. Grayscale punya 1 channel.

**Grayscale**
Citra 1-channel, tiap piksel bernilai 0 (hitam) sampai 255 (putih) untuk 8-bit.

**BGR (vs RGB)**
OpenCV menyimpan / membaca warna dalam urutan **B**lue-**G**reen-**R**ed, bukan RGB. Jebakan klasik. Mnemonic: *"OpenCV terbalik."*

**8-bit**
Tiap channel menyimpan nilai 0–255 (= 2⁸). Kenapa bukan 0–100 atau 0–1000? Karena trade-off memori vs kehalusan; 256 nilai cukup untuk mata manusia.

**Frame**
Satu gambar utuh dari sumber video (webcam / file). Video = urutan frame.

**NumPy array**
Struktur data tabular dari library NumPy. OpenCV menyimpan citra sebagai array NumPy. Akses piksel: `img[row, col]` atau `img[y, x]`.

---

## AI Virtual Mouse — domain terms

(These are taken directly from `AI Virtual Mouse/CONTEXT.md` — the project's own glossary.)

**Real Mouse Runtime**
Runtime di mana gesture mengontrol kursor OS sungguhan. _Avoid_: "video version", "real app".

**Benchmark Runtime**
Runtime di mana gesture mengontrol kursor simulasi di dalam window benchmark. _Avoid_: "test mode", "fake mouse".

**Shared Hand-Control Pipeline**
Alur bersama: hand landmarks → gesture state → mapped cursor intent. Dipakai kedua runtime.

**Backend Fallback**
Pergantian dari MediaPipe Tasks ke MediaPipe Solutions yang **harus terlihat di metadata**. Tidak boleh silent.

**Simple Real Mouse Profile**
Profil gesture minimal: movement, left click, pause. Tidak termasuk drag atau scroll.

**Pause Toggle Gesture**
Open-palm hold yang toggle pause/unpause. Runtime mengabaikan aksi cursor & click saat paused.

**Stable Pinch Click**
Click kiri yang dipancarkan **sekali** saat pinch (ibu jari + telunjuk) stabil selama N frame debounce. Re-arm setelah release.

**Default Tracking Bounds**
Rectangle kamera yang dikurangi (gaya video) untuk mapping cursor. Default sebelum kalibrasi user.

**Optional Calibration**
Capture bounds tangan user yang bisa menimpa Default Tracking Bounds. Tidak wajib.

**Adaptive Smoothing Default**
Kebijakan smoothing default untuk cursor. Dikurangi jitter, dipertahankan responsif untuk gerakan besar. Dikonfigurasi via TOML.

**Runtime Safety Controls**
Mekanisme escape wajib untuk Real Mouse Runtime: keyboard quit, Pause Toggle Gesture, corner failsafe.

---

## Reserved for future lessons

*(terms will be added here as new lessons introduce them, e.g. convolution, threshold, edge detection, MediaPipe landmarks, etc.)*
