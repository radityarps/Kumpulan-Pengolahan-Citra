# Panduan Demo Kode Presentasi AI Virtual Mouse

Gunakan file ini sebagai pegangan saat audiens meminta bukti teknis. Fokus demo sebaiknya singkat: tunjukkan masalah baseline, tunjukkan perbaikan debounce, lalu tunjukkan cara benchmark menghasilkan metrik.

## 1. Kode Baseline yang Bermasalah

File:

`src/video version/AiVirtualMouseProject.py`

Bagian yang ditunjukkan:

```python
# 8. Both Index and middle fingers are up : Clicking Mode
if fingers[1] == 1 and fingers[2] == 1:
    # 9. Find distance between fingers
    length, img, lineInfo = detector.findDistance(8, 12, img)
    print(length)
    # 10. Click mouse if distance short
    if length < 40:
        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
        autopy.mouse.click()
```

Cara menjelaskan:

Kode ini berada di dalam loop frame kamera. Jika pinch tetap terbaca pada beberapa frame berurutan, `autopy.mouse.click()` bisa dipanggil berulang kali. Tidak ada state yang membedakan "pinch baru dimulai", "pinch sedang ditahan", dan "pinch sudah dilepas".

Masalah teknis:

- Klik langsung dipicu dari kondisi `length < 40`.
- Tidak ada debounce.
- Tidak ada release-before-next-click.
- Tidak ada cooldown.
- Satu gesture tahan bisa menjadi banyak click event.

## 2. Perbaikan Inti: Debounce Click

File:

`src/ai_virtual_mouse_experimental/gesture_engine.py`

Bagian konfigurasi:

```python
@dataclass(frozen=True)
class ClickDebounceConfig:
    stable_frames_required: int = 2
    release_frames_required: int = 2
    cooldown_seconds: float = 0.35
```

Bagian logika:

```python
def update_click_debounce(
    state: ClickDebounceState,
    raw_click_active: bool,
    now_s: float,
    config: ClickDebounceConfig | None = None,
) -> ClickDebounceResult:
    cfg = config or ClickDebounceConfig()

    if raw_click_active:
        next_state = ClickDebounceState(
            pressed_frames=state.pressed_frames + 1,
            released_frames=0,
            armed=state.armed,
            last_click_time_s=state.last_click_time_s,
        )
        cooldown_elapsed = now_s - state.last_click_time_s >= cfg.cooldown_seconds
        stable = next_state.pressed_frames >= cfg.stable_frames_required
        if next_state.armed and stable and cooldown_elapsed:
            return ClickDebounceResult(
                state=ClickDebounceState(
                    pressed_frames=next_state.pressed_frames,
                    released_frames=0,
                    armed=False,
                    last_click_time_s=now_s,
                ),
                emit_click=True,
                reason="stable_click_emitted",
            )
        return ClickDebounceResult(next_state, False, "click_not_ready")

    released_frames = state.released_frames + 1
    armed = state.armed or released_frames >= cfg.release_frames_required
    return ClickDebounceResult(
        state=ClickDebounceState(
            pressed_frames=0,
            released_frames=released_frames,
            armed=armed,
            last_click_time_s=state.last_click_time_s,
        ),
        emit_click=False,
        reason="released" if armed else "waiting_for_release",
    )
```

Cara menjelaskan:

Di sini sistem tidak langsung klik ketika pinch aktif. Sistem menghitung berapa frame pinch stabil, mengecek apakah state masih armed, dan memastikan cooldown sudah lewat. Setelah klik keluar, state menjadi tidak armed sampai gesture dilepas beberapa frame.

Kalimat demo:

"Bagian ini mengubah klik dari frame-based event menjadi intention-based event. Jadi satu pinch yang ditahan hanya boleh menghasilkan satu klik."

## 3. Perbaikan dalam Pipeline

File:

`src/ai_virtual_mouse_experimental/hand_control_pipeline.py`

Bagian yang ditunjukkan:

```python
if gesture.click:
    if self._debounce_enabled:
        debounce_res = update_click_debounce(
            self._click_debounce,
            True,
            time.time(),
            self._debounce_cfg,
        )
        self._click_debounce = debounce_res.state
        click_fired = debounce_res.emit_click
    else:
        click_fired = True
else:
    if self._debounce_enabled:
        debounce_res = update_click_debounce(
            self._click_debounce,
            False,
            time.time(),
            self._debounce_cfg,
        )
        self._click_debounce = debounce_res.state
```

Cara menjelaskan:

Pipeline menerima hasil gesture dari gesture engine. Jika gesture adalah click, pipeline tidak otomatis mengklik. Ia memanggil `update_click_debounce` dulu. Output yang dipakai runtime adalah `click_fired`, bukan raw gesture click.

Perbedaan dengan baseline:

- Baseline: `pinch true -> click langsung`.
- Improved: `pinch true -> debounce -> click_fired bila stabil dan armed`.

## 4. MediaPipe Tasks dan Solutions

File:

`src/ai_virtual_mouse_experimental/hand_tracker.py`

Bagian yang ditunjukkan:

```python
def _setup_backend(self) -> None:
    if self.prefer_tasks:
        try:
            self._setup_tasks_backend()
            self._backend_used = "mediapipe_tasks"
            return
        except Exception as exc:
            self._fallback_reason = str(exc)
            print(f"[WARN] Tasks backend failed ({exc}).")
            try:
                self._setup_solutions_backend()
            except Exception as fallback_exc:
                raise RuntimeError(...)
            print("[WARN] Falling back to MediaPipe Solutions.")
            self._backend_used = "mediapipe_solutions"
            return
    self._setup_solutions_backend()
    self._backend_used = "mediapipe_solutions"
```

Cara menjelaskan:

Improved prototype memprioritaskan MediaPipe Tasks, tetapi tetap punya fallback ke MediaPipe Solutions. Ini membuat backend lebih eksplisit dan metadata eksperimen bisa mencatat backend yang benar-benar digunakan.

Catatan penting untuk disampaikan:

Tasks membantu membuat backend lebih modern dan eksplisit, tetapi penurunan false clicks terutama berasal dari logika pipeline: stable pinch, debounce, dan release state.

## 5. Safety Benchmark: Simulated Cursor

File:

`src/ai_virtual_mouse_experimental/benchmark_shell.py`

Bagian yang ditunjukkan:

```python
def apply_hand_frame_to_benchmark(
    state: BenchmarkShellState,
    benchmark,
    hand_frame: HandControlFrame,
    now_s: float,
):
    if not hand_frame.paused and hand_frame.cursor_target is not None:
        mirrored_x = state.width - hand_frame.cursor_target.x
        state = set_simulated_cursor(state, mirrored_x, hand_frame.cursor_target.y)
    if not hand_frame.paused and hand_frame.click_fired:
        benchmark = register_click(benchmark, state.cursor.x, state.cursor.y, now_s)
    return state, benchmark
```

Cara menjelaskan:

Benchmark tidak menggerakkan mouse asli. Output pipeline diterapkan ke `state.cursor`, yaitu simulated cursor pada Pygame. Jika `click_fired` true, benchmark mendaftarkan klik pada posisi simulated cursor, bukan menekan mouse sistem operasi.

Kalimat demo:

"Ini alasan benchmark aman. Kita tetap menguji input tangan, tetapi efeknya hanya di window Pygame."

## 6. Cara Benchmark Menghasilkan Kesimpulan

File:

`src/ai_virtual_mouse_experimental/benchmark_grid.py`

Bagian yang ditunjukkan:

```python
hit = distance(click_x, click_y, target.x, target.y) <= target.radius
completion_time = max(0.0, now_s - state.trial_start_time_s)

if not hit:
    return PointClickBenchmarkState(
        targets=state.targets,
        current_index=state.current_index,
        trial_start_time_s=state.trial_start_time_s,
        false_clicks_current_trial=state.false_clicks_current_trial + 1,
        results=state.results,
    )

result = TrialResult(
    trial_index=state.current_index,
    target_x=target.x,
    target_y=target.y,
    click_x=click_x,
    click_y=click_y,
    hit=True,
    completion_time_s=completion_time,
    false_clicks_before_hit=state.false_clicks_current_trial,
)
```

Cara menjelaskan:

Jika click berada dalam radius target, trial dianggap hit dan target maju. Jika click di luar radius target, itu false click dan target tetap sama. Karena itu baseline yang memancarkan banyak klik saat pinch ditahan akan mendapat banyak false clicks.

Kesimpulan yang aman:

- Baseline dan improved sama-sama mencapai 100% hit rate.
- Improved jauh mengurangi false clicks.
- Improved tidak diklaim lebih cepat rata-rata karena ada outlier session.

## 7. Urutan Demo yang Disarankan

1. Buka `src/video version/AiVirtualMouseProject.py`.
2. Tunjukkan `if length < 40: autopy.mouse.click()`.
3. Jelaskan kenapa loop frame membuat satu pinch bisa menjadi banyak click event.
4. Buka `src/ai_virtual_mouse_experimental/gesture_engine.py`.
5. Tunjukkan `ClickDebounceConfig` dan `update_click_debounce`.
6. Buka `src/ai_virtual_mouse_experimental/hand_control_pipeline.py`.
7. Tunjukkan bahwa runtime memakai `click_fired`, bukan raw click.
8. Buka `src/ai_virtual_mouse_experimental/benchmark_grid.py`.
9. Jelaskan hit, false click, dan completion time.

## 8. Kalimat Penutup Demo

"Dari demo kode ini, perubahan utamanya bukan hanya mengganti MediaPipe Solutions ke Tasks. Perubahan paling penting adalah memisahkan deteksi tangan dari logika kontrol, lalu membuat klik punya state melalui debounce. Karena itu, improved pipeline bisa mempertahankan hit rate 100% sambil menurunkan klik tidak disengaja secara besar."

