from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from .config import BenchmarkSettings


@dataclass(frozen=True)
class Target:
    index: int
    x: int
    y: int
    radius: int


@dataclass(frozen=True)
class TrialResult:
    trial_index: int
    target_x: int
    target_y: int
    click_x: float
    click_y: float
    hit: bool
    completion_time_s: float
    false_clicks_before_hit: int


@dataclass(frozen=True)
class BenchmarkSummary:
    total_trials: int
    hits: int
    misses: int
    false_clicks: int
    mean_completion_time_s: float


@dataclass(frozen=True)
class PointClickBenchmarkState:
    targets: tuple[Target, ...]
    current_index: int = 0
    trial_start_time_s: float = 0.0
    false_clicks_current_trial: int = 0
    results: tuple[TrialResult, ...] = field(default_factory=tuple)

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.targets)

    @property
    def current_target(self) -> Target | None:
        if self.is_complete:
            return None
        return self.targets[self.current_index]


def generate_grid_targets(settings: BenchmarkSettings) -> tuple[Target, ...]:
    rng = random.Random(settings.random_seed)
    margin = settings.target_radius * 2
    columns = 4
    rows = max(1, math.ceil(settings.target_count / columns))
    usable_width = settings.window_width - margin * 2
    usable_height = settings.window_height - margin * 2

    points: list[tuple[int, int]] = []
    for row in range(rows):
        for column in range(columns):
            if len(points) >= settings.target_count:
                break
            x = margin + int((column + 0.5) * usable_width / columns)
            y = margin + int((row + 0.5) * usable_height / rows)
            points.append((x, y))

    rng.shuffle(points)
    return tuple(
        Target(index=index, x=x, y=y, radius=settings.target_radius)
        for index, (x, y) in enumerate(points)
    )


def create_point_click_benchmark(settings: BenchmarkSettings) -> PointClickBenchmarkState:
    return PointClickBenchmarkState(
        targets=generate_grid_targets(settings),
        trial_start_time_s=0.0,
    )


def start_current_trial(
    state: PointClickBenchmarkState, now_s: float
) -> PointClickBenchmarkState:
    return PointClickBenchmarkState(
        targets=state.targets,
        current_index=state.current_index,
        trial_start_time_s=now_s,
        false_clicks_current_trial=state.false_clicks_current_trial,
        results=state.results,
    )


def register_click(
    state: PointClickBenchmarkState,
    click_x: float,
    click_y: float,
    now_s: float,
) -> PointClickBenchmarkState:
    target = state.current_target
    if target is None:
        return state

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
    return PointClickBenchmarkState(
        targets=state.targets,
        current_index=state.current_index + 1,
        trial_start_time_s=now_s,
        false_clicks_current_trial=0,
        results=state.results + (result,),
    )


def summarize_benchmark(state: PointClickBenchmarkState) -> BenchmarkSummary:
    hits = sum(1 for result in state.results if result.hit)
    false_clicks = sum(result.false_clicks_before_hit for result in state.results)
    misses = len(state.targets) - hits
    mean_time = (
        sum(result.completion_time_s for result in state.results) / hits if hits else 0.0
    )
    return BenchmarkSummary(
        total_trials=len(state.targets),
        hits=hits,
        misses=misses,
        false_clicks=false_clicks + state.false_clicks_current_trial,
        mean_completion_time_s=mean_time,
    )


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x2 - x1, y2 - y1)
