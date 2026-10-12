import contextlib
import io
import unittest
from pathlib import Path

from evallint.__main__ import EXIT_ERRORS, EXIT_USAGE, main

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def run(*args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(args))
    return code, out.getvalue()


class CliTests(unittest.TestCase):
    def test_clean_set_exits_zero(self):
        code, out = run(str(FIXTURES / "good.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("0 finding(s)", out)

    def test_defective_set_exits_one(self):
        code, out = run(str(FIXTURES / "bad.jsonl"))
        self.assertEqual(code, EXIT_ERRORS)
        self.assertIn("[duplicate-id]", out)

    def test_missing_file_is_a_usage_error(self):
        self.assertEqual(run(str(FIXTURES / "nope.jsonl"))[0], EXIT_USAGE)

    def test_no_arguments_is_a_usage_error(self):
        self.assertEqual(run()[0], EXIT_USAGE)


if __name__ == "__main__":
    unittest.main()
