"""Report artifacts are replaced only after a complete write succeeds."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.reports import write_text_atomic


class AtomicReportWriteTests(unittest.TestCase):
    def test_successful_write_replaces_existing_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            report.write_text("old\n", encoding="utf-8")

            write_text_atomic(report, "new\n")

            self.assertEqual(report.read_text(encoding="utf-8"), "new\n")
            self.assertEqual(list(Path(directory).glob(".report.json.*")), [])

    def test_failed_replace_preserves_existing_artifact_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "REPORT.md"
            report.write_text("previous report\n", encoding="utf-8")

            with patch("src.reports.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    write_text_atomic(report, "incomplete replacement\n")

            self.assertEqual(report.read_text(encoding="utf-8"), "previous report\n")
            self.assertEqual(list(Path(directory).glob(".REPORT.md.*")), [])


if __name__ == "__main__":
    unittest.main()
