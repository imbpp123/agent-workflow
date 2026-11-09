import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

from scripts import install


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workflow tests ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "target"
        self.target.mkdir()
        self.repo = self.root / "shared repo"
        file = self.repo / "skills/agent-workflow/SKILL.md"
        file.parent.mkdir(parents=True)
        file.write_text("Skill", encoding="utf-8")

    def write_config(self, value):
        path = self.target / ".codex/hooks.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_dry_run_does_not_write(self):
        result = install.install(self.target, self.repo)
        self.assertFalse(result["applied"])
        self.assertEqual(list(self.target.iterdir()), [])

    def test_cli_default_installs_skills_without_creating_hooks(self):
        script = install.ROOT / "scripts/install.py"
        run = subprocess.run(
            [sys.executable, str(script), "--project", str(self.target), "--apply"],
            capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIsNone(json.loads(run.stdout)["hooks"])
        self.assertTrue((self.target / ".agents/skills/retro/SKILL.md").is_file())
        self.assertFalse((self.target / ".codex").exists())

    def test_default_leaves_existing_hook_file_alone(self):
        path = self.write_config({"hooks": {"SessionStart": [{"hooks": [{"statusMessage": install.MARKER}]}]}})
        before = path.read_bytes()
        result = install.install(self.target, self.repo, apply=True)
        self.assertIsNone(result["hooks"])
        self.assertEqual(path.read_bytes(), before)

    def test_repeated_install_is_idempotent(self):
        install.install(self.target, self.repo, apply=True, with_hooks=True)
        path = self.target / ".codex/hooks.json"
        before = path.read_bytes()
        result = install.install(self.target, self.repo, apply=True, with_hooks=True)
        self.assertEqual(result["new_links"], [])
        self.assertEqual(path.read_bytes(), before)
        dest = self.target / ".agents/skills/agent-workflow"
        self.assertEqual(dest.resolve(), (self.repo / "skills/agent-workflow").resolve())

    def test_preserves_existing_hooks_and_other_fields(self):
        old = {"hooks": [{"type": "command", "command": "echo existing"}]}
        path = self.write_config({"description": "Existing hooks", "hooks": {"SessionStart": [old]}})
        install.install(self.target, self.repo, apply=True, with_hooks=True)
        config = json.loads(path.read_text())
        self.assertEqual(config["description"], "Existing hooks")
        self.assertEqual(config["hooks"]["SessionStart"][0], old)
        self.assertEqual(len(config["hooks"]["SessionStart"]), 2)

    def test_conflicting_skill_is_not_replaced_and_hook_not_written(self):
        dest = self.target / ".agents/skills/agent-workflow"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("Existing", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already exists"):
            install.install(self.target, self.repo, apply=True, with_hooks=True)
        self.assertEqual((dest / "SKILL.md").read_text(), "Existing")
        self.assertFalse((self.target / ".codex").exists())

    def test_broken_link_is_a_conflict(self):
        dest = self.target / ".agents/skills/agent-workflow"
        dest.parent.mkdir(parents=True)
        dest.symlink_to(self.root / "missing")
        with self.assertRaises(ValueError):
            install.install(self.target, self.repo, apply=True)
        self.assertTrue(dest.is_symlink())

    def test_obsolete_broken_skill_link_is_preserved(self):
        dest = self.target / ".agents/skills/go-coding"
        dest.parent.mkdir(parents=True)
        dest.symlink_to(self.root / "removed-go-coding")
        install.install(self.target, self.repo, apply=True)
        self.assertTrue(dest.is_symlink())
        self.assertFalse(dest.exists())
        self.assertTrue((self.target / ".agents/skills/agent-workflow").is_symlink())

    def test_invalid_hook_config_does_not_create_links(self):
        for config in ([], {"hooks": []}, {"hooks": {"SessionStart": {}}},
                       {"hooks": {"SessionStart": [None]}},
                       {"hooks": {"SessionStart": [{"hooks": [None]}]}}):
            path = self.write_config(config)
            before = path.read_bytes()
            with self.subTest(config=config), self.assertRaises(ValueError):
                install.install(self.target, self.repo, apply=True, with_hooks=True)
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse((self.target / ".agents").exists())

    def test_edited_owned_hook_is_not_silently_replaced(self):
        handler = {"statusMessage": install.MARKER, "type": "command", "command": "custom"}
        self.write_config({"hooks": {"SessionStart": [{"hooks": [handler]}]}})
        with self.assertRaisesRegex(ValueError, "differs"):
            install.install(self.target, self.repo, apply=True, with_hooks=True)

    def test_duplicate_owned_hooks_are_rejected(self):
        group = {"hooks": [{"statusMessage": install.MARKER}]}
        self.write_config({"hooks": {"SessionStart": [group, group]}})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            install.install(self.target, self.repo, apply=True, with_hooks=True)

    def test_command_quoting_handles_spaces_and_shell_characters(self):
        config = install.hook_config(self.target / "hooks.json", self.repo / "$(echo unsafe)")
        cmd = config["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertEqual(shlex.split(cmd), [sys.executable, str(self.repo / "$(echo unsafe)/scripts/context_hook.py")])

    def test_installed_command_delivers_real_skills(self):
        script = install.ROOT / "scripts/install.py"
        run = subprocess.run(
            [sys.executable, str(script), "--project", str(self.target), "--apply", "--with-hooks"],
            capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        hooks = self.target / ".codex/hooks.json"
        self.assertEqual(Path(json.loads(run.stdout)["hooks"]), hooks.resolve())
        config = json.loads(hooks.read_text())
        cmd = config["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        (self.target / "go.mod").write_text("module example.com/test\n", encoding="utf-8")
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "cwd": str(self.target), "prompt": "$retro"})
        run = subprocess.run(cmd, shell=True, input=payload, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        context = json.loads(run.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Skill: agent-workflow", context)
        for name in ("go-code-style", "go-clean-architecture", "go-concurrency", "retro"):
            self.assertNotIn("Skill: " + name, context)
        (self.target / ".agent-workflow.json").write_text(
            json.dumps({"always": ["go-code-style"], "routes": {"go-clean-architecture": ["clean architecture"]}}), encoding="utf-8")
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "cwd": str(self.target), "prompt": "Clean Architecture"})
        run = subprocess.run(cmd, shell=True, input=payload, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        context = json.loads(run.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Skill: go-code-style", context)
        self.assertIn("Skill: go-clean-architecture", context)
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "cwd": str(self.target), "prompt": "Fix goroutine leaks"})
        run = subprocess.run(cmd, shell=True, input=payload, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        context = json.loads(run.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Skill: go-code-style", context)
        self.assertNotIn("Skill: go-concurrency", context)


if __name__ == "__main__":
    unittest.main()
