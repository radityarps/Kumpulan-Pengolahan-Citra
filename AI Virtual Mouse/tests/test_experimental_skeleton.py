import sys
import unittest
from contextlib import redirect_stdout
from importlib import import_module
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

app_module = import_module("ai_virtual_mouse_experimental.app")
baseline_module = import_module("ai_virtual_mouse_experimental.baseline")
cli_module = import_module("ai_virtual_mouse_experimental.cli")
config_module = import_module("ai_virtual_mouse_experimental.config")

StartupError = app_module.StartupError
build_runtime_plan = app_module.build_runtime_plan
build_baseline_metadata = baseline_module.build_baseline_metadata
classify_baseline_gesture = baseline_module.classify_baseline_gesture
main = cli_module.main
ConfigError = config_module.ConfigError
load_config = config_module.load_config


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


if __name__ == "__main__":
    unittest.main()
