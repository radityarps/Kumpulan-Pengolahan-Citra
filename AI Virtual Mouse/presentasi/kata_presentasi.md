# Kata-Kata Presentasi Sidang — AI Virtual Mouse

> Full script narasi untuk 18 slide. Bahasa campuran natural (Indonesia + English technical terms).
> Estimasi total: 12-14 menit. Tiap slide: 30-60 detik.

---

## Slide 1 — Judul

Selamat pagi/siang, Bapak/Ibu dosen penguji.

Perkenalkan, saya Raditya, dari mata kuliah Pengolahan Citra semester 6.

Hari ini saya akan mempresentasikan proyek AI Virtual Mouse — sistem yang memungkinkan kita mengontrol kursor komputer hanya dengan gestur tangan, tanpa menyentuh mouse fisik sama sekali.

Tapi presentasi ini bukan cuma soal "ini hasil akhirnya". Saya mau cerita perjalanannya — dari awal cuma copy-paste tutorial YouTube, sampai akhirnya rewrite total jadi sistem modular. Karena justru di proses itulah pembelajaran paling besarnya terjadi.

---

## Slide 2 — Kenapa Virtual Mouse?

Jadi kenapa sih virtual mouse?

Simpelnya: kita bisa kontrol kursor pakai tangan. Cuma modal webcam. Nggak perlu mouse fisik.

Bayangin dua use case. Pertama, presentasi — kayak sekarang. Kita bisa ganti slide, tunjuk sesuatu, tanpa megang apa pun. Kedua, aksesibilitas — buat orang yang punya keterbatasan motorik, gerakin mouse fisik itu susah. Tapi angkat jari? Lebih mudah.

Jadi motivasinya sederhana: touchless interaction yang accessible.

---

## Slide 3 — Mulai dari Mana?

Nah, mulai dari mana?

Saya mulai dari tutorial YouTube. Murtaza's Workshop — channel computer vision yang cukup populer. Videonya judulnya "AI Virtual Mouse | OpenCV Python". Ditonton 843 ribu kali. Satu jam tutorial, kodenya cuma sekitar 140 baris.

Keliatannya simpel. Deteksi tangan pakai MediaPipe, terus gerakin kursor sesuai posisi jari.

Saya pikir: "OK, ini tinggal jalanin, beres."

Ternyata... nggak sesimpel itu.

---

## Slide 4 — Fase 1: Copy-Paste

Jadi saya copy-paste kode dari tutorial. Jalankan. Dan... kursor gerak!

Flow-nya simpel: webcam nangkap gambar → MediaPipe deteksi tangan (21 landmarks) → kita cek jari mana yang naik → klasifikasi gestur → mapping koordinat ke layar → gerakin kursor.

Secara teknis: jalan. Tapi ada yang aneh...

---

## Slide 5 — Masalah #1: Scroll Nggak Jalan

Masalah pertama: scroll.

Di tutorial, scroll pakai `autopy.mouse.toggle()`. Fungsi `toggle()` itu buat "tahan tombol mouse", bukan scroll wheel beneran. Jadi pas saya coba scroll di browser, halamannya nggak gerak. Cuma kursor doang yang gerak.

Ini bug serius karena scroll itu gestur paling sering dipakai selain move.

Solusinya: saya bypass Autopy dan panggil langsung Windows API lewat `ctypes`. Jadi kita kirim event `MOUSEEVENTF_WHEEL` langsung ke sistem operasi. Ini Windows-only — tapi karena development di Windows, cukup untuk sekarang.

> 📍 **Lokasi kode:**
> - `video-version/AIVirtualMouse.py` → `_scroll()` baris ~54: fallback ctypes Windows API
> - `src/mouse_controller.py` → `_scroll()` baris ~122: implementasi production dengan try/except
> - Dokumentasi inline: blok `MASALAH #1 / Slide 5` di kedua file

---

## Slide 6 — Masalah #2: Kursor Kebalik

Masalah kedua lebih subtle: kursor geraknya kebalik.

Saya gerakin tangan ke kanan, kursor malah ke kiri. Setelah debugging, ketemu penyebabnya: webcam itu mirror. Gambar yang kita lihat di layar itu kebalikan dari aslinya. Tutorial pakai rumus `wScr - clocX` buat nge-balikin — tapi di setup saya, itu malah bikin double-inversion.

Solusinya: `cv2.flip(img, 1)`. Satu baris. Mirror gambar dari webcam, terus koordinat langsung dipakai apa adanya — nggak perlu di-invert lagi. Hasilnya: tangan kiri = layar kiri. Natural.

> 📍 **Lokasi kode:**
> - `video-version/AIVirtualMouse.py` → `main()` PHASE 1: setelah `cap.read()`, baris `cv2.flip(img, 1)`
> - `src/ai_virtual_mouse.py` → `main()` PHASE 1: blok `MASALAH #2 / Slide 6`
> - Dokumentasi inline: blok `╔ MASALAH #2 / Slide 6` di kedua file

---

## Slide 7 — Masalah #3: Jempol Unreliable

Masalah ketiga: jempol.

Cara tutorial deteksi jempol itu dengan x-coordinate: "kalau ujung jempol lebih kanan dari sendinya, berarti naik". Ini cuma berfungsi buat tangan kanan yang telapaknya menghadap kamera.

Begitu kita pakai tangan kiri — atau tangan diputar sedikit — deteksinya ngaco. Kadang jempol kebaca naik padahal turun, atau sebaliknya. Gesture jadi unreliable.

Solusi paling pragmatis: abaikan jempol. Di semua gesture pattern, jempol kita kasih nilai `None` — alias wildcard. Jadi classifier cuma lihat 4 jari: telunjuk, tengah, manis, kelingking. Solusi simpel, tapi efektif.

> 📍 **Lokasi kode:**
> - `video-version/AIVirtualMouse.py` → `_match_pattern()` baris ~84: logika None wildcard
> - `src/hand_tracking_module.py` → `fingersUp()` baris ~199: deteksi jempol distance-based
> - `src/gesture_profiles.py` → profile `practical_no_thumb`: `[None, ...]` di setiap pattern
> - Dokumentasi inline: blok `MASALAH #3 / Slide 7` di ketiga file

---

## Slide 8 — Gesture Kurang Lengkap

Setelah tiga bug diperbaiki, saya lihat gesture-nya masih kurang.

Tutorial cuma punya 4 gesture: Move, Left Click, Right Click, Scroll. Itu pun right click pakai 5 jari naik semua — susah dan nggak natural. Scroll masih broken.

Saya tambah 2 gesture lagi dan perbaiki yang ada: Drag (buat drag-and-drop file) dan perbaikan Scroll. Right click diganti dari 5 jari jadi 3 jari (telunjuk, tengah, manis) + pinch antara telunjuk dan jari manis.

Sekarang total 6 gesture: Move, Left Click, Right Click, Drag, Scroll — dengan gesture yang lebih natural.

> 📍 **Lokasi kode:**
> - `video-version/AIVirtualMouse.py` → `main()` gesture blocks:
>   - Drag: `[*,0,0,0,0]` (kepalan) + anchor-based relative movement
>   - Right Click: `[*,1,1,1,0]` (3 jari) + pinch 8→16 < 34px
>   - Scroll: `[*,1,1,1,1]` (4 jari) + camera center boundary
> - `src/gesture_profiles.py` → profile `practical_no_thumb`:
>   - `drag_pattern: [None, 0, 0, 0, 0]`
>   - `right_click_pattern: [None, 1, 1, 1, 0]`
>   - `scroll_pattern: [None, 1, 1, 1, 1]`
> - Dokumentasi inline: blok `MASALAH #4 / Slide 8` di video-version

---

## Slide 9 — Rangkuman Fine-Tuning

Jadi total ada 8 perbaikan di fase fine-tuning ini: scroll beneran, kamera mirror, jempol diabaikan, right click diperbaiki, drag ditambahin, click logic dari spam jadi edge-triggered, threshold dituning (28px buat click, 34px buat right click), dan scroll pakai camera center boundary.

> 📍 **Lokasi kode (8 perbaikan):**
> 1. Scroll → `video-version/AIVirtualMouse.py::_scroll()` + `src/mouse_controller.py::_scroll()`
> 2. Mirror → `video-version/AIVirtualMouse.py` + `src/ai_virtual_mouse.py` (PHASE 1: `cv2.flip`)
> 3. Jempol → `src/hand_tracking_module.py::fingersUp()` + `src/gesture_profiles.py` + `_match_pattern()`
> 4. Right Click 5→3 jari → `video-version/AIVirtualMouse.py` RC block + `src/gesture_profiles.py::right_click_pattern`
> 5. Drag (baru) → `video-version/AIVirtualMouse.py` Drag block + `src/gesture_profiles.py::drag_pattern`
> 6. Edge-triggered click → `video-version/AIVirtualMouse.py` LC block (`click_ready` flag)
> 7. Threshold → `video-version/config.py` (`LEFT_CLICK_PINCH_PX=28`, `RIGHT_CLICK_PINCH_PX=34`)
> 8. Scroll center boundary → `video-version/AIVirtualMouse.py` Scroll block (dead zone ±35px)

Setelah semua perbaikan ini, kode udah jalan lebih baik. Gesture lebih lengkap, lebih natural. Saya pikir: "OK, selesai."

Tapi pas saya pakai beneran sehari-hari... masih ada masalah.

---

## Slide 10 — Kenapa Masih Nggak Enak?

Coba bayangin: saya lagi drag file. Kepalan sedikit kendor karena jari reflek gerak — langsung drag putus, file ke-drop di tempat acak.

Atau: lagi mode Move, tiba-tiba satu frame flicker, langsung ganti ke mode Click. Kursor berhenti, nge-klik sesuatu yang nggak dimaksud.

Atau: pas lagi klik, setiap frame nge-klik lagi dan lagi. Spam click. Karena satu frame pinch-nya masih di bawah threshold, langsung trigger lagi.

Semua masalah ini bukan salah gesture-nya. Bukan salah kameranya. Ini salah struktur kodenya.

> 📍 **Lokasi kode (BEFORE — video version):**
> - `video-version/AIVirtualMouse.py` → main loop: tidak ada state management
>   - Drag: langsung `if _match_pattern(fingers, [None,0,0,0,0])` tanpa hold-time
>   - Click: langsung `if length < 28: autopy.mouse.click()` tanpa edge-trigger
>   - Mode: langsung `if-elif` chain, flicker 1 frame langsung ganti
> 📍 **Lokasi kode (AFTER — main version):**
> - `src/gesture_classifier.py` → semua state machine logic (detail di Slide 15)
> - `src/ai_virtual_mouse.py` → hand-lost grace di main loop

---

## Slide 11 — Akar Masalah: Nggak Ada "State"

Akar masalahnya: setiap frame diproses sendiri-sendiri.

Frame 1: "Oh, ini gesture Drag." → OK.
Frame 2: Satu frame flicker, jari sedikit berubah → "Oh, ini bukan gesture apa-apa." → Mode ganti.

Kode nggak ingat apa yang terjadi di frame sebelumnya. Nggak ada memori. Nggak ada "state".

Solusinya butuh tiga hal: debounce (harus stabil beberapa frame dulu sebelum ganti gesture), hysteresis (batas buat ON beda sama batas OFF, jadi nggak bolak-balik di threshold), dan state machine (ingat gesture sebelumnya, tahu konteks transisinya).

> 📍 **Lokasi kode:**
> - `src/gesture_classifier.py` → class `GestureClassifier`: semua state machine logic
>   - Debounce 300ms: method `classify()` → `_debounce_stable_mode()`
>   - Hysteresis ON≠OFF: method `_handle_left_click()` → `ON_PX=28` vs `OFF_PX=38`
>   - State memory: attributes `current_mode`, `stable_mode`, `click_ready`, `drag_active`
> - Dokumentasi inline: blok `MASALAH #5, #6, #8` di class docstring

---

## Slide 12 — Plus: Nggak Bisa Dites

Masalah struktural kedua: kode nggak bisa dites.

Semua logic — deteksi tangan, klasifikasi gestur, mapping koordinat, kontrol mouse, FPS counter — semua dalam satu main loop, satu file yang sama.

Mau ganti threshold? Edit kode, tes manual sambil liat webcam. Mau yakin gesture classifier-nya bener? Nggak bisa unit test. Harus gerakin tangan beneran di depan kamera. Mau tambah gesture? Bisa ngerusak logic yang lain karena semuanya interdependent.

Ini bukan cuma masalah kenyamanan ngoding. Ini masalah correctness. Saya sebagai developer nggak bisa buktikan kode saya benar tanpa tes.

> 📍 **Lokasi kode (BEFORE):**
> - `video-version/AIVirtualMouse.py` → 1 file, ~400 baris, semua logic bercampur
> 📍 **Lokasi kode (AFTER — modular):**
> - `src/` → 8 modul terisolasi (daftar lengkap di Slide 14)
> - `tests/` → 33 unit tests (test_smoke.py, test_gestures.py, test_drag.py, dll)
> - Dokumentasi inline: blok `MASALAH #7 / Slide 12-13` di `src/ai_virtual_mouse.py`

---

## Slide 13 — Insight

Di titik ini, saya sadar:

**"Masalahnya bukan di gesture-nya. Masalahnya di struktur kodenya."**

Kode yang saya tulis — walaupun gesture-nya udah diperbaiki — arsitekturnya salah. Single-loop monolithic nggak scalable, nggak testable, nggak reliable.

Butuh rewrite total. Pisahin tanggung jawab ke modul-modul kecil.

> 📍 **Lokasi kode (AFTER):**
> - Semua file di `src/` — hasil rewrite modular
> - `src/ai_virtual_mouse.py` → orchestrator tipis (~150 baris main loop saja)
> - Dokumentasi inline: blok `MASALAH #7` di module docstring

---

## Slide 14 — Rewrite Modular

Jadi saya redesign dari awal. Prinsipnya: **satu tanggung jawab, satu modul**.

Empat modul inti:

- **HandTrackingModule**: semua yang berhubungan dengan MediaPipe. Deteksi tangan, ekstrak 21 landmarks, cek jari naik/turun. Modul ini nggak tahu apa-apa soal gesture atau mouse.

- **GestureClassifier**: klasifikasi gestur dari finger state. State machine dengan debounce dan hysteresis. Modul ini nggak perlu tahu koordinat layar atau cara gerakin mouse.

- **CoordinateMapper**: mapping koordinat dari kamera ke layar. Interpolasi linear plus exponential smoothing. Modul ini nggak peduli gestur apa yang lagi aktif.

- **MouseController**: eksekusi action — move, click, drag, scroll. Thin wrapper di atas Autopy. Modul ini cuma terima perintah, nggak tahu dari mana asalnya.

Masing-masing modul terisolasi. Bisa di-test sendiri-sendiri.

> 📍 **Lokasi kode:**
> - `src/hand_tracking_module.py` (273 baris) → class `HandDetector`: `findHands()`, `findPosition()`, `fingersUp()`
> - `src/gesture_classifier.py` (460 baris) → class `GestureClassifier`: `classify()`, `_handle_left_click()`, `reset()`
> - `src/coordinate_mapper.py` (205 baris) → class `CoordinateMapper`: `process()`, `process_drag()`, `smooth()`
> - `src/mouse_controller.py` (150 baris) → class `MouseController`: `execute()`, `_scroll()`, `cleanup()`
> - `src/ai_virtual_mouse.py` (380 baris) → fungsi `main()`: orchestrator, PHASE 1-7 loop

---

## Slide 15 — GestureClassifier Deep Dive

Yang paling signifikan perubahannya ada di GestureClassifier. Bukan cuma if-else biasa.

**Debounce 300ms**: gesture baru harus bertahan 300 milidetik sebelum diakui. Flicker 1-2 frame diabaikan.

**Hysteresis**: batas ON beda sama batas OFF. Contoh klik: ON di 28px, OFF di 38px. Begitu pinch turun di bawah 28px → klik. Begitu pinch naik di atas 38px → baru re-arm. Nggak bakal spam click di boundary.

**Hold-time 100ms**: drag baru aktif setelah kepalan ditahan 100ms. Mencegah drag nggak sengaja pas lagi transisi gesture.

**Hand-lost grace 4 frame**: tangan hilang kurang dari 4 frame? State dipertahankan. Drag nggak putus cuma gara-gara tangan sebentar keluar frame.

**Post-click freeze 200ms**: setelah klik, kursor di-freeze 200ms. Biar nggak drift pas jari refleks gerak setelah pinch.

Ini semua bikin gesture recognition stabil. Bukan cuma "deteksi bener", tapi "transisi antar gesture mulus".

> 📍 **Lokasi kode:**
> - `src/gesture_classifier.py` → class docstring: blok `MASALAH #5, #6, #8`
>   - Debounce 300ms: `_debounce_stable_mode()` — bandingkan `now_ms` dengan `mode_change_ms + 300`
>   - Hysteresis ON≠OFF: `_handle_left_click()` — `LEFT_CLICK_PINCH_ON_PX=28` vs `LEFT_CLICK_PINCH_OFF_PX=38`
>   - Hold-time 100ms: `_handle_left_click()` — `pinch_hold_start_ms + CLICK_HOLD_TIME_MS`
>   - Post-click freeze 200ms: `_freeze_movement()` — set `freeze_until_ms = now_ms + 200`
> - `src/ai_virtual_mouse.py` → `main()`: hand-lost grace — counter `hand_lost_frames >= HAND_LOST_GRACE_FRAMES`

---

## Slide 16 — Hasil Akhir

Hasil akhir: 8 modul, 33 unit tests, 6 gesture stabil, dikerjakan dalam 7 fase.

Dulu: 1 file, 4 gesture, 0 tests.
Sekarang: 8 modul, 6 gesture, 33 tests.

Yang paling penting: kalau ada bug, saya tinggal tes satu modul. Nggak perlu jalanin webcam.

Misal: "GestureClassifier ngasih mode salah?" → run `test_gesture_classifier.py`. 2 detik. Ketauan.

Ini perbedaan fundamental antara kode yang "jalan" dan kode yang "benar dan terverifikasi".

> 📍 **Lokasi kode:**
> - `src/` → 8 modul hasil rewrite (daftar di Slide 14)
> - `tests/` → 33 unit tests
> - `video-version/` → 3 file referensi (versi sederhana, tanpa state management)
> - `presentasi/` → 16 file dokumentasi (.md), termasuk script ini

---

## Slide 17 — Yang Saya Pelajari

Tiga lesson utama dari proyek ini:

**Pertama: Copy-paste bukan akhir.** Tutorial itu starting point. Tapi hampir selalu ada bug yang baru ketemu pas dipakai beneran. Kode tutorial Murtaza bukan kode production — dan itu normal. Justru dengan nemuin dan ngebenerin bug-bug itu, saya belajar jauh lebih banyak.

**Kedua: Struktur kode = UX juga.** User nggak lihat kode. Tapi kualitas UX — drag stabil, click nggak spam — langsung dipengaruhi struktur kode. Debounce dan hysteresis bukan "nice to have", tapi kebutuhan dasar untuk gesture recognition yang reliable. Dan itu cuma bisa diimplementasi dengan benar kalau arsitekturnya mendukung.

**Ketiga: Library bisa mati kapan aja.** MediaPipe Solutions API — yang dipakai di tutorial — dihapus total di versi 0.10.30. Saya harus migrasi ke Tasks API. Ini realita di software engineering: API deprecation is real. Kita harus siap adaptasi.

> 📍 **Lokasi kode:**
> - `video-version/HandTrackingModule.py` → class `HandDetector`: internal pakai Tasks API (`HandLandmarker.create_from_options()`)
> - `src/hand_tracking_module.py` → sama: Tasks API, tidak ada import `mp.solutions`
> - `requirements.txt` → `mediapipe>=0.10.30` (hanya Tasks API yang tersedia di PyPI)

---

## Slide 18 — Terima Kasih

Sekian presentasi dari saya. Ada pertanyaan?

---

## Catatan untuk Presenter

- Kecepatan: santai, natural. Jangan buru-buru.
- Slide 4, 13, 17 adalah titik transisi penting — kasih jeda sedikit sebelum lanjut.
- Kalau ada pertanyaan teknis di tengah, bisa langsung jawab. Slide berikutnya sering kali udah nge-cover jawabannya.
- Backup plan kalau waktu mepet: skip slide 8-9 (rangkuman fine-tuning), langsung dari "gesture kurang lengkap" ke "kenapa masih nggak enak". Atau skip slide 15 (deep dive) kalau audiens udah cukup teknis dan penjelasan di slide 14 udah cukup.
