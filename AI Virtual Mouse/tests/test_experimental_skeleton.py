from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest

from ai_virtual_mouse_experimental.app import StartupError, build_runtime_plan
from ai_virtual_mouse_experimental.cli import main
from ai_virtual_mouse_experimental.config import ConfigError, load_config


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


if __name__ == "__main__":
    unittest.main()
