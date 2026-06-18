# Naskah Presentasi Peer Tutoring AI Virtual Mouse

Presenter: Raditya Rafif Pratama Sasmita  
Institusi: Politeknik Negeri Semarang  
Format: Peer tutoring / narasumber  
Topik: AI Virtual Mouse - dari webcam ke cursor  

Catatan penggunaan:
- Naskah ini dibuat untuk dibaca secara natural, bukan dihafal kata per kata.
- Istilah teknis seperti MediaPipe Tasks, debounce, runtime, dan benchmark tetap dipakai jika lebih jelas sebagai istilah proyek.
- Bagian "Tunjukkan" mengarah ke file atau kode yang bisa dibuka saat demo.

## Slide 1 - AI Virtual Mouse: Dari Webcam ke Cursor

Selamat siang, perkenalkan saya Raditya Rafif Pratama Sasmita dari Politeknik Negeri Semarang. Pada sesi ini saya akan menjelaskan proyek AI Virtual Mouse dari sudut pandang teknis, tetapi tetap dengan gaya peer tutoring.

Fokusnya bukan hanya memperlihatkan demo cursor bergerak dengan tangan, tetapi membedah bagaimana alurnya bekerja: mulai dari kamera, deteksi landmark tangan, pembacaan gesture, sampai sistem memutuskan kapan cursor bergerak dan kapan klik terjadi.

## Slide 2 - Tujuan Belajar

Beberapa hal yang ingin saya capai dalam sesi ini. Pertama, kita samakan dulu pemahaman tentang OpenCV dan MediaPipe, karena dua library ini punya peran yang berbeda.

Kedua, kita akan lihat alur sistem dari frame kamera sampai menjadi target cursor dan event klik. Ketiga, kita bandingkan baseline tutorial-style dengan improved pipeline.

Terakhir, saya akan tunjukkan bagian kode yang menyebabkan masalah pada baseline dan bagaimana logika improved version memperbaikinya melalui debounce dan pipeline yang lebih terstruktur.

## Slide 3 - Fondasi Tool: OpenCV dan MediaPipe

OpenCV di proyek ini berperan sebagai lapisan computer vision untuk membaca webcam, mengambil frame, menggambar overlay, dan menampilkan window demo. Jadi OpenCV membantu sistem melihat dan menampilkan gambar.

MediaPipe berbeda perannya. MediaPipe dipakai untuk memahami posisi tangan. Output pentingnya adalah hand landmarks, yaitu titik-titik koordinat pada tangan. Dalam proyek ini, landmark seperti ujung jari telunjuk dan ujung jari tengah sangat penting untuk menentukan gerakan dan klik.

Tunjukkan bila perlu:
- `src/ai_virtual_mouse_experimental/hand_tracker.py`
- `src/video version/AiVirtualMouseProject.py`

## Slide 4 - MediaPipe Solutions dan Tasks

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/ai_virtual_mouse_experimental/hand_tracker.py` | `class HandTracker`, `class HandTrackingResult`, `_setup_backend` | MediaPipe Tasks prioritas, Solutions fallback, output tracking. |
| `src/video version/HandTrackingModule.py` | `class handDetector`, `findHands`, `findPosition`, `fingersUp`, `findDistance` | Pembanding baseline tracker. |


Pada baseline tutorial awal, pendekatannya mengikuti gaya MediaPipe Solutions. API ini populer karena mudah dipakai untuk prototype cepat. Kita bisa menggunakan `mp.solutions.hands.Hands`, membaca landmark, lalu langsung membuat logika gesture.

Pada improved prototype, sistem diarahkan ke MediaPipe Tasks, khususnya HandLandmarker dengan model `.task`. Tasks lebih eksplisit sebagai backend, dan lebih cocok untuk desain eksperimental karena backend yang dipakai bisa dicatat dalam metadata.

Tetapi penting: berpindah dari Solutions ke Tasks bukan otomatis membuat klik stabil. Stabilitas klik datang dari logika pipeline, terutama stable pinch, debounce, release state, dan cooldown.

Kalimat kunci untuk audiens: backend membantu deteksi landmark, tetapi kualitas interaksi ditentukan oleh logika event setelah landmark dibaca.

Tunjukkan:
- `src/ai_virtual_mouse_experimental/hand_tracker.py`
- bagian `_setup_tasks_backend`
- bagian `_setup_solutions_backend`

## Slide 5 - Alur Sistem dari Kamera ke Cursor

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/ai_virtual_mouse_experimental/real_mouse_runtime.py` | `run_real_mouse_runtime`, `cv2.VideoCapture(...)`, `cap.read()` | Webcam dibuka dan frame dibaca. |
| `src/ai_virtual_mouse_experimental/real_mouse_runtime.py` | `pipeline.process_frame(image)`, `mouse.move(...)`, `mouse.click()` | Frame masuk pipeline sebelum jadi mouse action. |


Alur sistemnya bisa dibaca sebagai pipeline. Pertama, webcam membaca frame menggunakan OpenCV. Kedua, frame itu masuk ke HandTracker untuk mendeteksi 21 landmark tangan.

Ketiga, landmark diterjemahkan menjadi gesture, misalnya move, click, pause, atau idle. Keempat, posisi ujung telunjuk dipetakan dari koordinat kamera ke koordinat output, bisa layar asli atau window benchmark.

Kelima, smoothing diterapkan supaya cursor tidak terlalu patah-patah. Baru setelah itu runtime menentukan efek akhirnya: pada real mouse runtime output bisa menggerakkan OS cursor, sedangkan pada benchmark runtime output hanya menggerakkan simulated cursor.

Tunjukkan:
- `src/ai_virtual_mouse_experimental/hand_control_pipeline.py`
- method `process_frame`

## Slide 6 - Model Gesture yang Dipakai

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/ai_virtual_mouse_experimental/gesture_engine.py` | `GestureInput`, `GestureResult`, `classify_simple_real_mouse_gesture`, `is_pinching` | Model gesture: pause, move, click, idle. |
| `src/ai_virtual_mouse_experimental/hand_control_pipeline.py` | `hand_input_from_tracking` | `fingers_up` dari tracker diubah menjadi `GestureInput`. |


Gesture utama yang dipakai sederhana. Untuk move, hanya jari telunjuk yang aktif. Untuk click, baseline memakai kombinasi telunjuk dan jari tengah, lalu mengecek jarak antar ujung jari.

Pada improved version, click tidak langsung dieksekusi hanya karena jarak pinch kecil. Pinch harus stabil dulu, lalu melewati debounce. Setelah satu klik keluar, sistem menunggu release sebelum boleh klik lagi.

Ada juga pause gesture menggunakan telapak terbuka. Ini penting karena ketika sistem mengendalikan cursor, pengguna perlu cara cepat untuk menghentikan kontrol sementara.

## Slide 7 - Prototype Baseline

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/video version/AiVirtualMouseProject.py` | import `time`, `autopy`, `cv2`, `HandTrackingModule`, `numpy` | Dependency baseline asli. |
| `src/video version/AiVirtualMouseProject.py` | `cv2.VideoCapture(0)`, `detector = htm.handDetector(maxHands=1)`, `autopy.screen.size()`, `while True`, `cap.read()` | Kamera, detector, layar, dan loop baseline ada dalam satu file. |


Baseline adalah versi tutorial-style. Kodenya relatif langsung: baca kamera, deteksi tangan, cek jari mana yang aktif, lalu gerakkan mouse atau klik.

Untuk gerak cursor, baseline memakai jari telunjuk. Koordinat dari kamera dipetakan ke ukuran layar menggunakan interpolasi, lalu diberi smoothing sederhana.

Untuk klik, baseline melihat apakah jari telunjuk dan jari tengah aktif. Jika jarak keduanya kurang dari threshold, maka mouse click langsung dipanggil. Desain ini mudah dipahami, tetapi belum cukup aman untuk interaksi yang stabil.

Tunjukkan:
- `src/video version/AiVirtualMouseProject.py`
- bagian movement mode dan clicking mode

## Slide 8 - Masalah Kode pada Baseline

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/video version/AiVirtualMouseProject.py` | `np.interp`, `clocX`, `clocY`, `autopy.mouse.move(...)` | Mapping cursor baseline. |
| `src/video version/AiVirtualMouseProject.py` | `if fingers[1] == 1 and fingers[2] == 1`, `findDistance(8, 12, img)`, `if length < 40: autopy.mouse.click()` | Kode bermasalah: click langsung tanpa debounce/cooldown. |
| `src/video version/HandTrackingModule.py` | `findDistance` | Helper jarak dua landmark. |


Masalah utama baseline ada pada cara event klik dibuat. Kode click berada langsung di dalam loop frame. Jika jarak pinch kurang dari 40, sistem langsung memanggil `autopy.mouse.click()`.

Karena kamera berjalan banyak frame per detik, satu pinch yang ditahan bisa memenuhi kondisi itu di banyak frame berturut-turut. Akibatnya satu niat klik bisa berubah menjadi banyak click event.

Jadi bug utamanya bukan semata-mata MediaPipe salah mendeteksi tangan. Bug utamanya adalah event generation yang terlalu sensitif: tidak ada debounce, tidak ada syarat stable frame, tidak ada release-before-next-click, dan tidak ada cooldown.

Tunjukkan:
- `src/video version/AiVirtualMouseProject.py`, sekitar baris 64-71

## Slide 9 - Improved Pipeline: Apa yang Diubah

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/ai_virtual_mouse_experimental/hand_control_pipeline.py` | `class HandControlPipeline`, `class HandControlFrame` | Pipeline per frame dan output `cursor_target`, `click_fired`, `paused`. |
| `src/ai_virtual_mouse_experimental/gesture_engine.py` | `classify_simple_real_mouse_gesture`, `update_click_debounce` | Gesture eksplisit dan click harus valid dulu. |


Improved version memperbaiki proyek bukan hanya dengan mengganti backend, tetapi dengan merapikan arsitektur kontrol.

Pertama, hand tracking disatukan dalam `HandTracker`, dengan MediaPipe Tasks sebagai prioritas dan Solutions sebagai fallback. Kedua, alur kontrol dipusatkan di `HandControlPipeline`, sehingga gesture, mapping, smoothing, debounce, pause, safety, dan metrics berada dalam satu pipeline.

Ketiga, click dibuat lebih stabil melalui stable pinch dan debounce. Ini yang langsung berkaitan dengan penurunan false clicks pada hasil benchmark.

Tunjukkan:
- `src/ai_virtual_mouse_experimental/hand_tracker.py`
- `src/ai_virtual_mouse_experimental/hand_control_pipeline.py`
- `src/ai_virtual_mouse_experimental/gesture_engine.py`

## Slide 10 - Arsitektur Kode

**Kode yang ditunjukkan di awal narasi:**

| Layer | File path | Kode/Fungsi |
|---|---|---|
| Runtime | `src/ai_virtual_mouse_experimental/real_mouse_runtime.py` | `run_real_mouse_runtime`, `_create_mouse_controller` |
| Tracking | `src/ai_virtual_mouse_experimental/hand_tracker.py` | `HandTracker`, `HandTrackingResult` |
| Gesture | `src/ai_virtual_mouse_experimental/gesture_engine.py` | `GestureInput`, `GestureResult`, `classify_simple_real_mouse_gesture` |
| Pipeline | `src/ai_virtual_mouse_experimental/hand_control_pipeline.py` | `HandControlPipeline`, `HandControlFrame` |
| Mapping | `src/ai_virtual_mouse_experimental/cursor_mapping.py` | `map_point_to_output`, `apply_smoothing` |


Ada beberapa file utama yang bisa dipakai untuk memahami arsitektur improved version.

`hand_tracker.py` bertugas memilih backend MediaPipe, menjalankan deteksi tangan, dan mengembalikan landmarks.

`gesture_engine.py` bertugas mengubah status jari dan jarak pinch menjadi hasil gesture.

`hand_control_pipeline.py` menggabungkan semua tahap: tracking, gesture, mapping, smoothing, debounce, pause, safety, dan technical metrics.

`benchmark_shell.py` menjalankan benchmark Pygame dan menerapkan output pipeline ke simulated cursor. `benchmark_grid.py` menyimpan logika target, hit, false click, dan completion time.

Kalau audiens ingin membaca kode, lima file ini adalah peta utamanya.

## Slide 11 - Logika Debounce

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/ai_virtual_mouse_experimental/gesture_engine.py` | `ClickDebounceConfig`, `ClickDebounceState`, `ClickDebounceResult` | Konfigurasi, state, dan output debounce. |
| `src/ai_virtual_mouse_experimental/gesture_engine.py` | `update_click_debounce`, `stable`, `cooldown_elapsed`, `armed`, `released_frames` | Click hanya keluar jika stabil, armed, cooldown lewat, dan perlu release. |


Debounce adalah bagian penting dari improved version. Pada baseline, click bersifat frame-based: selama kondisi click benar di frame saat itu, klik bisa keluar.

Pada improved version, sistem menyimpan state. Pertama, pinch harus aktif selama sejumlah frame, misalnya dua frame. Kedua, sistem harus dalam keadaan armed. Ketiga, cooldown harus sudah lewat.

Jika semua syarat terpenuhi, sistem memancarkan satu click event, lalu armed menjadi false. Setelah itu pengguna harus melepas pinch selama beberapa frame sebelum sistem siap klik lagi.

Jadi debounce mengubah logika dari "setiap frame bisa klik" menjadi "satu gesture stabil menghasilkan satu klik".

Tunjukkan:
- `src/ai_virtual_mouse_experimental/gesture_engine.py`
- `ClickDebounceConfig`
- `update_click_debounce`

## Slide 12 - Keamanan pada Konteks Runtime

**Kode yang ditunjukkan di awal narasi:**

| File path | Kode/Fungsi | Fokus |
|---|---|---|
| `src/ai_virtual_mouse_experimental/real_mouse_runtime.py` | `run_real_mouse_runtime`, `_create_mouse_controller`, `autopy.mouse.move`, `autopy.mouse.click` | Runtime menyentuh mouse OS sungguhan. |
| `src/ai_virtual_mouse_experimental/real_mouse_runtime.py` | `not frame_result.paused`, `if frame_result.click_fired`, `cv2.waitKey(1)`, `ord("q")` | Safety: pause, click final, safe quit. |
| `src/ai_virtual_mouse_experimental/gesture_engine.py` | `is_open_palm`, `_pause_result` | Open palm sebagai pause gesture. |


Proyek ini punya dua konteks runtime yang harus dibedakan.

Real Mouse Runtime adalah mode yang dapat menggerakkan cursor sistem operasi. Karena efeknya langsung ke desktop, mode ini perlu kontrol keamanan seperti pause gesture dan safe quit.

Benchmark Runtime berbeda. Benchmark memakai Pygame simulated cursor. Artinya, sistem tetap membaca input tangan, tetapi outputnya diarahkan ke cursor simulasi di window Pygame, bukan ke mouse asli.

Ini penting untuk eksperimen, karena kita bisa mengukur performa kontrol tangan tanpa mengambil alih komputer pengguna.

Tunjukkan:
- `src/ai_virtual_mouse_experimental/benchmark_shell.py`
- fungsi `apply_hand_frame_to_benchmark`

## Slide 13 - Metode Benchmark

Benchmark yang dipakai adalah point-and-click benchmark. Sistem membuat target pada grid di Pygame. Pengguna menggerakkan simulated cursor ke target, lalu melakukan click gesture.

Sebuah click dihitung hit jika jaraknya dari pusat target masih dalam radius target. Jika click terjadi di luar radius target, itu dihitung sebagai false click. Target tidak maju sampai ada hit yang benar.

Completion time dihitung dari awal trial sampai target berhasil diklik. Dari setiap trial, sistem bisa menghitung hit rate, false clicks, total clicks, completion time, dan metrik teknis seperti jitter.

Jadi kesimpulan eksperimen berasal dari aturan hit/miss yang eksplisit, bukan hanya dari impresi saat demo.

Tunjukkan:
- `src/ai_virtual_mouse_experimental/benchmark_grid.py`
- fungsi `register_click`
- fungsi `summarize_benchmark`

## Slide 14 - Hasil dan Klaim

**Kode dan docs benchmark yang ditunjukkan di awal narasi:**

| File path | Kode/Dokumen | Fokus |
|---|---|---|
| `src/ai_virtual_mouse_experimental/benchmark_shell.py` | mode benchmark, compare sessions | Entry point benchmark baseline vs improved. |
| `src/ai_virtual_mouse_experimental/benchmark_grid.py` | `generate_grid_targets(settings)`, `register_click` | Target grid, hit, false click. |
| `src/ai_virtual_mouse_experimental/benchmark_report.py` | `compute_metrics` | Hit rate, false clicks, total clicks. |
| `docs/Presentation/presentation_demo_code_ai_virtual_mouse.md` | bagian perbandingan benchmark baseline vs improved | Bukti angka hasil benchmark. |

| Metrik | Baseline | Improved |
|---|---:|---:|
| Hit rate | `100%` | `100%` |
| False clicks | `192,8` | `4,2` |
| Total clicks | `212,8` | `24,2` |


Eksperimen membandingkan lima sesi baseline hand-input dan lima sesi improved hand-input. Keduanya mencapai hit rate 100 persen, artinya kedua kondisi sama-sama bisa menyelesaikan target.

Perbedaan paling besar ada pada klik tidak disengaja. Baseline rata-rata menghasilkan 192.8 false clicks, sedangkan improved rata-rata hanya 4.2 false clicks.

Total clicks juga turun dari 212.8 menjadi 24.2. Namun improved tidak lebih cepat rata-rata, karena completion time baseline 3.085 detik dan improved 4.963 detik. Ada satu session improved yang menjadi outlier, jadi kita tidak boleh mengklaim improved selalu lebih cepat.

Klaim yang aman: improved pipeline sangat mengurangi unintended clicks sambil mempertahankan target acquisition success.

## Slide 15 - Ringkasan Pembelajaran

Ada tiga pembelajaran utama dari proyek ini.

Pertama, AI Virtual Mouse bukan hanya masalah mendeteksi tangan. Setelah landmark didapat, masih ada mapping, gesture logic, state control, smoothing, dan safety.

Kedua, baseline tutorial bagus untuk memulai, tetapi raw click di dalam frame loop rawan menghasilkan false clicks.

Ketiga, improved pipeline menunjukkan bahwa real-time interaction membutuhkan state machine sederhana seperti debounce, bukan hanya threshold jarak jari.

Untuk pengembangan berikutnya, proyek ini bisa diperluas dengan lebih banyak partisipan, sesi lebih panjang, evaluasi drag dan scroll, studi calibration, dan statistical testing.

## Slide 16 - Terima Kasih

Terima kasih. Jika ada pertanyaan, saya bisa menunjukkan tiga bagian kode utama: bug klik pada baseline, logika debounce pada improved version, atau cara benchmark menghitung hit dan false click.

Saya juga bisa menjalankan demo singkat untuk menunjukkan perbedaan antara cara berpikir baseline dan improved pipeline.
