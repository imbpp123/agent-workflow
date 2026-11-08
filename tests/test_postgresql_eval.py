import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "eval_postgresql.py"


class PostgreSQLEvalTests(unittest.TestCase):
    def run_eval(self, mode):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            fake = temp / "codex"
            fake.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
out = pathlib.Path(args[args.index("-o") + 1])
if "--output-schema" in args:
    mode = os.environ["FAKE_MODE"]
    if mode == "invalid":
        out.write_text("not json")
    else:
        out.write_text(json.dumps({"pass": mode == "pass", "reason": "test evidence"}))
else:
    prompt = args[-1]
    assert "expected_output" not in prompt and "assertions" not in prompt
    assert (pathlib.Path.cwd() / ".agents/skills/go-postgresql/SKILL.md").exists()
    out.write_text("Use pgxpool for PostgreSQL.")
''')
            fake.chmod(0o755)
            env = dict(os.environ, FAKE_MODE=mode, OPENAI_API_KEY="test-key", PATH=str(temp) + os.pathsep + os.environ.get("PATH", ""))
            return subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, env=env, capture_output=True, text=True)

    def test_pass(self):
        result = self.run_eval("pass")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_fail_is_nonzero(self):
        result = self.run_eval("fail")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stdout)

    def test_invalid_grader_output_is_nonzero(self):
        result = self.run_eval("invalid")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error", result.stderr.lower())

    def test_missing_key_fails_before_running_codex(self):
        env = dict(os.environ, OPENAI_API_KEY="")
        result = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OPENAI_API_KEY is required", result.stderr)


if __name__ == "__main__":
    unittest.main()
