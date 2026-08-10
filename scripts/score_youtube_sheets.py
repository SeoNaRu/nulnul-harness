#!/usr/bin/env python3
"""Score one YouTube-to-Sheets candidate output against a fixed fixture."""

import argparse
import json
from pathlib import Path


CATEGORIES = {"crypto", "stocks", "both"}


def score(fixture: dict, candidate: dict) -> dict:
    expected = {
        row["channel_id"]: row["category"]
        for row in fixture["expected"]
        if row["include"]
    }
    known_ids = {row["channel_id"] for row in fixture["expected"]}
    records = candidate.get("records", [])
    schema_errors = 0
    predicted = {}
    seen = set()
    duplicate_count = 0

    if not isinstance(records, list):
        records = []
        schema_errors += 1

    for row in records:
        if not isinstance(row, dict):
            schema_errors += 1
            continue
        channel_id = row.get("channel_id")
        category = row.get("category")
        if not isinstance(channel_id, str) or category not in CATEGORIES:
            schema_errors += 1
            continue
        if channel_id in seen:
            duplicate_count += 1
        seen.add(channel_id)
        predicted[channel_id] = category

    expected_ids = set(expected)
    predicted_ids = set(predicted)
    true_positives = len(expected_ids & predicted_ids)
    precision = true_positives / len(predicted_ids) if predicted_ids else 0.0
    recall = true_positives / len(expected_ids) if expected_ids else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    matched = expected_ids & predicted_ids
    classification_accuracy = (
        sum(predicted[channel_id] == expected[channel_id] for channel_id in matched) / len(expected_ids)
        if expected_ids
        else 1.0
    )
    duplicate_rate = duplicate_count / len(records) if records else 0.0
    unknown_count = len(predicted_ids - known_ids)
    passed = all(
        (
            precision == 1.0,
            recall == 1.0,
            classification_accuracy == 1.0,
            duplicate_rate == 0.0,
            schema_errors == 0,
            unknown_count == 0,
        )
    )

    return {
        "passed": passed,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "classification_accuracy": round(classification_accuracy, 4),
        "duplicate_rate": round(duplicate_rate, 4),
        "schema_errors": schema_errors,
        "unknown_records": unknown_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    print(json.dumps(score(fixture, candidate), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
