# Main Version — Gambaran Umum

## Apa ini?

Main version adalah hasil **rewrite total** dari video version. Arsitektur modular: setiap tanggung jawab dipisah ke modul sendiri. Hasil dari proses belajar dan iterasi yang didokumentasikan di video version.

## Kenapa rewrite?

Video version punya 3 masalah fundamental:
1. **Nggak ada state** — flicker 1 frame bikin gesture ganti
2. **Nggak bisa dites** — semua logic campur di satu loop
3. **Nggak scalable** — nambah gesture = rewrite logic

Solusi: pisah tanggung jawab ke modul terpisah. Masing-masing bisa dibangun, dites, dan diubah secara independen.

## Arsitektur

```
Webcam
  │
  ▼
HandDetector ─── deteksi tangan, ekstrak 21 landmarks
  │
  ▼
GestureClassifier ─── klasifikasi gestur + state machine (debounce, hysteresis)
  │
  ├─→ CoordinateMapper ─── mapping kamera → layar + smoothing
  │         │
  │         ▼
  └─→ MouseController ──── eksekusi action (move, click, drag, scroll)
```

## Modul

| Modul | File | Tanggung Jawab |
|---|---|---|
| HandDetector | `hand_tracking_module.py` | Deteksi tangan, ekstrak landmarks, cek jari |
| GestureClassifier | `gesture_classifier.py` | Klasifikasi gestur, state machine, debounce |
| CoordinateMapper | `coordinate_mapper.py` | Mapping koordinat + smoothing |
| MouseController | `mouse_controller.py` | Eksekusi action mouse |
| Config | `config.py` | Semua konstanta + parameter |
| GestureProfiles | `gesture_profiles.py` | Definisi pola gesture (bisa ganti profile) |
| Utils | `utils.py` | FPS counter, mode overlay, bounding box |
| Main | `ai_virtual_mouse.py` | Main loop, integrasi semua modul |

## Cara jalanin

```bash
pip install -r requirements.txt
python src/ai_virtual_mouse.py
```

## Apa yang bikin versi ini lebih baik?

| Aspek | Video Version | Main Version |
|---|---|---|
| Debounce | ❌ | ✅ 300ms |
| Hysteresis | ❌ | ✅ ON/OFF thresholds |
| Hold-time | ❌ | ✅ 100ms untuk click |
| Post-click freeze | ❌ | ✅ 200ms |
| Hand-lost grace | ❌ | ✅ 4 frame |
| Unit tests | 0 | 33 |
| Gesture profiles | Hardcoded | Switchable (legacy / practical_no_thumb) |
| Thumb detection | x-coordinate | Distance-based + sensitivity tuning |
| Modular | 2 files | 8 modules |
| Scroll | Windows-only ctypes | Autopy + Windows fallback |
