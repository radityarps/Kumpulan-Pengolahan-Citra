# AI Virtual Mouse — Proyek Computer Vision

Proyek **AI Virtual Mouse** menggunakan OpenCV dan MediaPipe untuk mendeteksi tangan dan mengontrol kursor mouse secara *touchless* melalui gestur tangan. Proyek ini mengimplementasikan video tutorial dari kanal **Murtaza's Workshop - Robotics and AI** ([YouTube](https://youtu.be/8gPONnGIPgw)).

## 📁 Struktur Folder

```
AI Virtual Mouse/
├── README.md                     ← File ini
├── article/                      ← Artikel ilmiah
│   └── 00_structure.md           ← Struktur/outline artikel
├── literature/                   ← Daftar literatur
│   ├── 00_literature_review.md   ← Literatur terkurasi dan review
│   ├── papers/                   ← PDF paper referensi utama
│   └── bibtex/                   ← File BibTeX (.bib)
│       └── references.bib
├── src/                          ← Kode sumber (akan diisi nanti)
├── docs/                         ← Dokumentasi riset
│   └── project_research.md       ← Hasil riset proyek dari video tutorial
└── Panduan/                      ← Referensi dari dosen
    ├── Pan et al. - 2026 - YOLO-ECN.pdf  ← Contoh artikel ilmiah
    └── Pembagian Projek IK 3C.docx
```

## 🚀 Teknologi yang Digunakan

- **Python 3**, **OpenCV**, **MediaPipe** (hand tracking)
- **NumPy** (interpolasi koordinat), **Autopy** (kontrol mouse)
- Modul custom **HandTrackingModule** (dibangun bertahap oleh Murtaza)

## 📚 Referensi Utama

1. **MediaPipe Hands: On-device Real-time Hand Tracking** — Zhang et al. (2020) [arXiv:2006.10214]
2. **A Real-time Hand Gesture Recognition and Human-Computer Interaction System** — Pei Xu (2017) [arXiv:1704.07296]

Lihat `literature/00_literature_review.md` untuk daftar lengkap.

## 📝 Artikel Ilmiah

Outline artikel → `article/00_structure.md`

## 🛠️ Cara Menjalankan (nanti setelah implementasi)

```bash
# Instal dependensi
pip install opencv-python mediapipe numpy autopy

# Jalankan program
python src/ai_virtual_mouse.py
```
