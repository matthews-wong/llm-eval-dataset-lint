"""Parse an eval set and report problems with it."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass

REQUIRED_FIELDS = ("id", "input", "expected")
MIN_CASES = 20
MAX_LABEL_SHARE = 0.7

ERROR = "error"
WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str


def normalise(text: str) -> str:
    return " ".join(text.lower().split())


def parse(lines: list[str]) -> tuple[list[dict], list[Finding]]:
    """Return the valid case objects and a finding for each malformed line."""
    cases: list[dict] = []
    findings: list[Finding] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            findings.append(Finding("bad-json", ERROR, f"line {number}: {exc.msg}"))
            continue
        if not isinstance(case, dict):
            findings.append(Finding("bad-json", ERROR, f"line {number}: expected an object, got {type(case).__name__}"))
            continue
        missing = [f for f in REQUIRED_FIELDS if not isinstance(case.get(f), str) or not case[f].strip()]
        if missing:
            ident = case.get("id", f"line {number}")
            findings.append(Finding("missing-field", ERROR, f"{ident}: missing or blank {', '.join(missing)}"))
            continue
        cases.append(case)
    return cases, findings


def check_duplicates(cases: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    ids = Counter(c["id"] for c in cases)
    for ident, count in ids.items():
        if count > 1:
            findings.append(Finding("duplicate-id", ERROR, f"id {ident!r} appears {count} times"))
    by_input: dict[str, list[dict]] = {}
    for case in cases:
        by_input.setdefault(normalise(case["input"]), []).append(case)
    for group in by_input.values():
        if len(group) < 2:
            continue
        names = ", ".join(c["id"] for c in group)
        labels = {normalise(c["expected"]) for c in group}
        if len(labels) > 1:
            findings.append(Finding("conflicting-label", ERROR, f"same input, different expected: {names}"))
        else:
            findings.append(Finding("duplicate-input", WARNING, f"same input: {names}"))
    return findings


def check_balance(cases: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    if len(cases) < MIN_CASES:
        findings.append(Finding("tiny-set", WARNING, f"{len(cases)} cases, want at least {MIN_CASES}"))
        return findings
    labels = Counter(normalise(c["expected"]) for c in cases)
    label, count = labels.most_common(1)[0]
    share = count / len(cases)
    if share > MAX_LABEL_SHARE:
        findings.append(Finding("label-imbalance", WARNING, f"label {label!r} covers {share:.0%} of {len(cases)} cases"))
    return findings


def lint(lines: list[str]) -> list[Finding]:
    cases, findings = parse(lines)
    return findings + check_duplicates(cases) + check_balance(cases)
