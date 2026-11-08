import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import context_hook as hook


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        self.repo = self.root / "shared"
        for name in ("agent-workflow", "go-clean-architecture", "go-code-style", "go-concurrency", "retro"):
            file = self.repo / "skills" / name / "SKILL.md"
            file.parent.mkdir(parents=True)
            file.write_text("Instructions for " + name, encoding="utf-8")

    def context(self, prompt="", **kwargs):
        event = dict(hook_event_name="UserPromptSubmit", cwd=str(self.project), prompt=prompt)
        event.update(kwargs)
        return hook.build_context(event, self.repo)["hookSpecificOutput"]["additionalContext"]

    def config(self, value, name=".agent-workflow.json"):
        (self.project / name).write_text(json.dumps(value), encoding="utf-8")

    def test_full_skill_text_is_delivered(self):
        self.assertIn("Instructions for agent-workflow", self.context())
        self.assertNotIn("Instructions for go-code-style", self.context())

    def test_go_markers_do_not_select_skills_from_nested_directory(self):
        for marker in ("go.mod", "go.work"):
            with self.subTest(marker=marker):
                project = self.project / marker
                project.mkdir()
                (project / ".git").mkdir()
                (project / marker).write_text("", encoding="utf-8")
                child = project / "cmd/api"
                child.mkdir(parents=True)
                self.assertNotIn("Instructions for go-code-style", self.context(cwd=str(child)))
                self.assertNotIn("Instructions for go-clean-architecture", self.context(cwd=str(child)))
                self.assertNotIn("Instructions for go-concurrency", self.context("Fix goroutines", cwd=str(child)))

    def test_clean_architecture_is_loaded_when_configured(self):
        for config in ({"always": ["go-clean-architecture"]},
                       {"routes": {"go-clean-architecture": ["clean architecture"]}}):
            self.config(config)
            with self.subTest(config=config):
                self.assertIn("Instructions for go-clean-architecture", self.context("Clean Architecture"))

    def test_configured_concurrency_is_loaded_without_a_go_marker(self):
        self.config({"always": ["go-concurrency"]})
        self.assertIn("Instructions for go-concurrency", self.context("Rename a variable"))

    def test_concurrency_prompt_does_not_select_skill_without_configuration(self):
        (self.project / "go.mod").write_text("", encoding="utf-8")
        self.assertNotIn("Instructions for go-concurrency", self.context("Fix goroutines"))

    def test_project_settings_do_not_leak_from_parent(self):
        (self.root / ".agent-workflow.json").write_text('{"always":["retro"]}', encoding="utf-8")
        self.assertNotIn("Instructions for retro", self.context())

    def test_routes_match_word_starts_and_casefold(self):
        self.config({"routes": {"retro": ["ретро"]}})
        self.assertIn("Instructions for retro", self.context("Проведи РЕТРОспективу"))
        self.assertNotIn("Instructions for retro", self.context("антиретро"))

    def test_explicit_retro_and_deduplication(self):
        self.config({"always": ["agent-workflow", "retro"], "routes": {"retro": ["retro"]}})
        self.assertEqual(self.context("$retro").count("Instructions for retro"), 1)
        self.assertIn("Instructions for retro", self.context("/retro"))

    def test_explicit_retro_is_not_loaded_without_configuration(self):
        for prompt in ("$retro", "/retro"):
            with self.subTest(prompt=prompt):
                self.assertNotIn("Instructions for retro", self.context(prompt))

    def test_local_settings_replace_shared_config(self):
        self.config({"always": ["go-code-style"]})
        self.config({"always": []}, ".agent-workflow.local.json")
        self.assertNotIn("Instructions for go-code-style", self.context())
        self.assertIn("Instructions for agent-workflow", self.context())

    def test_invalid_config_and_missing_skills_fail_explicitly(self):
        cases = [{"unknown": []}, {"always": "retro"}, {"always": ["../retro"]},
                 {"routes": []}, {"routes": {"retro": []}}, {"routes": {"retro": [""]}},
                 {"routes": {"../retro": ["retro"]}}, {"always": ["missing"]},
                 {"routes": {"missing": ["unused"]}}, {"always": ["go-checks"]},
                 {"routes": {"go-checks": ["go"]}}]
        for config in cases:
            self.config(config)
            with self.subTest(config=config), self.assertRaises((ValueError, OSError)):
                self.context()

    def test_removed_go_skill_gives_actionable_error(self):
        for config in ({"always": ["go-coding"]}, {"routes": {"go-coding": ["go"]}}):
            self.config(config)
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, "go-coding.*go-clean-architecture.*go-code-style"):
                self.context()

    def test_renamed_architecture_skill_gives_actionable_error(self):
        for config in ({"always": ["go-architecture"]}, {"routes": {"go-architecture": ["unused"]}}):
            self.config(config)
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, "go-architecture.*go-clean-architecture"):
                self.context()

    def test_invalid_event(self):
        for event in ([], {}, {"hook_event_name": "Stop"},
                      {"hook_event_name": "SessionStart", "cwd": str(self.project), "prompt": []}):
            with self.subTest(event=event), self.assertRaises(ValueError):
                hook.build_context(event, self.repo)

    def test_context_cap_prevents_truncated_skill_delivery(self):
        file = self.repo / "skills/agent-workflow/SKILL.md"
        file.write_text("я" * hook.MAX_CONTEXT_BYTES, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "context limit"):
            self.context()

    def test_both_event_shapes(self):
        for event in ("SessionStart", "UserPromptSubmit"):
            output = hook.build_context({"hook_event_name": event, "cwd": str(self.project)}, self.repo)
            self.assertEqual(output["hookSpecificOutput"]["hookEventName"], event)

    def test_cli_success_and_invalid_input(self):
        path = Path(hook.__file__)
        payload = json.dumps({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        good = subprocess.run([sys.executable, str(path)], input=payload, text=True, capture_output=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("additionalContext", json.loads(good.stdout)["hookSpecificOutput"])
        for payload in ("bad json", "[]", "x" * 65537):
            bad = subprocess.run([sys.executable, str(path)], input=payload, text=True, capture_output=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("NOT loaded", json.loads(bad.stdout)["systemMessage"])


if __name__ == "__main__":
    unittest.main()
