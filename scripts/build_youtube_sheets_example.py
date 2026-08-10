#!/usr/bin/env python3
"""Build a deterministic, synthetic YouTube-to-Sheets workbook example."""

import argparse
import copy
import json
from pathlib import Path
from urllib.parse import urlparse


DIRECT_CONTACTS = {
    "direct_email": "direct-email",
    "direct_open_chat": "direct-open-chat",
    "direct_telegram": "direct-telegram",
}
SECOND_REVIEW = {
    "channel_only": ("channel-only", "channel link has no direct message route"),
    "indirect": ("indirect", "only an indirect community or social route was found"),
    "none": ("none", "no contact route was found"),
}
CONTACT_RANK = {"none": 0, "indirect": 1, "channel_only": 2, **{key: 3 for key in DIRECT_CONTACTS}}


def safe_cell(value):
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def channel_key(row):
    channel_id = str(row.get("channel_id", "")).strip().lower()
    if channel_id:
        return channel_id
    path = urlparse(str(row.get("channel_url", ""))).path.rstrip("/")
    handle = path.rsplit("/", 1)[-1].lstrip("@").lower()
    if not handle:
        raise ValueError("candidate needs channel_id or channel_url handle")
    return f"handle:{handle}"


def deduplicate(candidates):
    unique = {}
    paths = {}
    for source in candidates:
        row = copy.deepcopy(source)
        key = channel_key(row)
        path = str(row.get("discovery_path", "")).strip()
        paths.setdefault(key, [])
        if path and path not in paths[key]:
            paths[key].append(path)
        if key not in unique:
            unique[key] = row
            continue
        current = unique[key]
        if CONTACT_RANK.get(row.get("contact", {}).get("type", "none"), 0) > CONTACT_RANK.get(
            current.get("contact", {}).get("type", "none"), 0
        ):
            current["contact"] = row["contact"]
        for field, value in row.items():
            if field not in {"contact", "discovery_path"} and current.get(field) in (None, ""):
                current[field] = value
    for key, row in unique.items():
        row["discovery_path"] = " | ".join(paths[key])
    return unique


def rejection_reason(row, policy, excluded):
    if channel_key(row) in excluded:
        return "already_contacted"
    if row.get("category") not in {"crypto", "stocks", "both"}:
        return "not_relevant"
    subscribers = int(row.get("subscribers", 0))
    if not policy["min_subscribers"] <= subscribers <= policy["max_subscribers"]:
        return "subscriber_range"
    if float(row.get("engagement", 0)) < policy["min_engagement"]:
        return "engagement_below_threshold"
    if int(row.get("recent_upload_days", 10**9)) > policy["max_recent_upload_days"]:
        return "inactive"
    return "accepted"


def clean_row(row):
    return {key: safe_cell(value) for key, value in row.items()}


def build(payload):
    policy = payload["policy"]
    excluded = {str(value).strip().lower() for value in payload.get("excluded_channel_ids", [])}
    unique = deduplicate(payload["candidates"])
    result = {"leads": [], "needs_second_review": [], "research_log": [], "exclusions": sorted(excluded)}

    for key in sorted(unique):
        row = unique[key]
        reason = rejection_reason(row, policy, excluded)
        result["research_log"].append(clean_row({
            "channel_id": key,
            "name": row["name"],
            "verdict": "O" if reason == "accepted" else "X",
            "reason": reason,
            "subscribers": row["subscribers"],
            "engagement": row["engagement"],
            "recent_upload_days": row["recent_upload_days"],
            "membership": row["membership"],
            "discovery_path": row["discovery_path"],
        }))
        if reason != "accepted":
            continue

        contact = row.get("contact", {"type": "none", "value": ""})
        common = {
            "channel_id": key,
            "name": row["name"],
            "channel_url": row["channel_url"],
            "subscribers": row["subscribers"],
            "engagement": row["engagement"],
            "recent_upload_days": row["recent_upload_days"],
            "membership": row["membership"],
            "category": row["category"],
            "discovery_path": row["discovery_path"],
        }
        if contact["type"] in DIRECT_CONTACTS:
            result["leads"].append(clean_row({
                **common,
                "contact": contact["value"],
                "contact_grade": DIRECT_CONTACTS[contact["type"]],
            }))
        else:
            grade, review_reason = SECOND_REVIEW[contact["type"]]
            result["needs_second_review"].append(clean_row({
                **common,
                "current_contact": contact["value"],
                "contact_grade": grade,
                "review_reason": review_reason,
            }))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(build(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
