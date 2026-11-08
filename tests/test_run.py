"""Command-line selection keeps exploratory reports separate from saved artifacts."""
from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import MagicMock, patch

from src import run


class ReportCommandTests(unittest.TestCase):
    def test_named_report_prints_only_the_selected_query(self):
        pool = MagicMock()
        rows = [{"TotalBookings": 4}]
        with patch.object(run, "create_pool", return_value=pool), \
             patch.object(run, "initialize_database"), \
             patch.object(run, "seed_database"), \
             patch.object(run, "validate_data"), \
             patch.object(run, "create_procedures"), \
             patch.object(run, "run_report", return_value=rows) as selected, \
             patch.object(run, "write_report") as write_all, \
             patch("sys.argv", ["sales-report", "--show-report", "booking_count"]), \
             redirect_stdout(StringIO()) as output:
            run.main()

        selected.assert_called_once_with(pool, "booking_count")
        write_all.assert_not_called()
        self.assertIn("Booking Count", output.getvalue())
        self.assertIn("4", output.getvalue())

    def test_unknown_report_fails_before_connecting(self):
        with patch.object(run, "create_pool") as create_pool, \
             patch("sys.argv", ["sales-report", "--show-report", "invented"]), \
             redirect_stdout(StringIO()):
            with self.assertRaises(SystemExit) as error:
                run.main()

        self.assertEqual(error.exception.code, 2)
        create_pool.assert_not_called()

    def test_saved_and_interactive_report_modes_are_mutually_exclusive(self):
        with patch.object(run, "create_pool") as create_pool, \
             patch("sys.argv", ["sales-report", "--report", "--show-report", "summary"]), \
             redirect_stdout(StringIO()):
            with self.assertRaises(SystemExit) as error:
                run.main()

        self.assertEqual(error.exception.code, 2)
        create_pool.assert_not_called()


if __name__ == "__main__":
    unittest.main()
