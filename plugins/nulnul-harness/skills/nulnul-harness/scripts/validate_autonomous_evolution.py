#!/usr/bin/env python3
"""Validate bounded autonomous-evolution episodes in an evolution state."""

import argparse
import json
from pathlib import Path


EPISODE_FIELDS = {
    "id", "mode", "feedback_id", "scope", "pathology", "budget",
    "archive_lookup", "baseline", "candidates", "gate_agent",
    "sealed_evaluation", "holdout_case_ids_read", "cost", "decision",
    "selected_candidate_id", "stop_reason", "claim_boundary",
}
PATHOLOGY_FIELDS = {"where", "why"}
BUDGET_FIELDS = {
    "max_candidates", "max_generations", "max_evaluation_runs",
    "max_failed_candidates", "max_identical_pathology_retries",
    "max_model_invocations",
}
CANDIDATE_FIELDS = {
    "id", "proposal_id", "generation", "author_agent", "parent_agent",
    "parent_version", "pathology", "mechanism_id", "prediction",
    "falsification_condition", "permission_delta", "rollback",
    "archive_match", "evaluation", "decision", "rejection_reason",
}
EVALUATION_FIELDS = {
    "candidate_id", "owner_agent", "status", "runs", "primary_success",
    "guardrails_passed", "evidence", "cost",
}
EVALUATION_COST_FIELDS = {"model_invocations", "completion_checks"}
EPISODE_COST_FIELDS = {
    "candidates_generated", "generations", "evaluation_runs",
    "failed_candidates", "model_invocations", "completion_checks",
}
BASELINE_FIELDS = {"comparable_dimension", "fair", "arms"}
BASELINE_ARM_FIELDS = {
    "id", "runs", "primary_successes", "model_invocations",
    "completion_checks", "evidence",
}
DECISIONS = {
    "AUTONOMOUS_EVOLUTION_WIN", "NO_ADVANTAGE_OVER_RETRY", "NO_PROMOTION",
    "INSUFFICIENT_FEEDBACK", "CAPABILITY_BOUND_SUSPECTED",
}
STOP_REASONS = {
    "SUCCESS", "BUDGET_EXHAUSTED", "NO_INFORMATIVE_FEEDBACK",
    "REPEATED_PATHOLOGY", "NO_ADVANTAGE_OVER_RETRY",
    "CAPABILITY_BOUND_SUSPECTED", "PERMISSION_BLOCKED", "NO_PROMOTION",
}
PROHIBITED_KEYS = {
    "raw_prompt", "raw_response", "raw_transcript", "command_list",
    "commands", "machine_path", "secret", "secrets", "credential",
    "credentials", "api_key", "token",
}


def validate(payload):
    errors = []

    def require(value, fields, label):
        if not isinstance(value, dict):
            errors.append(f"{label} must be an object")
            return False
        missing = sorted(fields - value.keys())
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
            return False
        return True

    def nonempty(value, label):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label} must be non-empty")

    def bounded_int(value, label, minimum=0):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            errors.append(f"{label} must be an integer >= {minimum}")

    def reject_sensitive(value, label="root"):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower() in PROHIBITED_KEYS:
                    errors.append(f"{label}.{key} is prohibited")
                reject_sensitive(item, f"{label}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                reject_sensitive(item, f"{label}[{index}]")

    if not isinstance(payload, dict):
        return ["root must be an object"]
    reject_sensitive(payload)
    episodes = payload.get("autonomous_episodes")
    if not isinstance(episodes, list):
        return errors + ["autonomous_episodes must be an array"]

    feedback = {
        row.get("id"): row for row in payload.get("feedback", []) if isinstance(row, dict)
    }
    proposals = {
        row.get("id"): row for row in payload.get("proposals", []) if isinstance(row, dict)
    }
    agents = payload.get("agents", {}) if isinstance(payload.get("agents"), dict) else {}
    approved = set(payload.get("checkpoint", {}).get("approved_permissions", []))
    seen_episodes = set()

    for episode_index, episode in enumerate(episodes):
        label = f"autonomous_episodes[{episode_index}]"
        if not require(episode, EPISODE_FIELDS, label):
            continue
        episode_id = episode["id"]
        nonempty(episode_id, f"{label}.id")
        if episode_id in seen_episodes:
            errors.append(f"autonomous episode id is duplicated: {episode_id}")
        seen_episodes.add(episode_id)
        if episode["mode"] not in {"live", "retrospective_frozen_replay"}:
            errors.append(f"{label}.mode is invalid")
        if episode["scope"] not in {"project", "core_dev"}:
            errors.append(f"{label}.scope is invalid")
        if episode["feedback_id"] not in feedback:
            errors.append(f"{label} references unknown feedback")
        if not require(episode["pathology"], PATHOLOGY_FIELDS, f"{label}.pathology"):
            continue
        for field in PATHOLOGY_FIELDS:
            nonempty(episode["pathology"][field], f"{label}.pathology.{field}")
        if not require(episode["budget"], BUDGET_FIELDS, f"{label}.budget"):
            continue
        for field, value in episode["budget"].items():
            bounded_int(value, f"{label}.budget.{field}", 1)
        if not isinstance(episode["archive_lookup"], list) or any(
            item not in proposals for item in episode["archive_lookup"]
        ):
            errors.append(f"{label}.archive_lookup must reference known proposals")
        if not isinstance(episode["holdout_case_ids_read"], list):
            errors.append(f"{label}.holdout_case_ids_read must be an array")
        elif episode["holdout_case_ids_read"]:
            errors.append(f"{label} leaked holdout material into autonomous search")
        if episode["sealed_evaluation"] is not True:
            errors.append(f"{label}.sealed_evaluation must be true")
        if episode["gate_agent"] not in agents:
            errors.append(f"{label}.gate_agent is unknown")
        if episode["decision"] not in DECISIONS:
            errors.append(f"{label}.decision is invalid")
        if episode["stop_reason"] not in STOP_REASONS:
            errors.append(f"{label}.stop_reason is invalid")
        expected_stop = {
            "AUTONOMOUS_EVOLUTION_WIN": {"SUCCESS"},
            "NO_ADVANTAGE_OVER_RETRY": {"NO_ADVANTAGE_OVER_RETRY"},
            "INSUFFICIENT_FEEDBACK": {"NO_INFORMATIVE_FEEDBACK"},
            "CAPABILITY_BOUND_SUSPECTED": {"CAPABILITY_BOUND_SUSPECTED"},
            "NO_PROMOTION": STOP_REASONS - {"SUCCESS"},
        }.get(episode["decision"], set())
        if episode["stop_reason"] not in expected_stop:
            errors.append(f"{label}.stop_reason does not match decision")
        nonempty(episode["claim_boundary"], f"{label}.claim_boundary")

        if not require(episode["baseline"], BASELINE_FIELDS, f"{label}.baseline"):
            continue
        comparable_dimension = episode["baseline"]["comparable_dimension"]
        if comparable_dimension not in EVALUATION_COST_FIELDS:
            errors.append(
                f"{label}.baseline.comparable_dimension must be model_invocations or completion_checks"
            )
        if episode["baseline"]["fair"] is not True:
            errors.append(f"{label}.baseline comparison must be fair")
        arms = episode["baseline"]["arms"]
        if not isinstance(arms, list):
            errors.append(f"{label}.baseline.arms must be an array")
            arms = []
        arm_by_id = {}
        for arm_index, arm in enumerate(arms):
            arm_label = f"{label}.baseline.arms[{arm_index}]"
            if not require(arm, BASELINE_ARM_FIELDS, arm_label):
                continue
            if arm["id"] in arm_by_id:
                errors.append(f"{label}.baseline arm id is duplicated: {arm['id']}")
            arm_by_id[arm["id"]] = arm
            for field in ("runs", "primary_successes", "model_invocations", "completion_checks"):
                bounded_int(arm[field], f"{arm_label}.{field}")
            if isinstance(arm["runs"], int) and isinstance(arm["primary_successes"], int) and arm["primary_successes"] > arm["runs"]:
                errors.append(f"{arm_label}.primary_successes exceeds runs")
            nonempty(arm["evidence"], f"{arm_label}.evidence")
        if set(arm_by_id) != {"champion", "retry", "best_of_n"}:
            errors.append(f"{label}.baseline needs champion, retry, and best_of_n arms")

        candidates = episode["candidates"]
        if not isinstance(candidates, list):
            errors.append(f"{label}.candidates must be an array")
            candidates = []
        if len(candidates) > episode["budget"]["max_candidates"]:
            errors.append(f"{label} exceeded max_candidates")
        seen_candidates = set()
        selected = []
        totals = {
            "evaluation_runs": 0, "failed_candidates": 0,
            "model_invocations": 0, "completion_checks": 0,
        }
        evaluated_pathologies = {}

        for candidate_index, candidate in enumerate(candidates):
            candidate_label = f"{label}.candidates[{candidate_index}]"
            if not require(candidate, CANDIDATE_FIELDS, candidate_label):
                continue
            candidate_id = candidate["id"]
            nonempty(candidate_id, f"{candidate_label}.id")
            if candidate_id in seen_candidates:
                errors.append(f"{label} candidate id is duplicated: {candidate_id}")
            seen_candidates.add(candidate_id)
            proposal = proposals.get(candidate["proposal_id"])
            if proposal is None:
                errors.append(f"{candidate_label} references unknown proposal")
                continue
            if candidate["author_agent"] not in agents:
                errors.append(f"{candidate_label}.author_agent is unknown")
            if candidate["parent_agent"] not in agents:
                errors.append(f"{candidate_label}.parent_agent is unknown")
            if proposal.get("author_agent") != candidate["author_agent"]:
                errors.append(f"{candidate_label} author identity does not match proposal")
            if proposal.get("target_agent") != candidate["parent_agent"] or proposal.get("from_version") != candidate["parent_version"]:
                errors.append(f"{candidate_label} parent identity does not match proposal")
            bounded_int(candidate["generation"], f"{candidate_label}.generation", 1)
            if isinstance(candidate["generation"], int) and candidate["generation"] > episode["budget"]["max_generations"]:
                errors.append(f"{candidate_label} exceeded max_generations")
            if not require(candidate["pathology"], PATHOLOGY_FIELDS, f"{candidate_label}.pathology"):
                continue
            for field in PATHOLOGY_FIELDS:
                nonempty(candidate["pathology"][field], f"{candidate_label}.pathology.{field}")
            if candidate["pathology"] != episode["pathology"]:
                errors.append(f"{candidate_label} pathology does not match episode")
            nonempty(candidate["mechanism_id"], f"{candidate_label}.mechanism_id")
            nonempty(candidate["prediction"], f"{candidate_label}.prediction")
            nonempty(candidate["falsification_condition"], f"{candidate_label}.falsification_condition")
            nonempty(candidate["rollback"], f"{candidate_label}.rollback")
            if proposal.get("mechanism_id") is not None and proposal.get("mechanism_id") != candidate["mechanism_id"]:
                errors.append(f"{candidate_label} mechanism identity does not match proposal")
            if proposal.get("pathology") is not None and proposal.get("pathology") != candidate["pathology"]:
                errors.append(f"{candidate_label} proposal pathology does not match")
            for field in ("prediction", "falsification_condition", "permission_delta", "rollback"):
                if proposal.get(field) != candidate[field]:
                    errors.append(f"{candidate_label}.{field} does not match proposal")
            if not isinstance(candidate["permission_delta"], list) or any(
                not isinstance(item, str) or not item for item in candidate["permission_delta"]
            ):
                errors.append(f"{candidate_label}.permission_delta must contain strings")

            evaluation = candidate["evaluation"]
            if not require(evaluation, EVALUATION_FIELDS, f"{candidate_label}.evaluation"):
                continue
            if evaluation["candidate_id"] != candidate_id:
                errors.append(f"{candidate_label} evaluation identity mismatch")
            if evaluation["owner_agent"] != episode["gate_agent"]:
                errors.append(f"{candidate_label} credit is not owned by the independent Gate")
            if evaluation["owner_agent"] in {candidate["author_agent"], candidate["parent_agent"]}:
                errors.append(f"{candidate_label} is self-credited")
            if evaluation["status"] not in {"passed", "failed", "deduplicated", "blocked_by_permission"}:
                errors.append(f"{candidate_label}.evaluation.status is invalid")
            bounded_int(evaluation["runs"], f"{candidate_label}.evaluation.runs")
            for field in ("primary_success", "guardrails_passed"):
                if not isinstance(evaluation[field], bool):
                    errors.append(f"{candidate_label}.evaluation.{field} must be boolean")
            nonempty(evaluation["evidence"], f"{candidate_label}.evaluation.evidence")
            if require(evaluation["cost"], EVALUATION_COST_FIELDS, f"{candidate_label}.evaluation.cost"):
                for field in EVALUATION_COST_FIELDS:
                    bounded_int(evaluation["cost"][field], f"{candidate_label}.evaluation.cost.{field}")
                    if isinstance(evaluation["cost"][field], int):
                        totals[field] += evaluation["cost"][field]
            if isinstance(evaluation["runs"], int):
                totals["evaluation_runs"] += evaluation["runs"]
            if evaluation["status"] == "failed":
                totals["failed_candidates"] += 1
            if evaluation["runs"]:
                key = (
                    candidate["pathology"]["where"],
                    candidate["pathology"]["why"],
                    candidate["mechanism_id"],
                )
                evaluated_pathologies[key] = evaluated_pathologies.get(key, 0) + 1

            archive_match = candidate["archive_match"]
            if archive_match is not None:
                archived = proposals.get(archive_match)
                if archive_match not in episode["archive_lookup"] or archived is None:
                    errors.append(f"{candidate_label}.archive_match is not in the episode archive")
                elif archived.get("status") not in {"rejected", "rolled_back"}:
                    errors.append(f"{candidate_label}.archive_match is not rejected knowledge")
                elif archived.get("mechanism_id") != candidate["mechanism_id"] or archived.get("pathology") != candidate["pathology"]:
                    errors.append(f"{candidate_label}.archive_match identity mismatch")
                if candidate["decision"] != "deduplicated" or evaluation["status"] != "deduplicated" or evaluation["runs"] != 0:
                    errors.append(f"{candidate_label} rejected replay must be deduplicated without evaluation")
            else:
                for archived_id in episode["archive_lookup"]:
                    archived = proposals.get(archived_id, {})
                    if (
                        archived.get("status") in {"rejected", "rolled_back"}
                        and archived.get("mechanism_id") == candidate["mechanism_id"]
                        and archived.get("pathology") == candidate["pathology"]
                    ):
                        errors.append(f"{candidate_label} replays rejected archive knowledge")
                        break

            unapproved = [item for item in candidate["permission_delta"] if item not in approved]
            if unapproved and (
                candidate["decision"] != "blocked_by_permission"
                or evaluation["status"] != "blocked_by_permission"
                or evaluation["runs"] != 0
            ):
                errors.append(f"{candidate_label} expands permission without approval")
            if candidate["decision"] == "selected":
                selected.append(candidate_id)
                if not (
                    evaluation["status"] == "passed"
                    and evaluation["primary_success"] is True
                    and evaluation["guardrails_passed"] is True
                    and evaluation["runs"] > 0
                ):
                    errors.append(f"{candidate_label} selected without passing deterministic evidence")
                if candidate["rejection_reason"] is not None:
                    errors.append(f"{candidate_label}.rejection_reason must be null when selected")
            elif not isinstance(candidate["rejection_reason"], str) or not candidate["rejection_reason"].strip():
                errors.append(f"{candidate_label} needs a rejection reason")

        for key, count in evaluated_pathologies.items():
            if count > episode["budget"]["max_identical_pathology_retries"]:
                errors.append(f"{label} exceeded max_identical_pathology_retries for {key[0]}/{key[1]}")
        for field in ("evaluation_runs", "failed_candidates", "model_invocations"):
            budget_field = f"max_{field}"
            if totals[field] > episode["budget"][budget_field]:
                errors.append(f"{label} exceeded {budget_field}")

        if require(episode["cost"], EPISODE_COST_FIELDS, f"{label}.cost"):
            expected_cost = {
                "candidates_generated": len(candidates),
                "generations": max((item.get("generation", 0) for item in candidates if isinstance(item, dict)), default=0),
                **totals,
            }
            for field, expected in expected_cost.items():
                if episode["cost"].get(field) != expected:
                    errors.append(f"{label}.cost.{field} does not match candidate evidence")

        if episode["selected_candidate_id"] is None:
            if selected:
                errors.append(f"{label} has a selected candidate but no selected_candidate_id")
        elif selected != [episode["selected_candidate_id"]]:
            errors.append(f"{label}.selected_candidate_id does not match exactly one selected candidate")
        if episode["decision"] == "AUTONOMOUS_EVOLUTION_WIN":
            retry = arm_by_id.get("retry", {})
            if (
                len(selected) != 1
                or episode["stop_reason"] != "SUCCESS"
                or retry.get("primary_successes") != 0
                or totals.get(comparable_dimension, 0) > retry.get(comparable_dimension, -1)
            ):
                errors.append(f"{label} autonomous win is not supported by the retry comparison")
        elif selected:
            errors.append(f"{label} cannot select a candidate for decision {episode['decision']}")

    return errors


def summarize(payload):
    return [
        {
            "id": episode["id"],
            "decision": episode["decision"],
            "stop_reason": episode["stop_reason"],
            "selected_candidate_id": episode["selected_candidate_id"],
            "cost": episode["cost"],
        }
        for episode in payload.get("autonomous_episodes", [])
        if isinstance(episode, dict) and "id" in episode
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.state.read_text(encoding="utf-8"))
    errors = validate(payload)
    print(json.dumps({"valid": not errors, "errors": errors, "episodes": summarize(payload)}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
