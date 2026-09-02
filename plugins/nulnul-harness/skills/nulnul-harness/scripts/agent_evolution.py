#!/usr/bin/env python3
"""Evidence-gated Agent topology contracts, competition, and transactions."""

import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import capability_contract
import capability_pack
import foundation_runtime as runtime
import natural_selection
from sync_host_entry import atomic_batch_write


SCHEMA_VERSION = 1
MAX_AGENTS = 8
MAX_EDGES = 16
MAX_SOURCE_EXPERIENCES = 20
RESULTS = {
    "KEEP", "UPGRADE_CANDIDATE", "SPLIT_CANDIDATE", "MERGE_CANDIDATE",
    "REPLACE_CANDIDATE", "RETIRE_CANDIDATE", "CREATE_CANDIDATE",
    "MORE_EXPERIENCE_REQUIRED", "NO_ACTION",
}
OPERATIONS = {"KEEP", "UPGRADE", "SPLIT", "MERGE", "REPLACE", "RETIRE", "CREATE"}
SIGNALS = {
    "success-only", "agent-contract-gap", "responsibility-overload",
    "duplicate-agent-work", "replacement-advantage", "obsolete-responsibility",
    "recurring-uncovered-responsibility", "missing-capability", "insufficient", "none",
}
AGENT_FIELDS = (
    "role", "job", "responsibilities", "task_boundary", "input_contract",
    "output_contract", "capability_requirements", "tool_requirements",
    "delegation_rules", "verification_responsibility", "authority_boundary",
    "handoff_contract", "failure_escalation", "context_requirements",
)
EDGE_FIELDS = (
    "parent_agent_id", "child_agent_id", "parent_task_boundary", "child_task_boundary",
    "expected_output", "allowed_scope", "required_check", "return_contract",
)
COST_FIELDS = (
    "agent_count", "model_calls", "input_tokens", "output_tokens", "runtime_ms",
    "pack_bytes", "memory_bytes", "handoff_bytes", "repository_reads",
    "verification_steps", "maintenance_units",
)
ADVANTAGES = {
    "LOWER_CONTEXT", "LOWER_FAILURE_RATE", "REUSABLE_SPECIALIZATION",
    "INDEPENDENT_VERIFICATION", "LOWER_MAINTENANCE",
}


def canonical_digest(payload):
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def paths(root):
    root = Path(root).resolve()
    nulnul = root / "docs/nulnul"
    local = nulnul / ".runtime/agent-evolution"
    return {
        "current": nulnul / "agent-topology.json",
        "history": nulnul / "memory/agent-topologies",
        "challengers": local / "challengers",
        "competitions": local / "competitions",
        "bindings": local / "bindings",
        "handoffs": local / "handoffs",
    }


def _strings(value, field, *, required=False, maximum=16):
    if not isinstance(value, list) or len(value) > maximum or any(
        not isinstance(item, str) or not item.strip() or len(item.encode()) > 512 for item in value
    ):
        raise ValueError(f"Agent {field} must be a bounded string list")
    output = list(dict.fromkeys(item.strip() for item in value))
    if required and not output:
        raise ValueError(f"Agent {field} cannot be empty")
    return output


def _text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value.encode()) > 2048:
        raise ValueError(f"Agent {field} must be one bounded string")
    return value.strip()


def _agent_content(specification):
    output = {}
    for field in AGENT_FIELDS:
        value = specification.get(field)
        if field in {
            "responsibilities", "input_contract", "output_contract", "capability_requirements",
            "tool_requirements", "delegation_rules", "handoff_contract", "failure_escalation",
            "context_requirements",
        }:
            output[field] = _strings(value, field, required=field in {"responsibilities", "input_contract", "output_contract"})
        else:
            output[field] = _text(value, field)
    return output


def _agent_digest(record):
    return canonical_digest({field: record[field] for field in ("agent_id", "version") + AGENT_FIELDS})


def _new_agent_id(specification, content):
    key = re.sub(r"[^a-z0-9]+", "-", str(specification.get("agent_key", "agent")).lower()).strip("-")[:28]
    if not key:
        key = "agent"
    return f"agent-{key}-{canonical_digest(content)[:8]}"


def agent_contract(specification, *, source=None, status="CURRENT"):
    """Canonicalize one semantic Agent contract; runtime owns identity and digest."""
    if not isinstance(specification, dict):
        raise ValueError("Agent contract must be one object")
    content = _agent_content(specification)
    if source:
        identity = source["agent_id"]
        previous_content = {field: source[field] for field in AGENT_FIELDS}
        version = source["version"] + (content != previous_content)
    else:
        identity = specification.get("agent_id") or _new_agent_id(specification, content)
        version = int(specification.get("version", 1))
    if not re.fullmatch(r"agent-[a-z0-9][a-z0-9-]{0,63}", str(identity)) or version < 1:
        raise ValueError("invalid Agent identity or version")
    record = {
        "schema_version": SCHEMA_VERSION,
        "agent_id": identity,
        "version": version,
        **content,
        "status": status,
    }
    record["agent_contract_digest"] = _agent_digest(record)
    return record


def _edge(edge):
    if not isinstance(edge, dict) or any(not isinstance(edge.get(field), str) or not edge[field].strip() for field in EDGE_FIELDS):
        raise ValueError("delegation edge is incomplete")
    return {field: edge[field].strip() for field in EDGE_FIELDS}


def _topology_digest(record):
    return canonical_digest({
        "topology_id": record["agent_topology_id"],
        "version": record["version"],
        "topology_kind": record["topology_kind"],
        "agents": [
            {"agent_id": row["agent_id"], "agent_contract_digest": row["agent_contract_digest"]}
            for row in record["agents"]
        ],
        "edges": record["edges"],
        "synthesis_owner_agent_id": record["synthesis_owner_agent_id"],
        "verification_owner_agent_id": record["verification_owner_agent_id"],
    })


def default_topology(root=None):
    agent = agent_contract({
        "agent_id": "agent-primary",
        "version": 1,
        "role": "single project owner",
        "job": "Complete the bounded project task and verify the result",
        "responsibilities": ["product-work"],
        "task_boundary": "the current user task",
        "input_contract": ["user task", "bounded project context", "task-fit Capability Pack"],
        "output_contract": ["task-owned product result", "authoritative verification receipt"],
        "capability_requirements": [],
        "tool_requirements": [],
        "delegation_rules": [],
        "verification_responsibility": "own the authoritative final project check",
        "authority_boundary": "task-owned product writes only; no structural authority",
        "handoff_contract": [],
        "failure_escalation": ["record an observable bounded failure"],
        "context_requirements": ["bounded relevant Memory", "selected capability bodies only"],
    })
    record = {
        "schema_version": SCHEMA_VERSION,
        "agent_topology_id": "topology-project-execution",
        "version": 1,
        "topology_kind": "SINGLE_AGENT",
        "status": "CURRENT",
        "agents": [agent],
        "edges": [],
        "synthesis_owner_agent_id": agent["agent_id"],
        "verification_owner_agent_id": agent["agent_id"],
        "created_at": "implicit-foundation-default",
        "derived_from": [],
    }
    record["agent_topology_digest"] = _topology_digest(record)
    return record


def _capability_ids(root):
    project = Path(root).resolve() / "docs/nulnul/project.md"
    return {row["capability_id"] for row in capability_contract.bounded_view(project)}


def validate_topology(
    root, topology, *,
    allowed_statuses={"CURRENT", "CHALLENGER", "SUPERSEDED", "RETIRED"},
    require_current_capabilities=True,
):
    if not isinstance(topology, dict) or topology.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("invalid Agent topology schema")
    agents = topology.get("agents")
    edges = topology.get("edges")
    if not isinstance(agents, list) or not 1 <= len(agents) <= MAX_AGENTS:
        raise ValueError("Agent topology requires 1-8 Agents")
    if not isinstance(edges, list) or len(edges) > MAX_EDGES:
        raise ValueError("Agent topology has too many delegation edges")
    if topology.get("status") not in allowed_statuses:
        raise ValueError("invalid Agent topology status")
    if topology.get("topology_kind") != ("SINGLE_AGENT" if len(agents) == 1 else "MULTI_AGENT"):
        raise ValueError("Agent topology kind does not match Agent count")
    by_id = {}
    capability_ids = (
        _capability_ids(root) if require_current_capabilities else {
            row["capability_id"] for row in capability_contract.load(
                Path(root).resolve() / "docs/nulnul/project.md", require_canonical=True
            )
        }
    )
    responsibilities = {}
    for agent in agents:
        if agent.get("schema_version") != SCHEMA_VERSION or agent.get("status") not in allowed_statuses:
            raise ValueError("invalid Agent contract status")
        if agent.get("agent_contract_digest") != _agent_digest(agent):
            raise ValueError("invalid Agent contract digest")
        identity = agent.get("agent_id")
        if identity in by_id:
            raise ValueError("duplicate Agent ID")
        by_id[identity] = agent
        unknown = set(agent.get("capability_requirements", [])) - capability_ids
        if unknown:
            raise ValueError("Agent references unknown or retired Capability: " + ", ".join(sorted(unknown)))
        for responsibility in agent.get("responsibilities", []):
            if responsibility in responsibilities:
                raise ValueError("duplicate conflicting responsibility owner: " + responsibility)
            responsibilities[responsibility] = identity
    edge_rows = [_edge(row) for row in edges]
    if edge_rows != sorted(edge_rows, key=lambda row: (row["parent_agent_id"], row["child_agent_id"])):
        raise ValueError("Agent topology edges must be canonical and sorted")
    parents = {}
    children = {identity: [] for identity in by_id}
    for edge in edge_rows:
        parent, child = edge["parent_agent_id"], edge["child_agent_id"]
        if parent not in by_id or child not in by_id:
            raise ValueError("dangling Agent delegation edge")
        if parent == child:
            raise ValueError("Agent cannot delegate to itself")
        if child in parents:
            raise ValueError("Agent topology gives one child multiple parents")
        parents[child] = parent
        children[parent].append(child)
    synthesis = topology.get("synthesis_owner_agent_id")
    verifier = topology.get("verification_owner_agent_id")
    if synthesis not in by_id or verifier not in by_id:
        raise ValueError("Agent topology requires valid synthesis and verification owners")
    if len(agents) == 1 and edge_rows:
        raise ValueError("SINGLE_AGENT topology cannot have delegation edges")
    if len(agents) > 1:
        reached, pending = set(), [synthesis]
        while pending:
            identity = pending.pop()
            if identity in reached:
                raise ValueError("cyclic Agent delegation")
            reached.add(identity)
            pending.extend(children[identity])
        if reached != set(by_id):
            raise ValueError("Agent topology has unreachable or cyclic Agents")
    if not by_id[verifier].get("verification_responsibility"):
        raise ValueError("verification owner has no verification responsibility")
    if topology.get("agent_topology_digest") != _topology_digest(topology):
        raise ValueError("invalid Agent topology digest")
    return topology


def current_topology(root):
    path = paths(root)["current"]
    topology = runtime.read_json(path) if path.exists() else default_topology(root)
    validate_topology(root, topology, allowed_statuses={"CURRENT"})
    return topology


def _all_experiences(root):
    store = runtime.Store(root)
    index = runtime.load_index(store)
    return [
        row for identity in index.get("experiences", [])[-runtime.MAX_SEARCH_ITEMS_PER_TYPE:]
        if (row := runtime.read_json(store.experiences / f"{identity}.json"))
    ]


def topology_snapshot(root):
    topology = current_topology(root)
    experiences = _all_experiences(root)
    decisions = runtime.read_jsonl(runtime.Store(root).decisions)
    return {
        "schema_version": SCHEMA_VERSION,
        "topology": topology,
        "agent_experience_ids": [
            row["experience_id"] for row in experiences if row.get("agent_evolution_eligible")
        ][-20:],
        "decision_ids": [row["decision_id"] for row in decisions if row.get("agent_evolution")][-20:],
    }


def _source_experiences(root, identities):
    identities = list(dict.fromkeys(identities or []))
    if not identities or len(identities) > MAX_SOURCE_EXPERIENCES:
        raise ValueError("Agent Evolution requires 1-20 source Experience IDs")
    available = {row["experience_id"]: row for row in _all_experiences(root)}
    missing = [identity for identity in identities if identity not in available]
    if missing:
        raise ValueError("unknown source Experience: " + ", ".join(missing))
    rows = [available[identity] for identity in identities]
    if any(row.get("status") != "ACTIVE" or row.get("quality") != "VERIFIED" for row in rows):
        raise ValueError("Agent Evolution accepts only active VERIFIED Experiences")
    return rows


def _covered_by_decision(root, affected, sources):
    for decision in reversed(runtime.read_jsonl(runtime.Store(root).decisions)):
        agent = decision.get("agent_evolution", {})
        if decision.get("status") != "ACTIVE" or not set(affected) <= set(agent.get("affected_agent_ids", [])):
            continue
        if set(sources) <= set(agent.get("source_experience_ids", [])):
            return decision["decision_id"]
    return None


def evaluate(root, review):
    """Map bounded observable evidence to a non-mutating topology candidate."""
    if not isinstance(review, dict) or review.get("signal") not in SIGNALS:
        raise ValueError("invalid bounded Agent Evolution signal")
    topology = current_topology(root)
    opportunity_policy, _ = runtime.harness_policy(root, "control-agent-opportunity", {
        "minimum_repeat_count": 2,
    })
    minimum_repeat = opportunity_policy["minimum_repeat_count"]
    current_ids = {row["agent_id"] for row in topology["agents"]}
    affected = list(dict.fromkeys(review.get("affected_agent_ids", [])))
    unknown = sorted(set(affected) - current_ids)
    if unknown:
        raise ValueError("unknown current Agent: " + ", ".join(unknown))
    source_ids = list(dict.fromkeys(review.get("source_experience_ids", [])))
    experiences = _source_experiences(root, source_ids) if source_ids else []
    signal = review["signal"]
    if signal not in {"none", "insufficient"} and not experiences:
        raise ValueError("evidence-bearing Agent Evolution signals require source Experiences")
    eligible = [row for row in experiences if row.get("agent_evolution_eligible")]
    attributable = [
        row for row in eligible
        if row.get("agent_id") in affected or row.get("agent_attribution_scope") == "TOPOLOGY"
    ]
    result, reason = "MORE_EXPERIENCE_REQUIRED", "bounded evidence does not justify Agent topology mutation"
    natural_selection_need = None
    if signal == "none":
        result, reason = "NO_ACTION", "no material Agent topology trigger is present"
    elif signal == "insufficient":
        result, reason = "MORE_EXPERIENCE_REQUIRED", "current Experience lacks Agent-attributable topology evidence"
    elif signal == "success-only":
        if len(eligible) != len(experiences) or any(row.get("result") != "SUCCESS" for row in experiences):
            result, reason = "MORE_EXPERIENCE_REQUIRED", "success review includes non-Agent or non-success evidence"
        elif _covered_by_decision(root, affected, source_ids):
            result, reason = "NO_ACTION", "an active Agent lifecycle decision already covers this evidence"
        elif review.get("trigger") == "explicit-maintenance":
            result, reason = "KEEP", "verified Agent Experience supports the current topology"
        else:
            result, reason = "NO_ACTION", "additional success alone does not reopen Agent Evolution"
    elif signal == "agent-contract-gap" and len(affected) == 1:
        if any(row.get("result") == "FAILURE" for row in attributable):
            result, reason = "UPGRADE_CANDIDATE", "verified Agent-attributable failure supports a same-responsibility contract Challenger"
    elif signal == "responsibility-overload" and len(affected) == 1:
        if len(attributable) >= minimum_repeat and len(set(review.get("overloaded_responsibilities", []))) >= 2:
            result, reason = "SPLIT_CANDIDATE", "repeated evidence supports partitioning one overloaded responsibility"
    elif signal == "duplicate-agent-work" and len(affected) >= 2:
        if len(eligible) >= minimum_repeat and review.get("independent_value_absent") is True:
            result, reason = "MERGE_CANDIDATE", "repeated duplicate work supports one lower-cost topology Challenger"
    elif signal == "replacement-advantage" and len(affected) == 1:
        if attributable and review.get("replacement_agent_key"):
            result, reason = "REPLACE_CANDIDATE", "a distinct project-local Agent design may compete for this responsibility"
    elif signal == "obsolete-responsibility" and len(affected) == 1:
        if attributable and (review.get("job_no_longer_exists") is True or review.get("absorbed_by_agent_id") in current_ids - set(affected)):
            result, reason = "RETIRE_CANDIDATE", "verified evidence supports removing an obsolete or absorbed Agent"
    elif signal == "recurring-uncovered-responsibility":
        jobs = {str(row.get("task_job", "")).strip().lower() for row in experiences}
        if len(experiences) >= minimum_repeat and len(jobs) == 1 and all(not row.get("agent_id") for row in experiences):
            result, reason = "CREATE_CANDIDATE", "repeated verified work exposes one uncovered execution responsibility"
    elif signal == "missing-capability":
        capability_type = review.get("required_capability_type")
        job = str(review.get("required_capability_job", "")).strip()
        check = str(review.get("project_check_concept", "")).strip()
        if capability_type not in natural_selection.CAPABILITY_TYPES or not job or not check:
            raise ValueError("missing-capability requires a capability type, job, and project-check concept")
        result, reason = "NO_ACTION", "Agent Evolution cannot create capabilities; forward this bounded need to Natural Selection"
        natural_selection_need = {
            "signal": "recurring-uncovered-job",
            "affected_capability_ids": [],
            "source_experience_ids": source_ids,
            "uncovered_job": job,
            "requested_capability_type": capability_type,
            "project_check_concept": check,
            "diagnosis": review.get("diagnosis", ""),
            "what_must_not_change": review.get("what_must_not_change", ""),
            "risk_analysis": review.get("regression_risk", ""),
            "rollback_plan": review.get("rollback_plan", ""),
        }
    if result.endswith("_CANDIDATE"):
        for field in (
            "diagnosis", "expected_benefit", "coordination_cost", "regression_risk",
            "what_must_not_change", "rollback_plan",
        ):
            if not str(review.get(field, "")).strip():
                raise ValueError(f"{result} requires {field}")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "result": result,
        "reason": reason,
        "champion_topology_id": topology["agent_topology_id"],
        "champion_digest": topology["agent_topology_digest"],
        "affected_agent_ids": affected,
        "source_experience_ids": source_ids,
        "diagnosis": review.get("diagnosis", ""),
        "expected_benefit": review.get("expected_benefit", ""),
        "coordination_cost": review.get("coordination_cost", ""),
        "regression_risk": review.get("regression_risk", ""),
        "what_must_not_change": review.get("what_must_not_change", ""),
        "rollback_plan": review.get("rollback_plan", ""),
        "candidate_hint": {
            key: review[key]
            for key in (
                "overloaded_responsibilities", "replacement_agent_key", "absorbed_by_agent_id",
                "uncovered_responsibility",
            ) if key in review
        },
        "natural_selection_need": natural_selection_need,
    }
    payload["evaluation_digest"] = canonical_digest(payload)
    return payload


def validate_evaluation(root, evaluation):
    if not isinstance(evaluation, dict):
        raise ValueError("Agent Evolution evaluation must be one object")
    unsigned = {key: value for key, value in evaluation.items() if key != "evaluation_digest"}
    if evaluation.get("result") not in RESULTS or evaluation.get("evaluation_digest") != canonical_digest(unsigned):
        raise ValueError("Agent Evolution evaluation identity is invalid")
    topology = current_topology(root)
    if topology["agent_topology_digest"] != evaluation.get("champion_digest"):
        raise ValueError("stale Agent topology Champion digest")
    sources = evaluation.get("source_experience_ids", [])
    if evaluation["result"] not in {"NO_ACTION", "MORE_EXPERIENCE_REQUIRED"} and not sources:
        raise ValueError("Agent lifecycle decision requires source Experiences")
    if sources:
        _source_experiences(root, sources)
    return topology


def _operation(result):
    return result.removesuffix("_CANDIDATE")


def _candidate_agents(champion, specification):
    existing = {row["agent_id"]: row for row in champion["agents"]}
    output, identities = [], {identity: identity for identity in existing}
    for row in specification.get("agents", []):
        source_id = row.get("source_agent_id")
        if source_id:
            if source_id not in existing:
                raise ValueError("Topology Challenger references unknown source Agent")
            agent = agent_contract(row, source=existing[source_id], status="CHALLENGER")
            identities[str(row.get("agent_key", source_id))] = agent["agent_id"]
        else:
            if row.get("agent_id"):
                raise ValueError("new Agent identity is runtime-owned; supply agent_key")
            if not isinstance(row.get("agent_key"), str) or not row["agent_key"].strip():
                raise ValueError("new Agent requires one semantic agent_key")
            agent = agent_contract(row, status="CHALLENGER")
            if row["agent_key"] in identities:
                raise ValueError("duplicate Agent semantic key")
            identities[row["agent_key"]] = agent["agent_id"]
        output.append(agent)
    return sorted(output, key=lambda row: row["agent_id"]), identities


def _candidate_edge(edge, identities):
    row = dict(edge)
    for side in ("parent", "child"):
        identity_field, key_field = f"{side}_agent_id", f"{side}_agent_key"
        value = row.get(identity_field) or identities.get(str(row.get(key_field)))
        if value not in set(identities.values()):
            raise ValueError("Topology Challenger edge references an unknown Agent key")
        row[identity_field] = value
    return _edge(row)


def _assert_unchanged(champion, challenger, ignored):
    before = {row["agent_id"]: row["agent_contract_digest"] for row in champion["agents"] if row["agent_id"] not in ignored}
    after_by_id = {row["agent_id"]: row["agent_contract_digest"] for row in challenger["agents"]}
    after = {identity: after_by_id.get(identity) for identity in before}
    if before != after:
        raise ValueError("Topology Challenger changes unaffected Agent contracts")


def _validate_operation(champion, challenger, evaluation):
    operation = _operation(evaluation["result"])
    affected = set(evaluation["affected_agent_ids"])
    old = {row["agent_id"] for row in champion["agents"]}
    new = {row["agent_id"] for row in challenger["agents"]}
    added, removed = new - old, old - new
    if operation in {"UPGRADE", "SPLIT", "REPLACE", "RETIRE"} and len(affected) != 1:
        raise ValueError(f"{operation} requires one affected Agent")
    if operation == "MERGE" and len(affected) < 2:
        raise ValueError("MERGE requires at least two affected Agents")
    if operation == "CREATE" and affected:
        raise ValueError("CREATE cannot replace an existing Agent")
    if operation == "UPGRADE":
        if old != new or removed or added:
            raise ValueError("UPGRADE must preserve Agent identity and topology membership")
        source = next(iter(affected))
        old_row = next(row for row in champion["agents"] if row["agent_id"] == source)
        new_row = next(row for row in challenger["agents"] if row["agent_id"] == source)
        if old_row["agent_contract_digest"] == new_row["agent_contract_digest"]:
            raise ValueError("UPGRADE Challenger must change the Agent contract")
    elif operation == "SPLIT":
        if removed != affected or len(added) < 2 or len(new) <= len(old):
            raise ValueError("SPLIT must replace one Agent with at least two bounded Agents")
    elif operation == "MERGE":
        if removed != affected or len(added) != 1 or len(new) != len(old) - len(affected) + 1:
            raise ValueError("MERGE must replace affected Agents with one Agent")
    elif operation == "REPLACE":
        if removed != affected or len(added) != 1 or len(new) != len(old):
            raise ValueError("REPLACE must exchange one Agent for one distinct Agent")
    elif operation == "RETIRE":
        if removed != affected or added or len(new) != len(old) - 1:
            raise ValueError("RETIRE must remove one Agent without replacement")
    elif operation == "CREATE":
        if removed or len(added) != 1 or len(new) != len(old) + 1:
            raise ValueError("CREATE must add exactly one Agent")
    _assert_unchanged(champion, challenger, affected)


def freeze_challenger(root, evaluation, specification):
    champion = validate_evaluation(root, evaluation)
    if not evaluation["result"].endswith("_CANDIDATE"):
        raise ValueError("only a mutation candidate may freeze one Topology Challenger")
    if not isinstance(specification, dict) or not isinstance(specification.get("agents"), list):
        raise ValueError("Topology Challenger specification is incomplete")
    agents, identities = _candidate_agents(champion, specification)
    synthesis = specification.get("synthesis_owner_agent_id") or identities.get(str(specification.get("synthesis_owner_agent_key")))
    verifier = specification.get("verification_owner_agent_id") or identities.get(str(specification.get("verification_owner_agent_key")))
    record = {
        "schema_version": SCHEMA_VERSION,
        "agent_topology_id": champion["agent_topology_id"],
        "version": champion["version"] + 1,
        "topology_kind": "SINGLE_AGENT" if len(agents) == 1 else "MULTI_AGENT",
        "status": "CHALLENGER",
        "agents": agents,
        "edges": sorted([_candidate_edge(row, identities) for row in specification.get("edges", [])], key=lambda row: (row["parent_agent_id"], row["child_agent_id"])),
        "synthesis_owner_agent_id": synthesis,
        "verification_owner_agent_id": verifier,
        "created_at": runtime.utc_now(),
        "derived_from": [f"experience:{identity}" for identity in evaluation["source_experience_ids"]],
        "evaluation_digest": evaluation["evaluation_digest"],
    }
    record["agent_topology_digest"] = _topology_digest(record)
    validate_topology(root, record, allowed_statuses={"CHALLENGER"})
    _validate_operation(champion, record, evaluation)
    path = paths(root)["challengers"] / f"{record['agent_topology_digest']}.json"
    if path.exists() and runtime.read_json(path) != record:
        raise ValueError("frozen Topology Challenger digest collision")
    runtime.write_json(path, record)
    path.chmod(0o444)
    return record


def load_challenger(root, digest):
    if not re.fullmatch(r"[a-f0-9]{64}", str(digest)):
        raise ValueError("invalid Topology Challenger digest")
    record = runtime.read_json(paths(root)["challengers"] / f"{digest}.json")
    if not record or record.get("agent_topology_digest") != digest:
        raise ValueError("unknown frozen Topology Challenger")
    return validate_topology(root, record, allowed_statuses={"CHALLENGER"})


def _metrics(row, label):
    if not isinstance(row, dict) or not all(isinstance(row.get(field), bool) for field in ("strict", "project_check", "completion")):
        raise ValueError(f"{label} has incomplete primary outcomes")
    if not isinstance(row.get("unauthorized_writes"), int) or row["unauthorized_writes"] < 0:
        raise ValueError(f"{label} has invalid write evidence")
    return row


def _cost(row, label):
    if not isinstance(row, dict) or any(not isinstance(row.get(field), (int, float)) or row[field] < 0 for field in COST_FIELDS):
        raise ValueError(f"{label} has incomplete topology carrying cost")
    return {field: row[field] for field in COST_FIELDS}


def freeze_competition(root, evaluation, challenger_digest, evidence):
    champion = validate_evaluation(root, evaluation)
    challenger = load_challenger(root, challenger_digest)
    if challenger.get("evaluation_digest") != evaluation["evaluation_digest"]:
        raise ValueError("Topology Challenger does not belong to this evaluation")
    groups = evidence.get("task_groups") if isinstance(evidence, dict) else None
    if not isinstance(groups, list) or not 1 <= len(groups) <= 3:
        raise ValueError("Agent competition requires 1-3 task groups")
    names, normalized = set(), []
    for group in groups:
        name = group.get("group")
        if name in names or name not in {"TARGET_WEAKNESS", "REGRESSION", "SEALED_HOLDOUT"}:
            raise ValueError("Agent competition task groups must be unique and bounded")
        names.add(name)
        for field in ("task_hash", "fixture_hash", "project_revision"):
            if not isinstance(group.get(field), str) or not group[field]:
                raise ValueError("competition freeze identity is incomplete")
        if not isinstance(group.get("check_identities"), list) or not group["check_identities"]:
            raise ValueError("competition requires authoritative check identities")
        champion_metrics = _metrics(group.get("champion"), f"{name} Champion")
        challenger_metrics = _metrics(group.get("challenger"), f"{name} Challenger")
        normalized.append({**group, "champion": champion_metrics, "challenger": challenger_metrics})
    if "SEALED_HOLDOUT" not in names:
        raise ValueError("Agent competition requires one sealed holdout")
    champion_cost = _cost(evidence.get("champion_cost"), "Champion")
    challenger_cost = _cost(evidence.get("challenger_cost"), "Challenger")
    def passed(row):
        return all(row[field] for field in ("strict", "project_check", "completion")) and row["unauthorized_writes"] == 0
    regressions = [row["group"] for row in normalized if passed(row["champion"]) and not passed(row["challenger"])]
    improvements = [row["group"] for row in normalized if not passed(row["champion"]) and passed(row["challenger"])]
    holdout = next(row for row in normalized if row["group"] == "SEALED_HOLDOUT")
    if not any(passed(row["champion"]) or passed(row["challenger"]) for row in normalized):
        outcome, reason = "NO_SURVIVOR", "neither topology produced one verified task-group outcome"
    elif regressions or not passed(holdout["challenger"]):
        outcome, reason = "KEEP_CURRENT", "Topology Challenger regressed verified behavior or failed the holdout"
    elif improvements:
        outcome, reason = "PROMOTE_CHALLENGER", "Topology Challenger improved verified quality without regression"
    else:
        advantage = evidence.get("meaningful_advantage")
        verified = evidence.get("advantage_verified") is True
        if advantage == "LOWER_CONTEXT":
            verified = verified and challenger_cost["pack_bytes"] + challenger_cost["memory_bytes"] < champion_cost["pack_bytes"] + champion_cost["memory_bytes"]
        elif advantage == "LOWER_MAINTENANCE":
            verified = verified and challenger_cost["maintenance_units"] < champion_cost["maintenance_units"]
        if advantage in ADVANTAGES and verified:
            outcome, reason = "PROMOTE_CHALLENGER", "equivalent quality has one verified meaningful topology advantage"
        else:
            outcome, reason = "KEEP_CURRENT", "equivalent quality does not justify additional or changed Agent complexity"
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "champion_digest": champion["agent_topology_digest"],
        "challenger_digest": challenger_digest,
        "evaluation_digest": evaluation["evaluation_digest"],
        "task_groups": normalized,
        "champion_cost": champion_cost,
        "challenger_cost": challenger_cost,
        "meaningful_advantage": evidence.get("meaningful_advantage"),
        "advantage_verified": evidence.get("advantage_verified") is True,
        "regressions": regressions,
        "improvements": improvements,
        "outcome": outcome,
        "reason": reason,
        "created_at": runtime.utc_now(),
    }
    receipt["competition_digest"] = canonical_digest(receipt)
    path = paths(root)["competitions"] / f"{receipt['competition_digest']}.json"
    runtime.write_json(path, receipt)
    path.chmod(0o444)
    return receipt


def load_competition(root, digest):
    if not re.fullmatch(r"[a-f0-9]{64}", str(digest)):
        raise ValueError("invalid Agent competition digest")
    receipt = runtime.read_json(paths(root)["competitions"] / f"{digest}.json")
    unsigned = {key: value for key, value in (receipt or {}).items() if key != "competition_digest"}
    if not receipt or receipt.get("competition_digest") != canonical_digest(unsigned):
        raise ValueError("unknown or corrupt Agent competition")
    return receipt


def _active_task(root):
    store = runtime.Store(root)
    active = runtime.read_json(store.active)
    task = next((row for row in (active or {}).get("tasks", []) if row.get("status") == "ACTIVE"), None)
    if not active or not task:
        raise ValueError("Agent Evolution transaction requires one active Foundation Task")
    return store, active, task


def _decision(store, active, task, evaluation, operation, competition, before, after, lineage):
    source_ids = evaluation["source_experience_ids"]
    return {
        "schema_version": runtime.SCHEMA_VERSION,
        "decision_id": runtime.make_id("decision"),
        "decision": f"{operation} Agent topology " + ", ".join(evaluation["affected_agent_ids"] or [after["agent_topology_id"]]),
        "why": evaluation["reason"],
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "derived_from": [f"experience:{identity}" for identity in source_ids],
        "evidence": source_ids,
        "source_refs": [f"experience:{identity}" for identity in source_ids],
        "created_at": runtime.utc_now(),
        "status": "ACTIVE",
        "supersedes": None,
        "superseded_by": None,
        "project_revision": active.get("project_revision", "unknown"),
        "host_fingerprint": active.get("host_fingerprint", {}).get("fingerprint_id"),
        "nulnul_revision": active.get("nulnul_revision"),
        "scope": "agent-topology",
        "agent_evolution": {
            "operation": operation,
            "affected_agent_ids": evaluation["affected_agent_ids"],
            "source_experience_ids": source_ids,
            "evaluation_digest": evaluation["evaluation_digest"],
            "diagnosis": evaluation.get("diagnosis", ""),
            "expected_benefit": evaluation.get("expected_benefit", ""),
            "coordination_cost": evaluation.get("coordination_cost", ""),
            "regression_risk": evaluation.get("regression_risk", ""),
            "rollback_plan": evaluation.get("rollback_plan", ""),
            "old_topology_digest": before["agent_topology_digest"],
            "new_topology_digest": after["agent_topology_digest"],
            "competition_digest": competition.get("competition_digest") if competition else None,
            "carrying_cost": ({
                "champion": competition["champion_cost"], "challenger": competition["challenger_cost"]
            } if competition else None),
            "lineage": lineage,
            "reconsideration_boundary": {
                "KEEP": "materially new Agent-attributable Experience",
                "UPGRADE": "verified post-upgrade Agent Experience",
                "SPLIT": "verified post-split topology Experience",
                "MERGE": "contradictory verified evidence before another split",
                "REPLACE": "contradictory verified comparison evidence",
                "RETIRE": "new evidence and an explicit reactivation transaction",
                "CREATE": "verified post-create Agent Experience",
            }[operation],
        },
    }


def _current_record(topology):
    return {
        **topology,
        "status": "CURRENT",
        "agents": [{**row, "status": "CURRENT"} for row in topology["agents"]],
    }


def transact(root, evaluation, challenger_digest=None, competition_digest=None, replace=os.replace):
    """Commit one topology decision atomically; capability lifecycle state is untouched."""
    root = Path(root).resolve()
    before = validate_evaluation(root, evaluation)
    if evaluation["result"] in {"NO_ACTION", "MORE_EXPERIENCE_REQUIRED"}:
        raise ValueError("a non-decision evaluation cannot mutate Agent topology")
    operation = _operation(evaluation["result"])
    competition = None
    if operation == "KEEP":
        if challenger_digest or competition_digest:
            raise ValueError("KEEP has no Topology Challenger competition")
        after = before
    else:
        after = load_challenger(root, challenger_digest)
        _validate_operation(before, after, evaluation)
        competition = load_competition(root, competition_digest)
        if (
            competition.get("outcome") != "PROMOTE_CHALLENGER"
            or competition.get("challenger_digest") != challenger_digest
            or competition.get("evaluation_digest") != evaluation["evaluation_digest"]
        ):
            raise ValueError("topology promotion requires one winning frozen competition")
        after = _current_record(after)
    old_ids = {row["agent_id"] for row in before["agents"]}
    new_ids = {row["agent_id"] for row in after["agents"]}
    lineage = {
        "old_topology": before["agent_topology_digest"],
        "new_topology": after["agent_topology_digest"],
        "preserved_agent_ids": sorted(old_ids & new_ids),
        "removed_agent_ids": sorted(old_ids - new_ids),
        "added_agent_ids": sorted(new_ids - old_ids),
    }
    store, active, task = _active_task(root)
    decision = _decision(store, active, task, evaluation, operation, competition, before, after, lineage)
    decisions = runtime.read_jsonl(store.decisions) + [decision]
    index = runtime.load_index(store)
    runtime._add_search(index, "decision", decision)
    index["updated_at"] = runtime.utc_now()
    active = dict(active)
    active.setdefault("decision_ids", []).append(decision["decision_id"])
    event_path = store.local / "events" / f"{active['session_id']}.jsonl"
    events = runtime.read_jsonl(event_path) + [{
        "event_id": len(runtime.read_jsonl(event_path)) + 1,
        "kind": "DECISION",
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "created_at": runtime.utc_now(),
        "details": {"decision_id": decision["decision_id"], "operation": operation, "surface": "agent-topology"},
    }]
    updates = {
        store.decisions: "".join(json.dumps(runtime.redact(row), ensure_ascii=False, sort_keys=True) + "\n" for row in decisions),
        store.index: runtime.encoded(runtime.redact(index)),
        store.active: runtime.encoded(runtime.redact(active)),
        event_path: "".join(json.dumps(runtime.redact(row), ensure_ascii=False, sort_keys=True) + "\n" for row in events),
    }
    if operation != "KEEP":
        archive = {**before, "status": "SUPERSEDED", "agents": [{**row, "status": "SUPERSEDED"} for row in before["agents"]]}
        updates[paths(root)["history"] / f"{before['agent_topology_digest']}.json"] = runtime.encoded(archive)
        updates[paths(root)["current"]] = runtime.encoded(after)
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else None for path in updates}
    with runtime.writer(store):
        try:
            atomic_batch_write(updates, replace=replace)
            errors = validate_state(root)
            if errors:
                raise ValueError("invalid Agent topology after lifecycle mutation: " + "; ".join(errors))
        except Exception:
            natural_selection._restore(originals, root)
            raise
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "COMMITTED",
        "operation": operation,
        "decision_id": decision["decision_id"],
        "old_topology_digest": before["agent_topology_digest"],
        "current_topology_digest": current_topology(root)["agent_topology_digest"],
        "current_agent_ids": [row["agent_id"] for row in current_topology(root)["agents"]],
        "rollback": "NOT_REQUIRED",
    }


def start_agent_task(root, goal, job, agent_id, *, parent_agent_id=None, work_scope=None, tags=None, modules=None):
    topology = current_topology(root)
    agent = next((row for row in topology["agents"] if row["agent_id"] == agent_id), None)
    if not agent:
        raise ValueError("unknown current Agent")
    expected_parent = next((row["parent_agent_id"] for row in topology["edges"] if row["child_agent_id"] == agent_id), None)
    if parent_agent_id != expected_parent:
        raise ValueError("Agent task does not match its delegation edge")
    context = {
        "agent_topology_id": topology["agent_topology_id"],
        "agent_topology_digest": topology["agent_topology_digest"],
        "agent_id": agent_id,
        "agent_contract_digest": agent["agent_contract_digest"],
        "agent_role": agent["role"],
        "parent_agent_id": parent_agent_id,
        "work_scope": work_scope or agent["task_boundary"],
        "verification_owner_agent_id": topology["verification_owner_agent_id"],
        "agent_attribution_scope": "AGENT",
        "responsibility_observed": True,
    }
    return runtime.start_task(root, goal, job, tags, modules, agent_context=context)


def start_topology_task(root, goal, job, *, tags=None, modules=None):
    topology = current_topology(root)
    owner = next(row for row in topology["agents"] if row["agent_id"] == topology["synthesis_owner_agent_id"])
    context = {
        "agent_topology_id": topology["agent_topology_id"],
        "agent_topology_digest": topology["agent_topology_digest"],
        "agent_id": owner["agent_id"],
        "agent_contract_digest": owner["agent_contract_digest"],
        "agent_role": owner["role"],
        "parent_agent_id": None,
        "work_scope": "coordinate and synthesize the bounded topology task",
        "verification_owner_agent_id": topology["verification_owner_agent_id"],
        "agent_attribution_scope": "TOPOLOGY",
        "responsibility_observed": False,
    }
    task = runtime.start_task(root, goal, job, tags, modules, agent_context=context)
    event = runtime.record_event(root, "WORK_SESSION_STARTED", task["task_id"], {
        "agent_topology_id": topology["agent_topology_id"], "surface": "topology",
    })
    store = runtime.Store(root)
    with runtime.writer(store):
        active = runtime.read_json(store.active)
        current = next(row for row in active["tasks"] if row["task_id"] == task["task_id"])
        current["agent_context"]["work_started_event_id"] = event["event_id"]
        runtime.write_json(store.active, active)
    return task


def _task(root, task_id):
    store = runtime.Store(root)
    active = runtime.read_json(store.active)
    task = next((row for row in (active or {}).get("tasks", []) if row["task_id"] == task_id), None)
    if not task or task.get("status") != "ACTIVE":
        raise ValueError("Agent Task is not active")
    return store, active, task


def bind_agent_pack(root, task_id, *, host="codex", selected=None, evidence=None, no_capability=False):
    store, active, task = _task(root, task_id)
    context = task.get("agent_context", {})
    topology = current_topology(root)
    if context.get("agent_topology_digest") != topology["agent_topology_digest"]:
        raise ValueError("Agent Task topology is stale")
    agent = next(row for row in topology["agents"] if row["agent_id"] == context["agent_id"])
    selected = list(dict.fromkeys(selected or []))
    if agent["capability_requirements"] and not set(selected) <= set(agent["capability_requirements"]):
        raise ValueError("Agent Pack exceeds its Capability requirements")
    boot = capability_pack.bootstrap(
        root, Path(root) / "docs/nulnul/project.md", task_id, host,
        selected=selected, evidence=evidence, no_capability=no_capability,
    )
    if boot.get("status") == "SELECTION_REQUIRED":
        return boot
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "agent_topology_id": topology["agent_topology_id"],
        "agent_topology_digest": topology["agent_topology_digest"],
        "agent_id": agent["agent_id"],
        "agent_contract_digest": agent["agent_contract_digest"],
        "task_id": task_id,
        "work_scope": context["work_scope"],
        "pack_id": boot["pack_id"],
        "pack_digest": boot["pack_digest"],
        "capability_ids": boot["capability_ids"],
        "memory_refs": [row["item_id"] for row in task.get("context_pack", {}).get("items", [])],
        "created_at": runtime.utc_now(),
    }
    receipt["agent_pack_binding_id"] = "binding-" + canonical_digest(receipt)
    target = paths(root)["bindings"] / f"{receipt['agent_pack_binding_id']}.json"
    runtime.write_json(target, receipt)
    target.chmod(0o444)
    with runtime.writer(store):
        latest = runtime.read_json(store.active)
        current_task = next(row for row in latest["tasks"] if row["task_id"] == task_id)
        current_task["agent_context"]["agent_pack_binding_id"] = receipt["agent_pack_binding_id"]
        runtime.write_json(store.active, latest)
    return boot | {"agent_pack_binding": receipt}


def record_handoff(root, task_id, status, *, output_refs=None, check_ids=None, next_contract=""):
    _, active, task = _task(root, task_id)
    context = task.get("agent_context", {})
    parent = context.get("parent_agent_id")
    if not parent:
        raise ValueError("only a delegated Agent Task may create an Agent handoff")
    if status not in {"DONE", "FAILED", "OPEN"}:
        raise ValueError("invalid Agent handoff status")
    outputs = _strings(output_refs or [], "handoff output refs", maximum=20)
    checks = _strings(check_ids or [], "handoff Check IDs", maximum=20)
    if any(not re.fullmatch(r"[a-f0-9]{64}", identity) for identity in checks):
        raise ValueError("Agent handoff contains an invalid Check ID")
    row = {
        "schema_version": SCHEMA_VERSION,
        "handoff_id": f"hnd-{uuid.uuid4().hex}",
        "session_id": active["session_id"],
        "task_id": task_id,
        "parent_agent_id": parent,
        "child_agent_id": context["agent_id"],
        "agent_topology_id": context["agent_topology_id"],
        "agent_topology_digest": context["agent_topology_digest"],
        "status": status,
        "output_refs": outputs,
        "check_ids": checks,
        "next_or_return_contract": str(next_contract)[:1024],
        "created_at": runtime.utc_now(),
    }
    if len(runtime.encoded(row).encode()) > 4096:
        raise ValueError("Agent handoff exceeds 4096 bytes")
    target = paths(root)["handoffs"] / f"{row['handoff_id']}.json"
    runtime.write_json(target, row)
    target.chmod(0o444)
    runtime.record_event(root, "AGENT_HANDOFF_RECORDED", task_id, {
        "handoff_id": row["handoff_id"], "status": status, "parent_agent_id": parent,
    })
    return row


def finalize_agent_task(root, pack_id, *, output_refs=None, next_contract=""):
    pack = capability_pack.load_pack(root, pack_id)
    _, _, task = _task(root, pack["task_id"])
    refs = pack["capability_refs"]
    if len(refs) != 1:
        raise ValueError("Agent attribution finalization requires one Capability Pack ref")
    check = capability_pack.run_check(root, pack_id, refs[0]["capability_id"])
    passed = check["result"] == "pass"
    handoff = None
    if task.get("agent_context", {}).get("parent_agent_id"):
        handoff = record_handoff(
            root, task["task_id"], "DONE" if passed else "FAILED",
            output_refs=output_refs, check_ids=[check["check_id"]], next_contract=next_contract,
        )
    outcome = {
        "pack_id": pack_id,
        "check_id": check["check_id"],
        "capability_id": refs[0]["capability_id"],
        "quality": "VERIFIED",
        "observability_completeness": "COMPLETE",
        "result": "SUCCESS" if passed else "FAILURE",
        "product_outcome": "Agent-scoped canonical project check passed" if passed else "Agent-scoped canonical project check failed",
        "checks": [{"id": refs[0]["project_check_identity"], "result": check["result"]}],
        "check_ids": [check["check_id"]],
        "source_refs": ([f"handoff:{handoff['handoff_id']}"] if handoff else []),
    }
    if handoff:
        outcome.update({"handoff_id": handoff["handoff_id"], "handoff_status": handoff["status"]})
    if not passed:
        outcome["verified_failure_reason"] = "the Agent-scoped canonical project check failed"
    experience = runtime.finish_task(root, task["task_id"], outcome)
    return {"check": check, "handoff": handoff, "experience": experience}


def finalize_topology_task(root, task_id, child_experience_ids):
    _, _, task = _task(root, task_id)
    context = task.get("agent_context", {})
    identities = list(dict.fromkeys(child_experience_ids or []))
    if not identities:
        raise ValueError("Topology finalization requires child Agent Experiences")
    experiences = {row["experience_id"]: row for row in _all_experiences(root)}
    children = [experiences.get(identity) for identity in identities]
    if any(
        not row or not row.get("agent_evolution_eligible")
        or row.get("agent_topology_digest") != context.get("agent_topology_digest")
        or row.get("agent_attribution_scope") != "AGENT"
        for row in children
    ):
        raise ValueError("Topology finalization has invalid child Agent Experience")
    if len({row["agent_id"] for row in children}) != len(children):
        raise ValueError("Topology finalization duplicates one Agent responsibility")
    check_ids = [identity for row in children for identity in row.get("check_ids", [])]
    checks = [
        {"id": identity, "result": "pass" if row.get("result") == "SUCCESS" else "fail"}
        for row in children for identity in row.get("check_ids", [])
    ]
    passed = all(row.get("result") == "SUCCESS" for row in children)
    check_order = max(row.get("check_receipt", {}).get("completed_event_id", 0) for row in children)
    outcome = {
        "quality": "VERIFIED",
        "observability_completeness": "COMPLETE",
        "result": "SUCCESS" if passed else "FAILURE",
        "product_outcome": "bounded Agent topology work completed" if passed else "bounded Agent topology work failed verification",
        "checks": checks,
        "check_ids": check_ids,
        "child_agent_experience_ids": identities,
        "agent_attribution_scope": "TOPOLOGY",
        "source_refs": [f"experience:{identity}" for identity in identities],
        "agent_ordering": {
            "topology_bound": context.get("topology_bound_event_id"),
            "work_started": context.get("work_started_event_id"),
            "check": check_order,
        },
    }
    if not passed:
        outcome["verified_failure_reason"] = "one or more child Agent authoritative checks failed"
    return runtime.finish_task(root, task_id, outcome)


def validate_state(root):
    errors = []
    known_topologies = {}
    try:
        current = current_topology(root)
        known_topologies[current["agent_topology_digest"]] = current
    except (OSError, UnicodeError, ValueError) as error:
        return [str(error)]
    history = paths(root)["history"]
    if history.exists():
        for path in history.glob("*.json"):
            try:
                row = runtime.read_json(path)
                validate_topology(
                    root, row, allowed_statuses={"SUPERSEDED", "RETIRED"},
                    require_current_capabilities=False,
                )
                known_topologies[row["agent_topology_digest"]] = row
            except (OSError, UnicodeError, ValueError) as error:
                errors.append(f"{path.name}: {error}")
    experiences = {row["experience_id"]: row for row in _all_experiences(root)}
    for row in runtime.read_jsonl(runtime.Store(root).decisions):
        agent = row.get("agent_evolution")
        if not agent:
            continue
        identity = row.get("decision_id")
        if agent.get("operation") not in OPERATIONS:
            errors.append(f"{identity}: invalid Agent Evolution operation")
        if any(source not in experiences for source in agent.get("source_experience_ids", [])):
            errors.append(f"{identity}: dangling Agent Evolution Experience")
        for field in ("old_topology_digest", "new_topology_digest"):
            if agent.get(field) not in known_topologies:
                errors.append(f"{identity}: dangling Agent topology lineage {field}")
        expected = {f"experience:{source}" for source in agent.get("source_experience_ids", [])}
        if not expected <= set(row.get("source_refs", [])):
            errors.append(f"{identity}: incomplete Agent Evolution provenance")
    for path in paths(root)["bindings"].glob("*.json") if paths(root)["bindings"].exists() else []:
        try:
            binding = runtime.read_json(path)
            topology = known_topologies.get(binding.get("agent_topology_digest"))
            if not topology or topology.get("agent_topology_id") != binding.get("agent_topology_id"):
                raise ValueError("dangling Agent Pack topology")
            agent = next((row for row in topology["agents"] if row["agent_id"] == binding.get("agent_id")), None)
            if not agent or agent["agent_contract_digest"] != binding.get("agent_contract_digest"):
                raise ValueError("dangling Agent Pack binding")
            pack = capability_pack.load_pack(root, binding.get("pack_id"), binding.get("task_id"))
            selected = {row["capability_id"] for row in pack["capability_refs"]}
            if selected != set(binding.get("capability_ids", [])):
                raise ValueError("Agent Pack binding capability mismatch")
            if agent["capability_requirements"] and not selected <= set(agent["capability_requirements"]):
                raise ValueError("Agent Pack binding exceeds Capability requirements")
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"{path.name}: {error}")
    for path in paths(root)["handoffs"].glob("*.json") if paths(root)["handoffs"].exists() else []:
        try:
            handoff = runtime.read_json(path)
            topology = known_topologies.get(handoff.get("agent_topology_digest"))
            edge = next((
                row for row in (topology or {}).get("edges", [])
                if row["parent_agent_id"] == handoff.get("parent_agent_id")
                and row["child_agent_id"] == handoff.get("child_agent_id")
            ), None)
            if not topology or topology.get("agent_topology_id") != handoff.get("agent_topology_id") or not edge:
                raise ValueError("dangling Agent handoff")
            if handoff.get("status") not in {"DONE", "FAILED", "OPEN"}:
                raise ValueError("invalid Agent handoff status")
            if any(not re.fullmatch(r"[a-f0-9]{64}", str(identity)) for identity in handoff.get("check_ids", [])):
                raise ValueError("invalid Agent handoff Check ID")
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"{path.name}: {error}")
    errors.extend(runtime.validate_lineage(root))
    return sorted(set(errors))


def real_review(root):
    """Inspect existing durable evidence without inventing an Agent weakness."""
    experiences = _all_experiences(root)
    eligible = [row for row in experiences if row.get("agent_evolution_eligible")]
    return {
        "schema_version": SCHEMA_VERSION,
        "topology": current_topology(root),
        "verified_experience_count": sum(row.get("quality") == "VERIFIED" for row in experiences),
        "agent_evolution_eligible_count": len(eligible),
        "agent_mutation_justified": False,
        "decision": "NO_ACTION" if eligible else "MORE_EXPERIENCE_REQUIRED",
        "reason": "no verified Agent-attributable weakness exists in current Foundation evidence",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("topology")
    review = sub.add_parser("evaluate")
    review.add_argument("review", type=Path)
    candidate = sub.add_parser("challenger")
    candidate.add_argument("evaluation", type=Path)
    candidate.add_argument("specification", type=Path)
    compete = sub.add_parser("compete")
    compete.add_argument("evaluation", type=Path)
    compete.add_argument("challenger_digest")
    compete.add_argument("evidence", type=Path)
    apply = sub.add_parser("transact")
    apply.add_argument("evaluation", type=Path)
    apply.add_argument("--challenger-digest")
    apply.add_argument("--competition-digest")
    sub.add_parser("validate")
    sub.add_parser("real-review")
    args = parser.parse_args()
    try:
        if args.command == "topology":
            payload = topology_snapshot(args.root)
        elif args.command == "evaluate":
            payload = evaluate(args.root, runtime.read_json(args.review))
        elif args.command == "challenger":
            payload = freeze_challenger(args.root, runtime.read_json(args.evaluation), runtime.read_json(args.specification))
        elif args.command == "compete":
            payload = freeze_competition(args.root, runtime.read_json(args.evaluation), args.challenger_digest, runtime.read_json(args.evidence))
        elif args.command == "transact":
            payload = transact(args.root, runtime.read_json(args.evaluation), args.challenger_digest, args.competition_digest)
        elif args.command == "real-review":
            payload = real_review(args.root)
        else:
            errors = validate_state(args.root)
            payload = {"valid": not errors, "errors": errors}
        failed = payload.get("valid") is False
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        payload = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
