import contextlib
from concurrent.futures import ThreadPoolExecutor
import io
from pathlib import Path
import tempfile
import unittest

from scripts import journal


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "data/journal.sqlite"

    def add(self, **kwargs):
        args = dict(project="api", area="http", task_id="42", task="Timeout", rounds=0,
                    date="2026-11-03")
        args.update(kwargs)
        return journal.add(self.db, **args)

    def test_roundtrip_unicode_and_filters(self):
        self.add(task="Обработка ошибок", rounds=1, causes=["verification:Нет теста"],
                 changes=["Added a test"], evidence=["test_handler_timeout"])
        self.add(project="worker", task_id="43")
        rows = journal.records(self.db, "api", "http")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["task"], "Обработка ошибок")
        self.assertEqual(rows[0]["causes"][0]["kind"], "verification")
        self.assertEqual(journal.records(self.db, "api", "missing"), [])

    def test_duplicate_task_is_rejected_without_extra_row(self):
        self.add()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.add(area="other")
        self.assertEqual(len(journal.records(self.db)), 1)

    def test_same_task_id_in_another_project_is_allowed(self):
        self.add()
        self.add(project="worker")
        self.assertEqual(len(journal.records(self.db)), 2)

    def test_invalid_retro_does_not_create_database(self):
        cases = [dict(rounds=-1), dict(rounds=1), dict(causes=["intent:Changed"]),
                 dict(rounds=1, causes=["bad:Reason"], changes=["Fix"], evidence=["Test"]),
                 dict(rounds=1, causes=["tooling:Failure"], changes=["Fix"]),
                 dict(rounds=1, causes=["tooling:Failure"], evidence=["Test"]),
                 dict(rounds=1, causes=["tooling: "], changes=["Fix"], evidence=["Test"]),
                 dict(date="2026-02-30"), dict(project=" "), dict(outcome="unknown"),
                 dict(changes=[" "])]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.add(**args)
        self.assertFalse(self.db.exists())

    def test_first_pass_and_abandoned_tasks(self):
        self.add(outcome="abandoned")
        self.assertEqual(journal.records(self.db)[0]["outcome"], "abandoned")

    def test_sql_input_is_data(self):
        name = "api'; DROP TABLE tasks; --"
        self.add(project=name)
        self.assertEqual(len(journal.records(self.db, name)), 1)
        self.assertEqual(len(journal.records(self.db)), 1)

    def test_empty_read_does_not_create_database(self):
        self.assertEqual(journal.records(self.db), [])
        self.assertFalse(self.db.parent.exists())
        self.assertEqual(journal.summarize([]), [])
        self.assertEqual(journal.change_windows([]), [])

    def test_stats_and_change_windows_keep_projects_separate(self):
        self.add(rounds=2, causes=["intent:New scope", "verification:Missed timeout"],
                 changes=["Add test"], evidence=["Test"])
        self.add(task_id="43")
        self.add(project="worker", rounds=1, causes=["tooling:Build failed"],
                 changes=["Fix build"], evidence=["Build"])
        rows = journal.records(self.db)
        stats = journal.summarize(rows)
        self.assertEqual(stats[0]["tasks"], 2)
        self.assertEqual(stats[0]["mean_rounds"], 1)
        self.assertEqual(stats[0]["intent_returns"], 1)
        windows = journal.change_windows(rows)
        self.assertEqual(windows[0]["before_mean"], 2)
        self.assertEqual(windows[0]["after_mean"], 0)
        self.assertEqual(windows[0]["after_n"], 1)
        self.assertIsNone(windows[1]["after_mean"])

    def test_cli_error_is_nonzero(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code = journal.main(["--db", str(self.db), "add", "--project", "api", "--area", "http",
                                 "--task-id", "42", "--task", "Timeout", "--rounds", "1"])
        self.assertEqual(code, 1)
        self.assertFalse(self.db.exists())

    def test_parallel_sessions_preserve_all_records(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(self.add, task_id=str(i)) for i in range(12)]
            ids = [future.result() for future in futures]
        self.assertEqual(len(set(ids)), 12)
        self.assertEqual(len(journal.records(self.db)), 12)

    def test_parallel_duplicate_has_one_winner(self):
        def attempt():
            try:
                self.add()
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: attempt(), range(4)))
        self.assertEqual(sum(results), 1)
        self.assertEqual(len(journal.records(self.db)), 1)


if __name__ == "__main__":
    unittest.main()
