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
benchmark_logging_module = import_module("ai_virtual_mouse_experimental.benchmark_logging")
benchmark_report_module = import_module("ai_virtual_mouse_experimental.benchmark_report")
benchmark_shell_module = import_module("ai_virtual_mouse_experimental.benchmark_shell")
cli_module = import_module("ai_virtual_mouse_experimental.cli")
config_module = import_module("ai_virtual_mouse_experimental.config")
gesture_engine_module = import_module("ai_virtual_mouse_experimental.gesture_engine")
tasks_backend_module = import_module("ai_virtual_mouse_experimental.tasks_backend")

StartupError = app_module.StartupError
build_runtime_plan = app_module.build_runtime_plan
build_baseline_metadata = baseline_module.build_baseline_metadata
classify_baseline_gesture = baseline_module.classify_baseline_gesture
benchmark_instruction_lines = benchmark_shell_module.benchmark_instruction_lines
create_benchmark_shell_state = benchmark_shell_module.create_benchmark_shell_state
move_simulated_cursor = benchmark_shell_module.move_simulated_cursor
create_point_click_benchmark = benchmark_grid_module.create_point_click_benchmark
generate_grid_targets = benchmark_grid_module.generate_grid_targets
register_click = benchmark_grid_module.register_click
start_current_trial = benchmark_grid_module.start_current_trial
summarize_benchmark = benchmark_grid_module.summarize_benchmark
format_output_paths = benchmark_logging_module.format_output_paths
persist_benchmark_session = benchmark_logging_module.persist_benchmark_session
compute_metrics = benchmark_report_module.compute_metrics
generate_report_from_session = benchmark_report_module.generate_report_from_session
load_trials_csv = benchmark_report_module.load_trials_csv
main = cli_module.main
ConfigError = config_module.ConfigError
load_config = config_module.load_config
GestureEngineConfig = gesture_engine_module.GestureEngineConfig
GestureInput = gesture_engine_module.GestureInput
classify_improved_gesture = gesture_engine_module.classify_improved_gesture
config_from_settings = gesture_engine_module.config_from_settings
feedback_style = gesture_engine_module.feedback_style
build_tasks_backend_metadata = tasks_backend_module.build_tasks_backend_metadata
download_hand_landmarker_model = tasks_backend_module.download_hand_landmarker_model
ensure_hand_landmarker_model = tasks_backend_module.ensure_hand_landmarker_model
resolve_model_path = tasks_backend_module.resolve_model_path
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
        plan = build_runtime_plan(config, mode_name="benchmark", condition_name="baseline")
        state = start_current_trial(create_point_click_benchmark(config.benchmark), 10.0)
        target = state.current_target
        self.assertIsNotNone(target)
        state = register_click(state, target.x, target.y, 12.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(state, config, plan, output_root=Path(tmpdir))
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
        plan = build_runtime_plan(config, mode_name="benchmark", condition_name="improved")
        state = create_point_click_benchmark(config.benchmark)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(state, config, plan, output_root=Path(tmpdir))
            metadata = json.loads(paths.metadata_path.read_text(encoding="utf-8"))

        self.assertEqual(metadata["condition"], "improved")
        self.assertEqual(metadata["backend"], "mediapipe_tasks")

    def test_benchmark_output_paths_are_printable(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, mode_name="benchmark")
        state = create_point_click_benchmark(config.benchmark)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(state, config, plan, output_root=Path(tmpdir))

        formatted = format_output_paths(paths)

        self.assertIn("metadata", formatted)
        self.assertIn("trials CSV", formatted)
        self.assertIn("report", formatted)

    def test_benchmark_metrics_and_report_are_generated_from_session(self):
        config = load_config(CONFIG_PATH)
        plan = build_runtime_plan(config, mode_name="benchmark", condition_name="baseline")
        state = start_current_trial(create_point_click_benchmark(config.benchmark), 10.0)
        target = state.current_target
        self.assertIsNotNone(target)
        state = register_click(state, 0, 0, 11.0)
        state = register_click(state, target.x, target.y, 13.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = persist_benchmark_session(state, config, plan, output_root=Path(tmpdir))
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
        plan = build_runtime_plan(config, mode_name="benchmark", condition_name="baseline")
        state = start_current_trial(create_point_click_benchmark(config.benchmark), 10.0)
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

    def test_gesture_engine_config_uses_project_settings(self):
        config = load_config(CONFIG_PATH)

        engine_config = config_from_settings(config.gesture)

        self.assertEqual(engine_config.click_threshold_px, config.gesture.click_threshold_px)

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


if __name__ == "__main__":
    unittest.main()
