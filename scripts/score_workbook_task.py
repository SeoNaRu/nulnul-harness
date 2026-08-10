#!/usr/bin/env python3
"""Compare an offline workbook candidate with the public expected result."""

import argparse
import json
from pathlib import Path


SECTIONS = ("leads", "needs_second_review", "research_log", "exclusions")


def score(expected, candidate):
    section_matches = {
        section: isinstance(candidate, dict) and candidate.get(section) == expected[section]
        for section in SECTIONS
    }
    key_order_matches = isinstance(candidate, dict) and tuple(candidate) == SECTIONS
    return {
        "passed": key_order_matches and all(section_matches.values()),
        "key_order_matches": key_order_matches,
        "section_matches": section_matches,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("expected", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    result = score(expected, candidate)
    print(json.dumps(result, indent=2))
    raise SystemExit(not result["passed"])


if __name__ == "__main__":
    main()
