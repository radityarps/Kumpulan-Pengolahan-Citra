# ai_virtual_mouse.py — Penjelasan untuk Pemula

## Tujuan

Main loop — file yang dijalankan. Mengintegrasikan semua modul: HandDetector → GestureClassifier → CoordinateMapper → MouseController. Jauh lebih bersih dari video version karena logic udah didelegasikan ke modul masing-masing.

## Kenapa Kode Ditulis Begini?

### Kenapa main loop tetap satu file?

Karena main loop adalah **orchestrator** — dia nggak berisi logic, cuma memanggil modul dalam urutan yang benar. Ini design pattern yang disebut **coordinator**. Bedakan dengan video version yang semua logic di satu file.

### Kenapa import pakai `sys.path.insert`?

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

Ini trik supaya script bisa dijalankan dari mana aja — baik dari folder `src/` langsung, maupun dari project root dengan `python src/ai_virtual_mouse.py`. Tanpa ini, `from src.config import ...` bakal gagal karena Python nggak tahu `src` itu package.

### Kenapa hand-lost grace di-handle di main loop?

Kalau tangan hilang beberapa frame, kita nggak langsung reset GestureClassifier dan CoordinateMapper. Kita tunggu `HAND_LOST_GRACE_FRAMES` (4 frame). Ini memberi toleransi untuk momentary loss (kedip, tangan gerak cepat).

Kalau tangan beneran hilang lebih dari 4 frame, baru kita reset semua state dan lepas drag.

## Flow Main Loop

```
while True:
    1. cap.read()                    # Ambil frame
    2. cv2.flip(img, 1)              # Mirror
    3. detector.findHands(img)       # Deteksi tangan
    4. detector.findPosition(img)    # Ekstrak landmarks

    5. if tangan terdeteksi:
         fingers = detector.fingersUp()
         classifier.classify()        # Klasifikasi gestur
         if action == "drag_start":
             mapper.set_drag_anchor() # Catat anchor
         if mode == "Drag":
             mapper.process_drag()    # Koordinat relatif
         else:
             mapper.process()         # Koordinat absolut
         controller.execute("move")   # Gerakin kursor
       else:
         hand_lost_frames += 1
         if hand_lost_frames >= 4:
             reset semua

    6. controller.execute(action)     # Click, scroll, drag_start/end

    7. utils.put_fps()               # Overlay FPS
    8. utils.put_mode_text()         # Overlay mode

    9. cv2.imshow()                  # Tampilkan
   10. cv2.waitKey(1)                # Cek keyboard (q=quit, l=toggle)
```

## Perbedaan Utama dari Video Version

| Aspek | Video Version | Main Version |
|---|---|---|
| Logic gesture | if-elif block 50+ baris | `classifier.classify()` — 1 baris |
| Mapping koordinat | `np.interp()` inline + smoothing manual | `mapper.process()` — 1 baris |
| Kontrol mouse | `autopy.mouse.xxx()` langsung | `controller.execute()` — 1 baris |
| Debug info | `cv2.putText()` inline | `utils.put_fps()` + `utils.put_mode_text()` |
| Drag anchor | Variable di main loop | `mapper.set_drag_anchor()` |
| Hand lost handling | Reset langsung | Grace period 4 frame |
| Keyboard handler | Cuma 'q' | 'q' + 'l' (toggle landmarks) |
| Debug finger state | Sederhana | Detail: per-jari, pattern matching status |

## Kenapa ada dua debug mode?

- `DEBUG_FINGERS`: tampilkan state jari `[1, 1, 0, 0, 0]` dan status pattern matching
- `DEBUG_ACTION`: tampilkan aksi terakhir yang di-trigger

Berguna untuk debugging gesture — bisa lihat real-time apakah finger detection berfungsi dengan benar.

## Istilah Teknis

- **Orchestrator / Coordinator:** komponen yang mengatur alur kerja modul-modul lain, tanpa berisi business logic sendiri.
- **sys.path.insert:** memodifikasi Python module search path. Biar `import` bisa menemukan package `src/` dari berbagai working directory.
- **Grace period:** toleransi waktu/frame sebelum mengambil tindakan. Di sini: toleransi sebelum reset state saat tangan hilang.
- **Toggle landmarks:** fitur 'l' untuk menyembunyikan/menampilkan overlay landmark. Berguna untuk presentasi atau screenshot tanpa clutter.
