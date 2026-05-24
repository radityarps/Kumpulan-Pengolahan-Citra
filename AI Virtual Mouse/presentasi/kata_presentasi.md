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

---

## Slide 6 — Masalah #2: Kursor Kebalik

Masalah kedua lebih subtle: kursor geraknya kebalik.

Saya gerakin tangan ke kanan, kursor malah ke kiri. Setelah debugging, ketemu penyebabnya: webcam itu mirror. Gambar yang kita lihat di layar itu kebalikan dari aslinya. Tutorial pakai rumus `wScr - clocX` buat nge-balikin — tapi di setup saya, itu malah bikin double-inversion.

Solusinya: `cv2.flip(img, 1)`. Satu baris. Mirror gambar dari webcam, terus koordinat langsung dipakai apa adanya — nggak perlu di-invert lagi. Hasilnya: tangan kiri = layar kiri. Natural.

---

## Slide 7 — Masalah #3: Jempol Unreliable

Masalah ketiga: jempol.

Cara tutorial deteksi jempol itu dengan x-coordinate: "kalau ujung jempol lebih kanan dari sendinya, berarti naik". Ini cuma berfungsi buat tangan kanan yang telapaknya menghadap kamera.

Begitu kita pakai tangan kiri — atau tangan diputar sedikit — deteksinya ngaco. Kadang jempol kebaca naik padahal turun, atau sebaliknya. Gesture jadi unreliable.

Solusi paling pragmatis: abaikan jempol. Di semua gesture pattern, jempol kita kasih nilai `None` — alias wildcard. Jadi classifier cuma lihat 4 jari: telunjuk, tengah, manis, kelingking. Solusi simpel, tapi efektif.

---

## Slide 8 — Gesture Kurang Lengkap

Setelah tiga bug diperbaiki, saya lihat gesture-nya masih kurang.

Tutorial cuma punya 4 gesture: Move, Left Click, Right Click, Scroll. Itu pun right click pakai 5 jari naik semua — susah dan nggak natural. Scroll masih broken.

Saya tambah 2 gesture lagi dan perbaiki yang ada: Drag (buat drag-and-drop file) dan perbaikan Scroll. Right click diganti dari 5 jari jadi 3 jari (telunjuk, tengah, manis) + pinch antara telunjuk dan jari manis.

Sekarang total 6 gesture: Move, Left Click, Right Click, Drag, Scroll — dengan gesture yang lebih natural.

---

## Slide 9 — Rangkuman Fine-Tuning

Jadi total ada 8 perbaikan di fase fine-tuning ini: scroll beneran, kamera mirror, jempol diabaikan, right click diperbaiki, drag ditambahin, click logic dari spam jadi edge-triggered, threshold dituning (28px buat click, 34px buat right click), dan scroll pakai camera center boundary.

Setelah semua perbaikan ini, kode udah jalan lebih baik. Gesture lebih lengkap, lebih natural. Saya pikir: "OK, selesai."

Tapi pas saya pakai beneran sehari-hari... masih ada masalah.

---

## Slide 10 — Kenapa Masih Nggak Enak?

Coba bayangin: saya lagi drag file. Kepalan sedikit kendor karena jari reflek gerak — langsung drag putus, file ke-drop di tempat acak.

Atau: lagi mode Move, tiba-tiba satu frame flicker, langsung ganti ke mode Click. Kursor berhenti, nge-klik sesuatu yang nggak dimaksud.

Atau: pas lagi klik, setiap frame nge-klik lagi dan lagi. Spam click. Karena satu frame pinch-nya masih di bawah threshold, langsung trigger lagi.

Semua masalah ini bukan salah gesture-nya. Bukan salah kameranya. Ini salah struktur kodenya.

---

## Slide 11 — Akar Masalah: Nggak Ada "State"

Akar masalahnya: setiap frame diproses sendiri-sendiri.

Frame 1: "Oh, ini gesture Drag." → OK.
Frame 2: Satu frame flicker, jari sedikit berubah → "Oh, ini bukan gesture apa-apa." → Mode ganti.

Kode nggak ingat apa yang terjadi di frame sebelumnya. Nggak ada memori. Nggak ada "state".

Solusinya butuh tiga hal: debounce (harus stabil beberapa frame dulu sebelum ganti gesture), hysteresis (batas buat ON beda sama batas OFF, jadi nggak bolak-balik di threshold), dan state machine (ingat gesture sebelumnya, tahu konteks transisinya).

---

## Slide 12 — Plus: Nggak Bisa Dites

Masalah struktural kedua: kode nggak bisa dites.

Semua logic — deteksi tangan, klasifikasi gestur, mapping koordinat, kontrol mouse, FPS counter — semua dalam satu main loop, satu file yang sama.

Mau ganti threshold? Edit kode, tes manual sambil liat webcam. Mau yakin gesture classifier-nya bener? Nggak bisa unit test. Harus gerakin tangan beneran di depan kamera. Mau tambah gesture? Bisa ngerusak logic yang lain karena semuanya interdependent.

Ini bukan cuma masalah kenyamanan ngoding. Ini masalah correctness. Saya sebagai developer nggak bisa buktikan kode saya benar tanpa tes.

---

## Slide 13 — Insight

Di titik ini, saya sadar:

**"Masalahnya bukan di gesture-nya. Masalahnya di struktur kodenya."**

Kode yang saya tulis — walaupun gesture-nya udah diperbaiki — arsitekturnya salah. Single-loop monolithic nggak scalable, nggak testable, nggak reliable.

Butuh rewrite total. Pisahin tanggung jawab ke modul-modul kecil.

---

## Slide 14 — Rewrite Modular

Jadi saya redesign dari awal. Prinsipnya: **satu tanggung jawab, satu modul**.

Empat modul inti:

- **HandTrackingModule**: semua yang berhubungan dengan MediaPipe. Deteksi tangan, ekstrak 21 landmarks, cek jari naik/turun. Modul ini nggak tahu apa-apa soal gesture atau mouse.

- **GestureClassifier**: klasifikasi gestur dari finger state. State machine dengan debounce dan hysteresis. Modul ini nggak perlu tahu koordinat layar atau cara gerakin mouse.

- **CoordinateMapper**: mapping koordinat dari kamera ke layar. Interpolasi linear plus exponential smoothing. Modul ini nggak peduli gestur apa yang lagi aktif.

- **MouseController**: eksekusi action — move, click, drag, scroll. Thin wrapper di atas Autopy. Modul ini cuma terima perintah, nggak tahu dari mana asalnya.

Masing-masing modul terisolasi. Bisa di-test sendiri-sendiri.

---

## Slide 15 — GestureClassifier Deep Dive

Yang paling signifikan perubahannya ada di GestureClassifier. Bukan cuma if-else biasa.

**Debounce 300ms**: gesture baru harus bertahan 300 milidetik sebelum diakui. Flicker 1-2 frame diabaikan.

**Hysteresis**: batas ON beda sama batas OFF. Contoh klik: ON di 28px, OFF di 38px. Begitu pinch turun di bawah 28px → klik. Begitu pinch naik di atas 38px → baru re-arm. Nggak bakal spam click di boundary.

**Hold-time 100ms**: drag baru aktif setelah kepalan ditahan 100ms. Mencegah drag nggak sengaja pas lagi transisi gesture.

**Hand-lost grace 4 frame**: tangan hilang kurang dari 4 frame? State dipertahankan. Drag nggak putus cuma gara-gara tangan sebentar keluar frame.

**Post-click freeze 200ms**: setelah klik, kursor di-freeze 200ms. Biar nggak drift pas jari refleks gerak setelah pinch.

Ini semua bikin gesture recognition stabil. Bukan cuma "deteksi bener", tapi "transisi antar gesture mulus".

---

## Slide 16 — Hasil Akhir

Hasil akhir: 8 modul, 33 unit tests, 6 gesture stabil, dikerjakan dalam 7 fase.

Dulu: 1 file, 4 gesture, 0 tests.
Sekarang: 8 modul, 6 gesture, 33 tests.

Yang paling penting: kalau ada bug, saya tinggal tes satu modul. Nggak perlu jalanin webcam.

Misal: "GestureClassifier ngasih mode salah?" → run `test_gesture_classifier.py`. 2 detik. Ketauan.

Ini perbedaan fundamental antara kode yang "jalan" dan kode yang "benar dan terverifikasi".

---

## Slide 17 — Yang Saya Pelajari

Tiga lesson utama dari proyek ini:

**Pertama: Copy-paste bukan akhir.** Tutorial itu starting point. Tapi hampir selalu ada bug yang baru ketemu pas dipakai beneran. Kode tutorial Murtaza bukan kode production — dan itu normal. Justru dengan nemuin dan ngebenerin bug-bug itu, saya belajar jauh lebih banyak.

**Kedua: Struktur kode = UX juga.** User nggak lihat kode. Tapi kualitas UX — drag stabil, click nggak spam — langsung dipengaruhi struktur kode. Debounce dan hysteresis bukan "nice to have", tapi kebutuhan dasar untuk gesture recognition yang reliable. Dan itu cuma bisa diimplementasi dengan benar kalau arsitekturnya mendukung.

**Ketiga: Library bisa mati kapan aja.** MediaPipe Solutions API — yang dipakai di tutorial — dihapus total di versi 0.10.30. Saya harus migrasi ke Tasks API. Ini realita di software engineering: API deprecation is real. Kita harus siap adaptasi.

---

## Slide 18 — Terima Kasih

Sekian presentasi dari saya. Ada pertanyaan?

---

## Catatan untuk Presenter

- Kecepatan: santai, natural. Jangan buru-buru.
- Slide 4, 13, 17 adalah titik transisi penting — kasih jeda sedikit sebelum lanjut.
- Kalau ada pertanyaan teknis di tengah, bisa langsung jawab. Slide berikutnya sering kali udah nge-cover jawabannya.
- Backup plan kalau waktu mepet: skip slide 8-9 (rangkuman fine-tuning), langsung dari "gesture kurang lengkap" ke "kenapa masih nggak enak". Atau skip slide 15 (deep dive) kalau audiens udah cukup teknis dan penjelasan di slide 14 udah cukup.
