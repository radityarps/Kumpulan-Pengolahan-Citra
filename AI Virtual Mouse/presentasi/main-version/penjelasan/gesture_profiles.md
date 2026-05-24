# gesture_profiles.py — Penjelasan untuk Pemula

## Tujuan

Menyimpan definisi pola jari untuk setiap gesture. Memungkinkan ganti gaya gesture tanpa ubah kode classifier.

## Kenapa Kode Ditulis Begini?

### Kenapa gesture dipisah dari classifier?

Video version: pola gesture hardcoded di if-elif block. `if fingers == [None, 1, 0, 0, 0]:` — ini cuma bisa satu gaya gesture.

Main version: pola gesture di file terpisah. Mau ganti gaya? Tinggal ganti `GESTURE_STYLE` di config. Classifier nggak perlu diubah.

### Kenapa ada dua profile?

**`legacy`:** pola asli tutorial. Move = `[0,1,1,0,0]` (jempol+tunjuk naik). Right click = `[1,1,0,0,0]`. Profile ini disimpan untuk backward compatibility.

**`practical_no_thumb`:** pola yang dipakai sekarang. Semua gesture abaikan jempol (`None` wildcard). Lebih robust karena jempol unreliable.

## Struktur Profile

Setiap profile adalah dictionary dengan key:

| Key | Artinya | Contoh (`practical_no_thumb`) |
|---|---|---|
| `move_patterns` | Pola jari untuk Move | `([None, 1, 0, 0, 0],)` |
| `stop_pattern` | Pola jari untuk stop (mode None) | `None` (tidak dipakai) |
| `click_pattern` | Pola jari untuk Left Click | `[None, 1, 1, 0, 0]` |
| `right_click_pattern` | Pola jari untuk Right Click | `[None, 1, 1, 1, 0]` |
| `drag_pattern` | Pola jari untuk Drag | `[None, 0, 0, 0, 0]` |
| `scroll_pattern` | Pola jari untuk Scroll | `[None, 1, 1, 1, 1]` |

`move_patterns` adalah **tuple of list** — bisa punya multiple alternatif. Contoh: `([0,1,0,0,0], [1,1,0,0,0])` → dua cara berbeda untuk Move.

## Cara Tambah Profile Baru

```python
GESTURE_PROFILES["custom"] = {
    "move_patterns": ([None, 1, 0, 0, 0],),  # telunjuk naik
    "stop_pattern": None,
    "click_pattern": [None, 1, 1, 0, 0],     # telunjuk+tengah pinch
    "right_click_pattern": [None, 1, 1, 1, 0],
    "drag_pattern": [None, 0, 0, 0, 0],
    "scroll_pattern": [None, 1, 1, 1, 1],
}
```

Lalu set `GESTURE_STYLE = "custom"` di config.py.

## Istilah Teknis

- **Profile:** satu set definisi gesture. Bisa ada multiple profile untuk gaya gesture berbeda.
- **Wildcard (`None`):** dalam pattern matching, `None` = "nilai di posisi ini diabaikan". Dipakai untuk mengabaikan jempol.
- **Pattern matching:** membandingkan state jari aktual dengan pola yang diharapkan. `[1,1,0,0,0]` harus persis sama di setiap posisi (kecuali yang `None`).
