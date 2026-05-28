import csv
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from importlib import import_module
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

app_module = import_module("ai_virtual_mouse_experimental.app")
baseline_module = import_module("ai_virtual_mouse_experimental.baseline")
benchmark_grid_module = import_module("ai_virtual_mouse_experimental.benchmark_grid")
benchmark_logging_module = import_module(
    "ai_virtual_mouse_experimental.benchmark_logging"
)
benchmark_report_module = import_module(
    "ai_virtual_mouse_experimental.benchmark_report"
)
benchmark_shell_module = import_module("ai_virtual_mouse_experimental.benchmark_shell")
cli_module = import_module("ai_virtual_mouse_experimental.cli")
config_module = import_module("ai_virtual_mouse_experimental.config")
cursor_mapping_module = import_module("ai_virtual_mouse_experimental.cursor_mapping")
gesture_engine_module = import_module("ai_virtual_mouse_experimental.gesture_engine")
hand_control_pipeline_module = import_module(
    "ai_virtual_mouse_experimental.hand_control_pipeline"
)
tasks_backend_module = import_module("ai_virtual_mouse_experimental.tasks_backend")

StartupError = app_module.StartupError
build_runtime_plan = app_module.build_runtime_plan
build_baseline_metadata = baseline_module.build_baseline_metadata
classify_baseline_gesture = baseline_module.classify_baseline_gesture
benchmark_instruction_lines = benchmark_shell_module.benchmark_instruction_lines
create_benchmark_shell_state = benchmark_shell_module.create_benchmark_shell_state
apply_hand_frame_to_benchmark = benchmark_shell_module.apply_hand_frame_to_benchmark
move_simulated_cursor = benchmark_shell_module.move_simulated_cursor
run_pygame_benchmark_shell = benchmark_shell_module.run_pygame_benchmark_shell
create_point_click_benchmark = benchmark_grid_module.create_point_click_benchmark
generate_grid_targets = benchmark_grid_module.generate_grid_targets
register_click = benchmark_grid_module.register_click
start_current_trial = benchmark_grid_module.start_current_trial
summarize_benchmark = benchmark_grid_module.summarize_benchmark
format_output_paths = benchmark_logging_module.format_output_paths
persist_benchmark_session = benchmark_logging_module.persist_benchmark_session
BenchmarkMetrics = benchmark_report_module.BenchmarkMetrics
compute_metrics = benchmark_report_module.compute_metrics
generate_comparison_report = benchmark_report_module.generate_comparison_report
generate_markdown_report = benchmark_report_module.generate_markdown_report
generate_report_from_session = benchmark_report_module.generate_report_from_session
load_trials_csv = benchmark_report_module.load_trials_csv
main = cli_module.main
ConfigError = config_module.ConfigError
load_config = config_module.load_config
Bounds = cursor_mapping_module.Bounds
CalibrationConfig = cursor_mapping_module.CalibrationConfig
Point = cursor_mapping_module.Point
SmoothingConfig = cursor_mapping_module.SmoothingConfig
adaptive_smooth = cursor_mapping_module.adaptive_smooth
apply_smoothing = cursor_mapping_module.apply_smoothing
calibrate_bounds = cursor_mapping_module.calibrate_bounds
default_camera_bounds = cursor_mapping_module.default_camera_bounds
map_point_to_output = cursor_mapping_module.map_point_to_output
select_mapping_bounds = cursor_mapping_module.select_mapping_bounds
GestureEngineConfig = gesture_engine_module.GestureEngineConfig
GestureInput = gesture_engine_module.GestureInput
ClickDebounceConfig = gesture_engine_module.ClickDebounceConfig
ClickDebounceState = gesture_engine_module.ClickDebounceState
classify_improved_gesture = gesture_engine_module.classify_improved_gesture
classify_simple_real_mouse_gesture = (
    gesture_engine_module.classify_simple_real_mouse_gesture
)
config_from_settings = gesture_engine_module.config_from_settings
debounce_config_from_settings = gesture_engine_module.debounce_config_from_settings
feedback_style = gesture_engine_module.feedback_style
update_click_debounce = gesture_engine_module.update_click_debounce
build_tasks_backend_metadata = tasks_backend_module.build_tasks_backend_metadata
download_hand_landmarker_model = tasks_backend_module.download_hand_landmarker_model
ensure_hand_landmarker_model = tasks_backend_module.ensure_hand_landmarker_model
resolve_model_path = tasks_backend_module.resolve_model_path
HandControlFrame = hand_control_pipeline_module.HandControlFrame
_classify_baseline_as_gesture_result = (
    hand_control_pipeline_module._classify_baseline_as_gesture_result
)
_compute_jitter = hand_control_pipeline_module._compute_jitter
hand_input_from_tracking = hand_control_pipeline_module.hand_input_from_tracking
BackendError = tasks_backend_module.BackendError


CONFIG_PATH = Path("config/experimental.toml")


class ExperimentalSkeletonTests(unittest.TestCase):
    def test_loads_default_config(self):
        config = load_config(CONFIG_PATH)

        self.assertEqual(config.app.default_mode, "benchmark")
        self.assertIn("baseline", config.conditions)
        self.assertIn("improved", config.conditions)

    def test_builds_safe_default_runtime_plan(self):
        config = load_config(CONFIG_PATH)

        plan = build_runtime_plan(config)

        self.assertEqual(plan.mode, "benchmark")
        self.assertEqual(plan.condition, "baseline")
        self.assertFalse(plan.controls_real_mouse)

    def test_rejects_real_mouse_mode_without_explicit_permission(self):
        config = load_config(CONFIG_PATH)

        with self.assertRaisesRegex(StartupError, "real OS mouse"):
            build_runtime_plan(config, mode_name="demo")

    def test_rejects_unknown_condition(self):
        config = load_config(CONFIG_PATH)

        with self.assertRaisesRegex(ConfigError, "Unknown condition"):
            build_runtime_plan(config, condition_name="not-a-condition")

    def test_cli_help_exits_successfully(self):
        output = StringIO()

        with self.assertRaises(SystemExit) as exc, redirect_stdout(output):
            main(["--help"])

        self.assertEqual(exc.exception.code, 0)
        self.assertIn("experimental AI Virtual Mouse", output.getvalue())

    def test_cli_lists_modes_and_conditions(self):
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(["--list"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Available modes", output.getvalue())
        self.assertIn("Available conditions", output.getvalue())
        self.assertIn("MediaPipe Tasks backend", output.getvalue())

    def test_cli_exposes_selected_metadata(self):
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(["--metadata", "--condition", "baseline"])

        self.assertEqual(exit_code, 0)
        self.assertIn('"condition": "baseline"', output.getvalue())
        self.assertIn('"gesture_profile": "tutorial_pinch"', output.getvalue())

    def test_baseline_gesture_preserves_tutorial_movement(self):
        result = classify_baseline_gesture([0, 1, 0, 0, 0])

        self.assertEqual(result.action, "move")
        self.assertEqual(result.reason, "index_only")

    def test_baseline_gesture_preserves_tutorial_click(self):
        result = classify_baseline_gesture([0, 1, 1, 0, 0], pinch_distance=30)

        self.assertEqual(result.action, "click")

    def test_baseline_gesture_ignores_no_hand_state(self):
        result = classify_baseline_gesture([])

        self.assertEqual(result.action, "idle")

    def test_baseline_metadata_exposes_condition_for_reports(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, condition_name="baseline")

        metadata = build_baseline_metadata(config, plan)

        self.assertEqual(metadata.condition, "baseline")
        self.assertEqual(metadata.backend, "mediapipe_solutions")
        self.assertEqual(metadata.gesture_profile, "tutorial_pinch")
        self.assertIn("no_hand_guard", metadata.compatibility_fixes)

    def test_benchmark_shell_state_uses_simulated_cursor_safely(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="baseline"
        )

        state = create_benchmark_shell_state(config, plan)

        self.assertEqual(state.condition, "baseline")
        self.assertEqual(state.backend, "mediapipe_solutions")
        self.assertFalse(state.controls_real_mouse)
        self.assertEqual(state.cursor.x, config.benchmark.window_width / 2)

    def test_benchmark_shell_instructions_include_safe_quit(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, mode_name="benchmark")
        state = create_benchmark_shell_state(config, plan)

        instructions = "\n".join(benchmark_instruction_lines(state))

        self.assertIn("simulated cursor", instructions)
        self.assertIn("does not move the OS mouse", instructions)
        self.assertIn("Q or Escape", instructions)

    def test_benchmark_shell_cursor_movement_is_clamped(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, mode_name="benchmark")
        state = create_benchmark_shell_state(config, plan)

        moved = move_simulated_cursor(state, -10_000, -10_000)

        self.assertEqual(moved.cursor.x, moved.cursor.radius)
        self.assertEqual(moved.cursor.y, moved.cursor.radius)

    def test_point_click_targets_are_deterministic(self):
        config = load_config(CONFIG_PATH)

        first = generate_grid_targets(config.benchmark)
        second = generate_grid_targets(config.benchmark)

        self.assertEqual(first, second)
        self.assertEqual(len(first), config.benchmark.target_count)

    def test_point_click_benchmark_records_hit_trial(self):
        config = load_config(CONFIG_PATH)
        state = start_current_trial(
            create_point_click_benchmark(config.benchmark), 10.0
        )
        target = state.current_target
        self.assertIsNotNone(target)

        clicked = register_click(state, target.x, target.y, 12.5)

        self.assertEqual(len(clicked.results), 1)
        self.assertTrue(clicked.results[0].hit)
        self.assertEqual(clicked.results[0].completion_time_s, 2.5)

    def test_point_click_benchmark_counts_false_clicks(self):
        config = load_config(CONFIG_PATH)
        state = start_current_trial(
            create_point_click_benchmark(config.benchmark), 10.0
        )
        target = state.current_target
        self.assertIsNotNone(target)

        missed = register_click(state, 0, 0, 11.0)
        hit = register_click(missed, target.x, target.y, 12.0)
        summary = summarize_benchmark(hit)

        self.assertEqual(hit.results[0].false_clicks_before_hit, 1)
        self.assertEqual(summary.false_clicks, 1)

    def test_benchmark_logging_creates_session_metadata_and_csv(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="baseline"
        )
        state = start_current_trial(
            create_point_click_benchmark(config.benchmark), 10.0
        )
        target = state.current_target
        self.assertIsNotNone(target)
        state = register_click(state, target.x, target.y, 12.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(
                state, config, plan, output_root=Path(tmpdir)
            )
            metadata = json.loads(paths.metadata_path.read_text(encoding="utf-8"))
            with paths.trials_csv_path.open(newline="", encoding="utf-8") as csv_file:
                rows = list(csv.DictReader(csv_file))

        self.assertTrue(paths.session_dir.name)
        self.assertEqual(metadata["condition"], "baseline")
        self.assertEqual(metadata["backend"], "mediapipe_solutions")
        self.assertEqual(rows[0]["condition"], "baseline")
        self.assertEqual(rows[0]["mode"], "benchmark")
        self.assertEqual(rows[0]["hit"], "True")

    def test_benchmark_logging_works_for_improved_placeholder(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="improved"
        )
        state = create_point_click_benchmark(config.benchmark)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(
                state, config, plan, output_root=Path(tmpdir)
            )
            metadata = json.loads(paths.metadata_path.read_text(encoding="utf-8"))

        self.assertEqual(metadata["condition"], "improved")
        self.assertEqual(metadata["backend"], "mediapipe_tasks")

    def test_benchmark_output_paths_are_printable(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, mode_name="benchmark")
        state = create_point_click_benchmark(config.benchmark)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(
                state, config, plan, output_root=Path(tmpdir)
            )

        formatted = format_output_paths(paths)

        self.assertIn("metadata", formatted)
        self.assertIn("trials CSV", formatted)
        self.assertIn("report", formatted)

    def test_benchmark_metrics_and_report_are_generated_from_session(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="baseline"
        )
        state = start_current_trial(
            create_point_click_benchmark(config.benchmark), 10.0
        )
        target = state.current_target
        self.assertIsNotNone(target)
        state = register_click(state, 0, 0, 11.0)
        state = register_click(state, target.x, target.y, 13.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(
                state, config, plan, output_root=Path(tmpdir)
            )
            report_paths = generate_report_from_session(paths.session_dir)
            rows = load_trials_csv(paths.trials_csv_path)
            metadata = json.loads(paths.metadata_path.read_text(encoding="utf-8"))
            metrics = compute_metrics(rows, metadata)
            report = report_paths.report_path.read_text(encoding="utf-8")
            plot_exists = report_paths.completion_plot_path.exists()

        self.assertEqual(metrics.hit_count, 1)
        self.assertEqual(metrics.false_clicks, 1)
        self.assertEqual(metrics.click_count, 2)
        self.assertGreaterEqual(metrics.hit_rate, 0)
        self.assertIn("Mean completion time", report)
        self.assertTrue(plot_exists)

    def test_cli_generates_report_from_existing_session(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="baseline"
        )
        state = start_current_trial(
            create_point_click_benchmark(config.benchmark), 10.0
        )
        target = state.current_target
        self.assertIsNotNone(target)
        state = register_click(state, target.x, target.y, 11.5)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(
                state, config, plan, output_root=Path(tmpdir), generate_report=False
            )
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(["--report-session", str(paths.session_dir)])

        self.assertEqual(exit_code, 0)
        self.assertIn("Benchmark report generated", output.getvalue())

    def test_improved_gesture_engine_supports_move(self):
        result = classify_improved_gesture(GestureInput(index=True))

        self.assertEqual(result.name, "move")
        self.assertTrue(result.cursor_enabled)

    def test_improved_gesture_engine_supports_click(self):
        result = classify_improved_gesture(
            GestureInput(index=True, middle=True, pinch_distance_px=20)
        )

        self.assertEqual(result.name, "click")
        self.assertTrue(result.click)

    def test_improved_gesture_engine_supports_drag(self):
        result = classify_improved_gesture(
            GestureInput(
                index=True,
                middle=True,
                pinch_distance_px=20,
                pinch_duration_s=1.0,
            ),
            GestureEngineConfig(drag_hold_seconds=0.5),
        )

        self.assertEqual(result.name, "drag")
        self.assertTrue(result.drag)

    def test_improved_gesture_engine_supports_scroll(self):
        result = classify_improved_gesture(
            GestureInput(
                index=True,
                middle=True,
                index_middle_vertical_delta_px=30,
            )
        )

        self.assertEqual(result.name, "scroll")
        self.assertNotEqual(result.scroll_delta, 0)

    def test_improved_gesture_engine_supports_pause_feedback(self):
        result = classify_improved_gesture(
            GestureInput(index=True, middle=True, ring=True, pinky=True)
        )
        style = feedback_style(result)

        self.assertEqual(result.name, "pause")
        self.assertTrue(result.paused)
        self.assertEqual(style["label"], "Paused")
        self.assertIn("color", style)

    def test_simple_real_mouse_profile_supports_only_move_click_pause(self):
        move = classify_simple_real_mouse_gesture(GestureInput(index=True))
        click = classify_simple_real_mouse_gesture(
            GestureInput(index=True, middle=True, pinch_distance_px=20)
        )
        pause = classify_simple_real_mouse_gesture(
            GestureInput(index=True, middle=True, ring=True, pinky=True)
        )
        scroll_like = classify_simple_real_mouse_gesture(
            GestureInput(
                index=True,
                middle=True,
                index_middle_vertical_delta_px=30,
            )
        )
        drag_like = classify_simple_real_mouse_gesture(
            GestureInput(
                index=True,
                middle=True,
                pinch_distance_px=20,
                pinch_duration_s=1.0,
            ),
            GestureEngineConfig(drag_hold_seconds=0.5),
        )
        not_index_only = classify_simple_real_mouse_gesture(
            GestureInput(index=True, ring=True)
        )

        self.assertEqual(move.name, "move")
        self.assertEqual(click.name, "click")
        self.assertEqual(pause.name, "pause")
        self.assertEqual(scroll_like.name, "idle")
        self.assertEqual(drag_like.name, "click")
        self.assertEqual(not_index_only.name, "idle")

    def test_gesture_engine_config_uses_project_settings(self):
        config = load_config(CONFIG_PATH)

        engine_config = config_from_settings(config.gesture)

        self.assertEqual(
            engine_config.click_threshold_px, config.gesture.click_threshold_px
        )

    def test_click_debounce_emits_one_click_per_stable_pinch(self):
        state = ClickDebounceState()
        config = ClickDebounceConfig(
            stable_frames_required=2, release_frames_required=2, cooldown_seconds=0.35
        )

        first = update_click_debounce(state, True, 1.0, config)
        second = update_click_debounce(first.state, True, 1.1, config)
        repeated = update_click_debounce(second.state, True, 1.2, config)

        self.assertFalse(first.emit_click)
        self.assertTrue(second.emit_click)
        self.assertFalse(repeated.emit_click)

    def test_click_debounce_rearms_after_release(self):
        config = ClickDebounceConfig(
            stable_frames_required=1, release_frames_required=2, cooldown_seconds=0.0
        )
        emitted = update_click_debounce(ClickDebounceState(), True, 1.0, config)
        release_one = update_click_debounce(emitted.state, False, 1.1, config)
        release_two = update_click_debounce(release_one.state, False, 1.2, config)
        emitted_again = update_click_debounce(release_two.state, True, 1.3, config)

        self.assertTrue(emitted.emit_click)
        self.assertFalse(release_one.state.armed)
        self.assertTrue(release_two.state.armed)
        self.assertTrue(emitted_again.emit_click)

    def test_click_debounce_respects_cooldown(self):
        config = ClickDebounceConfig(
            stable_frames_required=1, release_frames_required=1, cooldown_seconds=1.0
        )
        emitted = update_click_debounce(ClickDebounceState(), True, 1.0, config)
        released = update_click_debounce(emitted.state, False, 1.1, config)
        too_soon = update_click_debounce(released.state, True, 1.5, config)

        self.assertTrue(emitted.emit_click)
        self.assertFalse(too_soon.emit_click)

    def test_debounce_ablation_and_full_improved_modes_are_selectable(self):
        config = load_config(CONFIG_PATH)
        debounce_plan = build_runtime_plan(config, condition_name="debounce_only")
        improved_plan = build_runtime_plan(config, condition_name="improved")

        self.assertTrue(debounce_plan.metadata["debounce_enabled"])
        self.assertFalse(debounce_plan.metadata["calibration_enabled"])
        self.assertEqual(debounce_plan.metadata["smoothing_strategy"], "fixed")
        self.assertTrue(improved_plan.metadata["debounce_enabled"])
        self.assertTrue(improved_plan.metadata["calibration_enabled"])
        self.assertEqual(improved_plan.metadata["smoothing_strategy"], "adaptive")

    def test_debounce_parameters_are_in_run_metadata(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, condition_name="debounce_only")
        debounce_config = debounce_config_from_settings(config.debounce)

        self.assertEqual(plan.metadata["debounce_parameters"]["cooldown_seconds"], 0.35)
        self.assertEqual(debounce_config.stable_frames_required, 2)

    def test_calibration_captures_comfortable_tracking_region(self):
        bounds = calibrate_bounds(
            [Point(120, 140), Point(420, 360)], CalibrationConfig(margin_px=20)
        )

        self.assertEqual(bounds.left, 100)
        self.assertEqual(bounds.top, 120)
        self.assertEqual(bounds.right, 440)
        self.assertEqual(bounds.bottom, 380)

    def test_cursor_mapping_uses_calibrated_bounds_when_enabled(self):
        fallback = default_camera_bounds(640, 480)
        calibrated = Bounds(left=100, top=100, right=500, bottom=400)

        selected = select_mapping_bounds(True, calibrated, fallback)
        mapped = map_point_to_output(Point(300, 250), selected, 1000, 600)

        self.assertEqual(selected, calibrated)
        self.assertEqual(mapped, Point(500, 300))

    def test_cursor_mapping_falls_back_without_calibration(self):
        fallback = Bounds(left=0, top=0, right=100, bottom=100)
        calibrated = Bounds(left=20, top=20, right=80, bottom=80)

        selected = select_mapping_bounds(False, calibrated, fallback)

        self.assertEqual(selected, fallback)

    def test_adaptive_smoothing_preserves_large_movement_responsiveness(self):
        previous = Point(0, 0)
        small_target = Point(10, 0)
        large_target = Point(300, 0)
        config = SmoothingConfig(
            min_factor=2, max_factor=10, fast_movement_threshold_px=300
        )

        small_step = adaptive_smooth(previous, small_target, config)
        large_step = adaptive_smooth(previous, large_target, config)

        self.assertLess(small_step.x, 2)
        self.assertGreater(large_step.x, 100)

    def test_ablation_modes_for_smoothing_and_calibration_are_selectable(self):
        config = load_config(CONFIG_PATH)
        smoothing_plan = build_runtime_plan(config, condition_name="smoothing_only")
        calibration_plan = build_runtime_plan(config, condition_name="calibration_only")

        self.assertEqual(smoothing_plan.metadata["smoothing_strategy"], "adaptive")
        self.assertFalse(smoothing_plan.metadata["calibration_enabled"])
        self.assertEqual(calibration_plan.metadata["smoothing_strategy"], "fixed")
        self.assertTrue(calibration_plan.metadata["calibration_enabled"])

    def test_apply_smoothing_dispatches_strategy(self):
        previous = Point(0, 0)
        target = Point(70, 0)

        fixed = apply_smoothing(
            "fixed", previous, target, SmoothingConfig(fixed_factor=7)
        )
        none = apply_smoothing("none", previous, target)

        self.assertEqual(fixed, Point(10, 0))
        self.assertEqual(none, target)

    def test_all_comparison_conditions_are_selectable_in_same_benchmark(self):
        config = load_config(CONFIG_PATH)
        condition_names = [
            "baseline",
            "smoothing_only",
            "debounce_only",
            "calibration_only",
            "improved",
        ]

        plans = [
            build_runtime_plan(config, mode_name="benchmark", condition_name=name)
            for name in condition_names
        ]

        self.assertEqual([plan.condition for plan in plans], condition_names)
        self.assertTrue(all(plan.mode == "benchmark" for plan in plans))

    def test_comparison_report_compares_multiple_saved_sessions(self):
        config = load_config(CONFIG_PATH)
        baseline_plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="baseline"
        )
        improved_plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="improved"
        )
        state = start_current_trial(
            create_point_click_benchmark(config.benchmark), 10.0
        )
        target = state.current_target
        self.assertIsNotNone(target)
        state = register_click(state, target.x, target.y, 11.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_paths = persist_benchmark_session(
                state, config, baseline_plan, output_root=Path(tmpdir)
            )
            improved_paths = persist_benchmark_session(
                state, config, improved_plan, output_root=Path(tmpdir)
            )
            comparison = generate_comparison_report(
                [baseline_paths.session_dir, improved_paths.session_dir]
            )
            content = comparison.report_path.read_text(encoding="utf-8")

        self.assertIn("baseline", content)
        self.assertIn("improved", content)
        self.assertIn("Do not claim general mouse-replacement superiority", content)

    def test_cli_compare_sessions_generates_report(self):
        config = load_config(CONFIG_PATH)
        baseline_plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="baseline"
        )
        improved_plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="improved"
        )
        state = create_point_click_benchmark(config.benchmark)

        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_paths = persist_benchmark_session(
                state, config, baseline_plan, output_root=Path(tmpdir)
            )
            improved_paths = persist_benchmark_session(
                state, config, improved_plan, output_root=Path(tmpdir)
            )
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "--compare-sessions",
                        str(baseline_paths.session_dir),
                        str(improved_paths.session_dir),
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("Benchmark comparison generated", output.getvalue())

    def test_tasks_model_path_resolves_inside_project_root(self):
        path = resolve_model_path("models/hand_landmarker.task", Path("/tmp/project"))

        self.assertEqual(path, Path("/tmp/project/models/hand_landmarker.task"))

    def test_tasks_backend_metadata_exposes_model_state(self):
        config = load_config(CONFIG_PATH)

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata = build_tasks_backend_metadata(config, Path(tmpdir))

        self.assertEqual(metadata.api_family, "mediapipe_tasks")
        self.assertEqual(metadata.backend, "hand_landmarker")
        self.assertFalse(metadata.model_exists)
        self.assertIn("hand_landmarker.task", metadata.model_path)

    def test_tasks_model_download_supports_file_url_for_reproducible_setup(self):
        config = load_config(CONFIG_PATH)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "source.task"
            source.write_bytes(b"fake-model")
            test_config = replace(
                config,
                backend=replace(
                    config.backend,
                    model_path="models/hand_landmarker.task",
                    model_url=source.as_uri(),
                ),
            )

            model_path = download_hand_landmarker_model(test_config, root)

            self.assertEqual(model_path.read_bytes(), b"fake-model")

    def test_tasks_model_missing_error_explains_download_command(self):
        config = load_config(CONFIG_PATH)

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            self.assertRaisesRegex(BackendError, "--download-model"),
        ):
            ensure_hand_landmarker_model(config, Path(tmpdir))

    # Real Mouse Runtime tests

    def test_pause_toggle_activates_after_hold_threshold(self):
        from ai_virtual_mouse_experimental.hand_control_pipeline import (
            PauseToggleState,
            update_pause_toggle,
        )

        state = PauseToggleState(toggle_threshold_frames=3)

        result = update_pause_toggle(state, open_palm_active=True)
        self.assertFalse(result.toggled)
        self.assertFalse(result.state.paused)

        result = update_pause_toggle(result.state, open_palm_active=True)
        self.assertFalse(result.toggled)

        result = update_pause_toggle(result.state, open_palm_active=True)
        self.assertTrue(result.toggled)
        self.assertTrue(result.state.paused)

    def test_pause_toggle_resets_after_release(self):
        from ai_virtual_mouse_experimental.hand_control_pipeline import (
            PauseToggleState,
            update_pause_toggle,
        )

        paused = PauseToggleState(holding=True, hold_frames=5, paused=True)

        result = update_pause_toggle(paused, open_palm_active=False)

        self.assertFalse(result.state.holding)
        self.assertEqual(result.state.hold_frames, 0)
        self.assertTrue(result.state.paused)

    def test_safety_corner_failsafe_triggers_after_threshold(self):
        from ai_virtual_mouse_experimental.hand_control_pipeline import (
            SafetyState,
            check_safety,
        )

        state = SafetyState(corner_threshold_frames=3)

        result = check_safety(state, cursor_x=0, cursor_y=0)
        self.assertFalse(result.quit_requested)

        result = check_safety(result, cursor_x=0, cursor_y=0)
        self.assertFalse(result.quit_requested)

        result = check_safety(result, cursor_x=0, cursor_y=0)
        self.assertTrue(result.quit_requested)

    def test_safety_corner_failsafe_checks_all_screen_edges(self):
        from ai_virtual_mouse_experimental.hand_control_pipeline import (
            SafetyState,
            check_safety,
        )

        state = SafetyState(corner_threshold_frames=1)

        self.assertTrue(
            check_safety(
                state, cursor_x=1919, cursor_y=500, screen_width=1920
            ).quit_requested
        )
        self.assertTrue(
            check_safety(
                state, cursor_x=500, cursor_y=1079, screen_height=1080
            ).quit_requested
        )
        self.assertFalse(
            check_safety(
                state,
                cursor_x=960,
                cursor_y=540,
                screen_width=1920,
                screen_height=1080,
            ).quit_requested
        )

    def test_real_mouse_uses_index_middle_pinch_distance(self):
        from ai_virtual_mouse_experimental.hand_tracker import _index_middle_distance

        points = [Point(0, 0) for _ in range(21)]
        points[4] = Point(999, 999)
        points[8] = Point(10, 10)
        points[12] = Point(13, 14)

        self.assertEqual(_index_middle_distance(points), 5.0)

    def test_real_mouse_metadata_includes_safety_controls(self):
        from ai_virtual_mouse_experimental.real_mouse_runtime import (
            build_real_mouse_metadata,
        )

        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, mode_name="demo", allow_real_mouse=True)

        metadata = build_real_mouse_metadata(config, plan)

        self.assertIn("safety_controls", metadata)
        self.assertEqual(
            metadata["safety_controls"],
            ["keyboard_quit", "pause_toggle", "corner_failsafe"],
        )

    def test_real_mouse_metadata_records_backend_preference(self):
        from ai_virtual_mouse_experimental.real_mouse_runtime import (
            build_real_mouse_metadata,
        )

        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, mode_name="demo", allow_real_mouse=True)

        metadata = build_real_mouse_metadata(config, plan)

        self.assertEqual(metadata["backend_preference"], "mediapipe_tasks")
        self.assertTrue(metadata["backend_fallback_allowed"])

    def test_hand_tracking_result_records_backend_and_fallback(self):
        from ai_virtual_mouse_experimental.hand_tracker import HandTrackingResult

        result = HandTrackingResult(
            success=False,
            backend_used="mediapipe_solutions",
            fallback_reason="model not found",
        )

        self.assertEqual(result.backend_used, "mediapipe_solutions")
        self.assertEqual(result.fallback_reason, "model not found")

    def test_hand_control_pipeline_exposes_shared_interface(self):
        from ai_virtual_mouse_experimental.hand_tracker import HandTrackingResult

        # Verify hand_input_from_tracking works
        result = HandTrackingResult(
            landmarks=[Point(0, 0)] * 21,
            fingers_up=[0, 1, 0, 0, 0],
            pinch_distance_px=50.0,
            index_middle_vertical_delta_px=0.0,
            success=True,
            backend_used="mediapipe_tasks",
        )
        hand = hand_input_from_tracking(result, GestureEngineConfig())
        self.assertTrue(hand.index)
        self.assertFalse(hand.middle)

        # Verify HandControlFrame dataclass
        frame = HandControlFrame(
            cursor_target=Point(100, 200),
            click_fired=True,
            paused=False,
            gesture_name="click",
            feedback_label="Click",
            feedback_color=(76, 175, 80),
            backend_used="mediapipe_tasks",
            fallback_reason=None,
            fps=30.0,
            safety_triggered=False,
            hand_detected=True,
        )
        self.assertEqual(frame.cursor_target, Point(100, 200))
        self.assertTrue(frame.click_fired)
        self.assertEqual(frame.gesture_name, "click")

    def test_benchmark_shell_accepts_hand_input_flag(self):
        """Verify benchmark shell function signature accepts hand_input parameter."""
        import inspect

        sig = inspect.signature(run_pygame_benchmark_shell)
        self.assertIn("hand_input", sig.parameters)
        self.assertEqual(sig.parameters["hand_input"].default, False)

    def test_pipeline_baseline_gesture_profile_uses_tutorial_behavior(self):
        move = _classify_baseline_as_gesture_result(
            GestureInput(index=True), GestureEngineConfig()
        )
        click = _classify_baseline_as_gesture_result(
            GestureInput(index=True, middle=True, pinch_distance_px=20),
            GestureEngineConfig(),
        )
        idle = _classify_baseline_as_gesture_result(
            GestureInput(index=True, middle=True, ring=True, pinky=True),
            GestureEngineConfig(),
        )

        self.assertEqual(move.name, "move")
        self.assertTrue(move.cursor_enabled)
        self.assertEqual(click.name, "click")
        self.assertTrue(click.click)
        # Baseline does NOT support pause
        self.assertEqual(idle.name, "idle")
        self.assertFalse(idle.paused)

    def test_pipeline_technical_metrics_compute_correctly(self):
        self.assertEqual(_compute_jitter([]), 0.0)
        self.assertEqual(_compute_jitter([5.0]), 0.0)
        jitter = _compute_jitter([1.0, 3.0, 1.0, 3.0])
        self.assertAlmostEqual(jitter, 1.0, places=5)


    def test_hand_frame_updates_simulated_benchmark_without_os_mouse(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(
            config, mode_name="benchmark", condition_name="baseline"
        )
        state = create_benchmark_shell_state(config, plan)
        benchmark = start_current_trial(
            create_point_click_benchmark(config.benchmark), 1.0
        )
        target = benchmark.current_target
        self.assertIsNotNone(target)
        frame = HandControlFrame(
            cursor_target=Point(target.x, target.y),
            click_fired=True,
            paused=False,
        )

        updated_state, updated_benchmark = apply_hand_frame_to_benchmark(
            state, benchmark, frame, 2.0
        )

        self.assertEqual(updated_state.cursor.x, target.x)
        self.assertEqual(updated_state.cursor.y, target.y)
        self.assertEqual(len(updated_benchmark.results), 1)
        self.assertTrue(updated_benchmark.results[0].hit)
        self.assertFalse(updated_state.controls_real_mouse)

    def test_report_includes_hand_input_metadata_and_metrics(self):
        metadata = {
            "session_id": "session-test",
            "condition": "improved",
            "backend": "mediapipe_tasks",
            "mode": "benchmark",
            "created_at_utc": "20260528T000000Z",
            "benchmark": {
                "name": "point_click_grid",
                "target_count": 1,
                "target_radius": 24,
                "window_width": 960,
                "window_height": 640,
                "random_seed": 1,
            },
            "hand_input": {
                "gesture_profile": "simple",
                "configured_backend": "mediapipe_tasks",
                "backend_used": "mediapipe_tasks",
                "fallback_reason": None,
                "smoothing_strategy": "adaptive",
                "debounce_enabled": True,
                "calibration_enabled": True,
                "technical_metrics": {
                    "cursor_path_length_px": 123.4,
                    "mean_fps": 30.0,
                    "jitter_estimate_px": 2.5,
                    "movement_sample_count": 7,
                },
            },
        }
        metrics = BenchmarkMetrics(
            total_trials=1,
            hit_count=1,
            miss_count=0,
            hit_rate=1.0,
            false_clicks=0,
            click_count=1,
            mean_completion_time_s=1.0,
            median_completion_time_s=1.0,
            jitter_estimate_px=0.0,
            fps_mean=None,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.md"
            plot = Path(tmpdir) / "completion_times.svg"
            generate_markdown_report(metadata, metrics, plot, output)
            report = output.read_text(encoding="utf-8")

        self.assertIn("## Hand Input", report)
        self.assertIn("Backend used: `mediapipe_tasks`", report)
        self.assertIn("Cursor path length", report)

if __name__ == "__main__":
    unittest.main()
