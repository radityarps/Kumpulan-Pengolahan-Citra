from __future__ import annotations

import time
from dataclasses import dataclass
from importlib import import_module

from .app import RuntimePlan
from .benchmark_grid import (
    create_point_click_benchmark,
    register_click,
    start_current_trial,
    summarize_benchmark,
)
from .benchmark_logging import format_output_paths, persist_benchmark_session
from .config import ExperimentalConfig
from .hand_control_pipeline import HandControlFrame, HandControlPipeline


class BenchmarkShellError(RuntimeError):
    """Raised when the simulated benchmark shell cannot start."""


@dataclass(frozen=True)
class SimulatedCursor:
    x: float
    y: float
    radius: int = 10


@dataclass(frozen=True)
class BenchmarkShellState:
    width: int
    height: int
    condition: str
    backend: str
    cursor: SimulatedCursor
    safe_quit_keys: tuple[str, ...] = ("q", "escape")
    controls_real_mouse: bool = False


def create_benchmark_shell_state(
    config: ExperimentalConfig, plan: RuntimePlan
) -> BenchmarkShellState:
    return BenchmarkShellState(
        width=config.benchmark.window_width,
        height=config.benchmark.window_height,
        condition=plan.condition,
        backend=plan.backend,
        cursor=SimulatedCursor(
            x=config.benchmark.window_width / 2,
            y=config.benchmark.window_height / 2,
        ),
    )


def benchmark_instruction_lines(state: BenchmarkShellState) -> list[str]:
    return [
        "AI Virtual Mouse Benchmark Shell",
        f"Condition: {state.condition}",
        f"Backend: {state.backend}",
        "This benchmark uses a simulated cursor and does not move the OS mouse.",
        "Placeholder controls: arrow keys or WASD move the simulated cursor.",
        "Press Space or left mouse button to click the current target.",
        "Safe quit: press Q or Escape, or close the window.",
    ]


def move_simulated_cursor(
    state: BenchmarkShellState, dx: float, dy: float
) -> BenchmarkShellState:
    cursor = SimulatedCursor(
        x=min(
            max(state.cursor.x + dx, state.cursor.radius),
            state.width - state.cursor.radius,
        ),
        y=min(
            max(state.cursor.y + dy, state.cursor.radius),
            state.height - state.cursor.radius,
        ),
        radius=state.cursor.radius,
    )
    return _replace_cursor(state, cursor)


def set_simulated_cursor(
    state: BenchmarkShellState, x: float, y: float
) -> BenchmarkShellState:
    cursor = SimulatedCursor(
        x=min(max(x, state.cursor.radius), state.width - state.cursor.radius),
        y=min(max(y, state.cursor.radius), state.height - state.cursor.radius),
        radius=state.cursor.radius,
    )
    return _replace_cursor(state, cursor)


def apply_hand_frame_to_benchmark(
    state: BenchmarkShellState,
    benchmark,
    hand_frame: HandControlFrame,
    now_s: float,
):
    if not hand_frame.paused and hand_frame.cursor_target is not None:
        state = set_simulated_cursor(
            state, hand_frame.cursor_target.x, hand_frame.cursor_target.y
        )
    if not hand_frame.paused and hand_frame.click_fired:
        benchmark = register_click(benchmark, state.cursor.x, state.cursor.y, now_s)
    return state, benchmark


def prefer_tasks_for_hand_benchmark(condition_name: str) -> bool:
    """Prefer available Tasks backend for hand benchmark; condition controls semantics."""
    return True


def _replace_cursor(
    state: BenchmarkShellState, cursor: SimulatedCursor
) -> BenchmarkShellState:
    return BenchmarkShellState(
        width=state.width,
        height=state.height,
        condition=state.condition,
        backend=state.backend,
        cursor=cursor,
        safe_quit_keys=state.safe_quit_keys,
        controls_real_mouse=state.controls_real_mouse,
    )


def run_pygame_benchmark_shell(
    config: ExperimentalConfig, plan: RuntimePlan, hand_input: bool = False
) -> int:
    try:
        pygame = import_module("pygame")
    except ModuleNotFoundError as exc:
        raise BenchmarkShellError(
            "Pygame is required for benchmark mode. Install project requirements "
            "with `pip install -r requirements.txt`."
        ) from exc

    state = create_benchmark_shell_state(config, plan)
    benchmark = start_current_trial(
        create_point_click_benchmark(config.benchmark), time.perf_counter()
    )
    pygame.init()
    screen = pygame.display.set_mode((state.width, state.height))
    pygame.display.set_caption("AI Virtual Mouse Benchmark Shell")
    font = pygame.font.SysFont("arial", 22)
    small_font = pygame.font.SysFont("arial", 18)
    clock = pygame.time.Clock()

    # Hand input setup
    pipeline = None
    cap = None
    cv2 = None
    if hand_input:
        cv2 = import_module("cv2")
        pipeline = HandControlPipeline(
            config=config,
            condition_name=plan.condition,
            output_width=state.width,
            output_height=state.height,
            prefer_tasks=prefer_tasks_for_hand_benchmark(plan.condition),
        )
        cap = cv2.VideoCapture(config.backend.camera_index)
        cap.set(3, config.backend.camera_width)
        cap.set(4, config.backend.camera_height)
        print(f"Hand input enabled for benchmark. Profile: {pipeline.gesture_profile}")

    running = True
    while running:
        dt = clock.tick(60) / 1000
        speed = 420 * dt
        dx = dy = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_q, pygame.K_ESCAPE)
            ):
                running = False
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):
                benchmark = register_click(
                    benchmark, state.cursor.x, state.cursor.y, time.perf_counter()
                )

        # Hand input processing
        hand_frame = None
        if pipeline is not None and cap is not None and cv2 is not None:
            success, camera_image = cap.read()
            if success:
                hand_frame = pipeline.process_frame(camera_image)
                state, benchmark = apply_hand_frame_to_benchmark(
                    state, benchmark, hand_frame, time.perf_counter()
                )

        # Keyboard fallback controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed
        if dx or dy:
            state = move_simulated_cursor(state, dx, dy)

        screen.fill((18, 22, 28))
        y = 28
        for index, line in enumerate(benchmark_instruction_lines(state)):
            rendered = (font if index == 0 else small_font).render(
                line, True, (236, 240, 244)
            )
            screen.blit(rendered, (28, y))
            y += 34 if index == 0 else 26

        if benchmark.is_complete:
            summary = summarize_benchmark(benchmark)
            summary_lines = [
                "Benchmark complete",
                f"hits: {summary.hits}/{summary.total_trials}",
                f"false clicks: {summary.false_clicks}",
                f"mean time: {summary.mean_completion_time_s:.2f}s",
            ]
            for offset, line in enumerate(summary_lines):
                rendered = font.render(line, True, (144, 238, 144))
                screen.blit(
                    rendered, (state.width // 2 - 120, state.height // 2 + offset * 32)
                )
        else:
            target = benchmark.current_target
            if target is not None:
                pygame.draw.circle(
                    screen, (88, 166, 255), (target.x, target.y), target.radius, 3
                )
                target_label = small_font.render(
                    f"target {target.index + 1}/{len(benchmark.targets)}",
                    True,
                    (136, 192, 255),
                )
                screen.blit(
                    target_label, (target.x - 48, target.y - target.radius - 26)
                )
        pygame.draw.circle(
            screen,
            (255, 92, 138),
            (int(state.cursor.x), int(state.cursor.y)),
            state.cursor.radius,
        )
        cursor_label = small_font.render("simulated cursor", True, (255, 166, 190))
        screen.blit(cursor_label, (int(state.cursor.x) + 14, int(state.cursor.y) - 8))

        # Hand input overlay
        if hand_frame is not None:
            hand_overlay = [
                f"Hand: {hand_frame.gesture_name}",
                f"Paused: {hand_frame.paused}",
                f"Backend: {hand_frame.backend_used}",
            ]
            for i, line in enumerate(hand_overlay):
                rendered = small_font.render(line, True, (180, 220, 255))
                screen.blit(rendered, (state.width - 220, 10 + i * 22))

        pygame.display.flip()

    if cap is not None:
        cap.release()
    hand_metadata = pipeline.build_metadata() if pipeline is not None else None
    if pipeline is not None:
        pipeline.close()
    paths = persist_benchmark_session(
        benchmark, config, plan, hand_input_metadata=hand_metadata
    )
    pygame.quit()
    print(format_output_paths(paths))
    return 0
