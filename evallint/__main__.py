"""Command line entry point: python3 -m evallint <cases.jsonl>."""

from __future__ import annotations

import sys

from .lint import ERROR, lint

EXIT_ERRORS = 1
EXIT_USAGE = 2


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python3 -m evallint <cases.jsonl>", file=sys.stderr)
        return EXIT_USAGE
    try:
        with open(argv[0], encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as exc:
        print(f"cannot read {argv[0]}: {exc.strerror}", file=sys.stderr)
        return EXIT_USAGE
    findings = lint(lines)
    for f in findings:
        print(f"{f.severity}: [{f.code}] {f.message}")
    errors = sum(f.severity == ERROR for f in findings)
    print(f"{len(findings)} finding(s), {errors} error(s)")
    return EXIT_ERRORS if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
