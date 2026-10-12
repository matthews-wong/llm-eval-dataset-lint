import json
import unittest
from pathlib import Path

from evallint.lint import MIN_CASES, lint

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def codes(lines):
    return {f.code for f in lint(lines)}


def case(i, expected="x", text=None):
    return json.dumps({"id": f"c{i}", "input": text or f"question {i}", "expected": f"{expected}{i % 4}"})


class LintTests(unittest.TestCase):
    def test_good_fixture_has_no_findings(self):
        self.assertEqual(lint((FIXTURES / "good.jsonl").read_text().splitlines()), [])

    def test_bad_fixture_reports_every_defect(self):
        found = codes((FIXTURES / "bad.jsonl").read_text().splitlines())
        self.assertEqual(found, {"bad-json", "missing-field", "duplicate-id", "conflicting-label", "tiny-set"})

    def test_duplicate_input_with_same_label_is_a_warning(self):
        lines = [case(i) for i in range(MIN_CASES)] + [json.dumps({"id": "dup", "input": "QUESTION  1", "expected": "x1"})]
        self.assertIn("duplicate-input", codes(lines))
        self.assertNotIn("conflicting-label", codes(lines))

    def test_label_imbalance(self):
        lines = [json.dumps({"id": str(i), "input": f"q{i}", "expected": "yes"}) for i in range(MIN_CASES)]
        self.assertIn("label-imbalance", codes(lines))

    def test_blank_lines_are_ignored(self):
        self.assertNotIn("bad-json", codes(["", "  "]))

    def test_non_object_line(self):
        self.assertIn("bad-json", codes(["[1, 2]"]))


if __name__ == "__main__":
    unittest.main()
