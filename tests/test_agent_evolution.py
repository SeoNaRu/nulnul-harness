import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import agent_evolution
import foundation_runtime as runtime
import natural_selection
import sync_host_entry
from test_natural_selection import NaturalSelectionCase


class AgentEvolutionCase(NaturalSelectionCase):
    def agent_spec(self, key, role, responsibility, *, source=None, capabilities=None, **changes):
        row = {
            "agent_key": key,
            "role": role,
            "job": f"Own {responsibility}",
            "responsibilities": [responsibility],
            "task_boundary": f"bounded {responsibility}",
            "input_contract": ["parent task", "bounded project context"],
            "output_contract": ["bounded artifact refs", "authoritative Check ID"],
            "capability_requirements": capabilities or [],
            "tool_requirements": [],
            "delegation_rules": [],
            "verification_responsibility": "execute assigned checks when designated",
            "authority_boundary": "task-owned product writes only",
            "handoff_contract": ["DONE, FAILED, or OPEN", "artifact refs", "return contract"],
            "failure_escalation": ["return one bounded causal failure"],
            "context_requirements": ["role-scoped Memory", "role-scoped Capability Pack"],
        }
        if source:
            row.update({field: source[field] for field in agent_evolution.AGENT_FIELDS})
            row["source_agent_id"] = source["agent_id"]
        row.update(changes)
        return row

    def seed_topology(self, agents, edges=None, synthesis=None, verification=None):
        rows = [agent_evolution.agent_contract(row) for row in agents]
        topology = {
            "schema_version": 1,
            "agent_topology_id": "topology-project-execution",
            "version": 1,
            "topology_kind": "SINGLE_AGENT" if len(rows) == 1 else "MULTI_AGENT",
            "status": "CURRENT",
            "agents": sorted(rows, key=lambda row: row["agent_id"]),
            "edges": sorted(edges or [], key=lambda row: (row["parent_agent_id"], row["child_agent_id"])),
            "synthesis_owner_agent_id": synthesis or rows[0]["agent_id"],
            "verification_owner_agent_id": verification or rows[0]["agent_id"],
            "created_at": runtime.utc_now(),
            "derived_from": [],
        }
        topology["agent_topology_digest"] = agent_evolution._topology_digest(topology)
        agent_evolution.validate_topology(self.root, topology, allowed_statuses={"CURRENT"})
        runtime.write_json(agent_evolution.paths(self.root)["current"], topology)
        return topology

    def two_agent_topology(self):
        implementation = self.agent_spec(
            "implementation", "implementation Agent", "api-implementation",
            capabilities=["project-api-validation"],
        ) | {"agent_id": "agent-implementation"}
        verification = self.agent_spec(
            "verification", "verification Agent", "release-verification",
            capabilities=["project-release-docs"],
        ) | {"agent_id": "agent-verification"}
        edge = {
            "parent_agent_id": "agent-implementation",
            "child_agent_id": "agent-verification",
            "parent_task_boundary": "API implementation",
            "child_task_boundary": "independent release verification",
            "expected_output": "verified bounded result",
            "allowed_scope": "verification-owned files only",
            "required_check": "project-contract",
            "return_contract": "DONE, FAILED, or OPEN with artifact refs",
        }
        return self.seed_topology(
            [implementation, verification], [edge], "agent-implementation", "agent-verification"
        )

    def agent_experience(self, agent_id=None, capability="project-api-validation", success=True):
        topology = agent_evolution.current_topology(self.root)
        agent_id = agent_id or topology["agents"][0]["agent_id"]
        parent = next((row["parent_agent_id"] for row in topology["edges"] if row["child_agent_id"] == agent_id), None)
        goal = (
            "Validate API behavior and error catalog changes"
            if capability == "project-api-validation"
            else "Preserve release documentation changes and release contract"
        )
        runtime.start_session(self.root, goal, self.fingerprint)
        task = agent_evolution.start_agent_task(
            self.root, goal, "project contract work", agent_id,
            parent_agent_id=parent, work_scope=goal,
        )
        if not success:
            project = self.root / "docs/nulnul/project.md"
            project.write_text(project.read_text(encoding="utf-8").replace("`true`", "`false`", 1), encoding="utf-8")
        boot = agent_evolution.bind_agent_pack(
            self.root, task["task_id"], selected=[capability],
            evidence="the exact accepted project contract governs this Agent scope",
        )
        (self.root / f"agent-work-{task['task_id']}.txt").write_text("done\n", encoding="utf-8")
        result = agent_evolution.finalize_agent_task(
            self.root, boot["pack_id"], output_refs=[f"agent-work-{task['task_id']}.txt"],
            next_contract="return verified result to the parent",
        )["experience"]
        runtime.finalize_session(self.root, "COMPLETED" if success else "PARTIAL", completeness="COMPLETE")
        if not success:
            project = self.root / "docs/nulnul/project.md"
            project.write_text(project.read_text(encoding="utf-8").replace("`false`", "`true`", 1), encoding="utf-8")
        return result

    def review(self, signal, experiences, affected=None, **extra):
        payload = {
            "trigger": extra.pop("trigger", "material-evidence"),
            "signal": signal,
            "affected_agent_ids": affected or [],
            "source_experience_ids": [row["experience_id"] for row in experiences],
        }
        if signal not in {"success-only", "none", "insufficient"}:
            payload.update({
                "diagnosis": "verified evidence identifies one bounded Agent topology weakness",
                "expected_benefit": "stronger verified project outcome",
                "coordination_cost": "one bounded handoff when the topology has multiple Agents",
                "regression_risk": "responsibility changes could regress current verified behavior",
                "what_must_not_change": "Capability lifecycle and task-owned authority",
                "rollback_plan": "restore the frozen Agent topology Champion",
            })
        payload.update(extra)
        return agent_evolution.evaluate(self.root, payload)

    def source_spec(self, agent, **changes):
        return self.agent_spec(agent["agent_id"], agent["role"], agent["responsibilities"][0], source=agent, **changes)

    def competition(self, champion_digest, challenger_digest, *, equivalent=False):
        passed = {"strict": True, "project_check": True, "completion": True, "unauthorized_writes": 0}
        failed = {"strict": False, "project_check": False, "completion": False, "unauthorized_writes": 0}
        groups = [
            {
                "group": "TARGET_WEAKNESS", "task_hash": "a" * 64, "fixture_hash": "b" * 64,
                "project_revision": "fixture-v1", "check_identities": ["project-contract"],
                "allowed_writes": ["task-owned"], "champion": dict(passed if equivalent else failed),
                "challenger": dict(passed),
            },
            {
                "group": "SEALED_HOLDOUT", "task_hash": "c" * 64, "fixture_hash": "d" * 64,
                "project_revision": "fixture-v1", "check_identities": ["project-contract"],
                "allowed_writes": ["task-owned"], "champion": dict(passed), "challenger": dict(passed),
            },
        ]
        champion_cost = {field: 10 for field in agent_evolution.COST_FIELDS}
        challenger_cost = {field: (5 if field in {"pack_bytes", "memory_bytes", "maintenance_units"} else 10) for field in agent_evolution.COST_FIELDS}
        payload = {
            "champion_digest": champion_digest,
            "challenger_digest": challenger_digest,
            "task_groups": groups,
            "champion_cost": champion_cost,
            "challenger_cost": challenger_cost,
        }
        if equivalent:
            payload.update({"meaningful_advantage": "LOWER_CONTEXT", "advantage_verified": True})
        return payload

    def apply_candidate(self, evaluation, specification, *, equivalent=False, replace=os.replace):
        challenger = agent_evolution.freeze_challenger(self.root, evaluation, specification)
        competition = agent_evolution.freeze_competition(
            self.root, evaluation, challenger["agent_topology_digest"],
            self.competition(evaluation["champion_digest"], challenger["agent_topology_digest"], equivalent=equivalent),
        )
        self.start("Apply Agent topology lifecycle", "agent topology maintenance")
        return agent_evolution.transact(
            self.root, evaluation, challenger["agent_topology_digest"], competition["competition_digest"], replace=replace,
        )


class AgentEvolutionEvaluatorTests(AgentEvolutionCase):
    def test_implicit_single_agent_is_champion_and_keep_is_anti_churn(self):
        topology = agent_evolution.current_topology(self.root)
        self.assertEqual(topology["topology_kind"], "SINGLE_AGENT")
        experience = self.agent_experience()
        evaluation = self.review("success-only", [experience], ["agent-primary"], trigger="explicit-maintenance")
        self.assertEqual(evaluation["result"], "KEEP")
        self.start()
        result = agent_evolution.transact(self.root, evaluation)
        self.assertEqual(result["operation"], "KEEP")
        runtime.finalize_session(self.root, "ABORTED")
        repeated = self.review("success-only", [experience], ["agent-primary"])
        self.assertEqual(repeated["result"], "NO_ACTION")
        self.assertFalse(agent_evolution.paths(self.root)["current"].exists())

    def test_mutation_signals_require_agent_attributable_repeated_evidence(self):
        generic = self.generic_experience()
        weak = self.review("agent-contract-gap", [generic], ["agent-primary"])
        self.assertEqual(weak["result"], "MORE_EXPERIENCE_REQUIRED")
        failures = [self.agent_experience(success=False), self.agent_experience(success=False)]
        split = self.review(
            "responsibility-overload", failures, ["agent-primary"],
            overloaded_responsibilities=["implementation", "verification"],
        )
        self.assertEqual(split["result"], "SPLIT_CANDIDATE")

    def test_real_review_does_not_invent_agent_weakness(self):
        self.capability_experience()
        review = agent_evolution.real_review(self.root)
        self.assertEqual(review["agent_evolution_eligible_count"], 0)
        self.assertEqual(review["decision"], "MORE_EXPERIENCE_REQUIRED")
        self.assertFalse(review["agent_mutation_justified"])

    def test_missing_capability_emits_natural_selection_need_without_agent_mutation(self):
        experiences = [self.generic_experience(), self.generic_experience()]
        evaluation = self.review(
            "missing-capability", experiences, ["agent-primary"],
            required_capability_type="SKILL",
            required_capability_job="uncovered deployment validation",
            project_check_concept="verify the deployment contract",
        )
        self.assertEqual(evaluation["result"], "NO_ACTION")
        need = evaluation["natural_selection_need"]
        self.assertEqual(need["signal"], "recurring-uncovered-job")
        self.assertEqual(need["requested_capability_type"], "SKILL")
        self.assertEqual(natural_selection.evaluate(self.root, need)["result"], "CREATE_CANDIDATE")


class AgentEvolutionLifecycleTests(AgentEvolutionCase):
    def test_upgrade_preserves_agent_identity_and_supersedes_topology(self):
        failure = self.agent_experience(success=False)
        evaluation = self.review("agent-contract-gap", [failure], ["agent-primary"])
        primary = agent_evolution.current_topology(self.root)["agents"][0]
        specification = {
            "agents": [self.source_spec(primary, handoff_contract=primary["handoff_contract"] + ["include failure locus"])],
            "edges": [], "synthesis_owner_agent_id": "agent-primary", "verification_owner_agent_id": "agent-primary",
        }
        result = self.apply_candidate(evaluation, specification)
        current = agent_evolution.current_topology(self.root)
        self.assertEqual(result["operation"], "UPGRADE")
        self.assertEqual(current["agents"][0]["agent_id"], "agent-primary")
        self.assertEqual(current["agents"][0]["version"], 2)
        self.assertTrue((agent_evolution.paths(self.root)["history"] / f"{result['old_topology_digest']}.json").is_file())

    def test_split_creates_isolated_responsibilities_and_pack_requirements(self):
        failures = [self.agent_experience(success=False), self.agent_experience(success=False)]
        evaluation = self.review(
            "responsibility-overload", failures, ["agent-primary"],
            overloaded_responsibilities=["implementation", "verification"],
        )
        specification = {
            "agents": [
                self.agent_spec("implementation", "implementation Agent", "api-implementation", capabilities=["project-api-validation"]),
                self.agent_spec("verification", "verification Agent", "release-verification", capabilities=["project-release-docs"]),
            ],
            "edges": [{
                "parent_agent_key": "implementation", "child_agent_key": "verification",
                "parent_task_boundary": "API implementation", "child_task_boundary": "independent verification",
                "expected_output": "verified bounded result", "allowed_scope": "verification only",
                "required_check": "project-contract", "return_contract": "DONE, FAILED, or OPEN",
            }],
            "synthesis_owner_agent_key": "implementation", "verification_owner_agent_key": "verification",
        }
        result = self.apply_candidate(evaluation, specification)
        current = agent_evolution.current_topology(self.root)
        self.assertEqual(result["operation"], "SPLIT")
        self.assertEqual(len(current["agents"]), 2)
        self.assertEqual({row["responsibilities"][0] for row in current["agents"]}, {"api-implementation", "release-verification"})

    def test_merge_promotes_equivalent_quality_lower_cost_single_agent(self):
        topology = self.two_agent_topology()
        evidence = [
            self.agent_experience("agent-implementation", "project-api-validation"),
            self.agent_experience("agent-verification", "project-release-docs"),
        ]
        evaluation = self.review(
            "duplicate-agent-work", evidence, ["agent-implementation", "agent-verification"],
            independent_value_absent=True,
        )
        specification = {
            "agents": [self.agent_spec("merged", "project Agent", "project-contract", capabilities=["project-api-validation", "project-release-docs"])],
            "edges": [], "synthesis_owner_agent_key": "merged", "verification_owner_agent_key": "merged",
        }
        result = self.apply_candidate(evaluation, specification, equivalent=True)
        self.assertEqual(result["operation"], "MERGE")
        self.assertEqual(agent_evolution.current_topology(self.root)["topology_kind"], "SINGLE_AGENT")

    def test_replace_retire_and_create_have_distinct_lineage(self):
        experience = self.agent_experience()
        replace = self.review(
            "replacement-advantage", [experience], ["agent-primary"], replacement_agent_key="domain",
        )
        replacement = {
            "agents": [self.agent_spec("domain", "domain Agent", "product-work")],
            "edges": [], "synthesis_owner_agent_key": "domain", "verification_owner_agent_key": "domain",
        }
        result = self.apply_candidate(replace, replacement)
        self.assertEqual(result["operation"], "REPLACE")
        self.assertNotIn("agent-primary", result["current_agent_ids"])

        # RETIRE is validated on a fresh two-Agent fixture so one active owner remains.
        self.tearDown()
        self.setUp()
        self.two_agent_topology()
        child = self.agent_experience("agent-verification", "project-release-docs")
        retire = self.review(
            "obsolete-responsibility", [child], ["agent-verification"], absorbed_by_agent_id="agent-implementation",
        )
        primary = next(row for row in agent_evolution.current_topology(self.root)["agents"] if row["agent_id"] == "agent-implementation")
        retired = self.apply_candidate(retire, {
            "agents": [self.source_spec(primary)], "edges": [],
            "synthesis_owner_agent_id": "agent-implementation", "verification_owner_agent_id": "agent-implementation",
        })
        self.assertEqual(retired["operation"], "RETIRE")

        self.tearDown()
        self.setUp()
        evidence = [self.generic_experience("independent artifact review"), self.generic_experience("independent artifact review")]
        create = self.review(
            "recurring-uncovered-responsibility", evidence, uncovered_responsibility="independent artifact review",
        )
        primary = agent_evolution.current_topology(self.root)["agents"][0]
        created = self.apply_candidate(create, {
            "agents": [self.source_spec(primary), self.agent_spec("review", "review Agent", "independent-review")],
            "edges": [{
                "parent_agent_id": "agent-primary", "child_agent_key": "review",
                "parent_task_boundary": "product work", "child_task_boundary": "independent review",
                "expected_output": "review result", "allowed_scope": "read and verify",
                "required_check": "project-contract", "return_contract": "DONE, FAILED, or OPEN",
            }],
            "synthesis_owner_agent_id": "agent-primary", "verification_owner_agent_key": "review",
        })
        self.assertEqual(created["operation"], "CREATE")
        self.assertEqual(len(created["current_agent_ids"]), 2)


class AgentExecutionIntegrationTests(AgentEvolutionCase):
    def test_pack_per_agent_isolated_and_handoff_bounded(self):
        self.two_agent_topology()
        runtime.start_session(self.root, "bounded Agent work", self.fingerprint)
        api = agent_evolution.start_agent_task(
            self.root, "Validate API behavior and error catalog changes", "API work", "agent-implementation"
        )
        release = agent_evolution.start_agent_task(
            self.root, "Preserve release documentation changes", "release work", "agent-verification",
            parent_agent_id="agent-implementation",
        )
        api_pack = agent_evolution.bind_agent_pack(
            self.root, api["task_id"], selected=["project-api-validation"], evidence="API responsibility match"
        )
        release_pack = agent_evolution.bind_agent_pack(
            self.root, release["task_id"], selected=["project-release-docs"], evidence="release responsibility match"
        )
        self.assertEqual(api_pack["capability_ids"], ["project-api-validation"])
        self.assertEqual(release_pack["capability_ids"], ["project-release-docs"])
        self.assertNotIn("project-release-docs", json.dumps(api_pack["model_context"]))
        self.assertNotIn("project-api-validation", json.dumps(release_pack["model_context"]))
        runtime.finalize_session(self.root, "ABORTED")
        self.assertEqual(agent_evolution.validate_state(self.root), [])

    def test_agent_and_topology_experiences_share_foundation_provenance(self):
        self.two_agent_topology()
        runtime.start_session(self.root, "topology task", self.fingerprint)
        parent = agent_evolution.start_topology_task(self.root, "topology task", "project contract work")
        child_ids = []
        for identity, capability, goal in (
            ("agent-implementation", "project-api-validation", "Validate API behavior and error catalog changes"),
            ("agent-verification", "project-release-docs", "Preserve release documentation changes"),
        ):
            task = agent_evolution.start_agent_task(
                self.root, goal, "project contract work", identity,
                parent_agent_id="agent-implementation" if identity == "agent-verification" else None,
            )
            boot = agent_evolution.bind_agent_pack(
                self.root, task["task_id"], selected=[capability], evidence="exact Agent responsibility match"
            )
            (self.root / f"work-{task['task_id']}.txt").write_text("done\n", encoding="utf-8")
            child_ids.append(agent_evolution.finalize_agent_task(self.root, boot["pack_id"])["experience"]["experience_id"])
        topology_experience = agent_evolution.finalize_topology_task(self.root, parent["task_id"], child_ids)
        runtime.finalize_session(self.root, completeness="COMPLETE")
        self.assertTrue(topology_experience["agent_evolution_eligible"])
        self.assertEqual(topology_experience["agent_attribution_scope"], "TOPOLOGY")
        self.assertEqual(topology_experience["child_agent_experience_ids"], child_ids)
        self.assertEqual(runtime.validate_lineage(self.root), [])


class AgentEvolutionFailureTests(AgentEvolutionCase):
    def candidate_evaluation(self):
        failure = self.agent_experience(success=False)
        return self.review("agent-contract-gap", [failure], ["agent-primary"])

    def upgraded_spec(self):
        primary = agent_evolution.current_topology(self.root)["agents"][0]
        return {
            "agents": [self.source_spec(primary, failure_escalation=primary["failure_escalation"] + ["name the failed boundary"])],
            "edges": [], "synthesis_owner_agent_id": "agent-primary", "verification_owner_agent_id": "agent-primary",
        }

    def test_graph_rejects_unknown_capability_missing_owner_cycle_and_dangling_edge(self):
        evaluation = self.candidate_evaluation()
        invalid = self.upgraded_spec()
        invalid["agents"][0]["capability_requirements"] = ["missing-capability"]
        with self.assertRaisesRegex(ValueError, "unknown or retired Capability"):
            agent_evolution.freeze_challenger(self.root, evaluation, invalid)
        missing = self.upgraded_spec()
        missing["verification_owner_agent_id"] = "agent-missing"
        with self.assertRaisesRegex(ValueError, "verification owners"):
            agent_evolution.freeze_challenger(self.root, evaluation, missing)

        first = self.agent_spec("a", "A", "a") | {"agent_id": "agent-a"}
        second = self.agent_spec("b", "B", "b") | {"agent_id": "agent-b"}
        edge = {
            "parent_agent_id": "agent-a", "child_agent_id": "agent-b",
            "parent_task_boundary": "a", "child_task_boundary": "b", "expected_output": "b",
            "allowed_scope": "b", "required_check": "project-contract", "return_contract": "return",
        }
        cycle = dict(edge, parent_agent_id="agent-b", child_agent_id="agent-a")
        with self.assertRaisesRegex(ValueError, "cyclic"):
            self.seed_topology([first, second], [edge, cycle], "agent-a", "agent-b")
        dangling = dict(edge, child_agent_id="agent-missing")
        with self.assertRaisesRegex(ValueError, "dangling"):
            self.seed_topology([first, second], [dangling], "agent-a", "agent-b")

    def test_unknown_experience_stale_champion_and_promotion_without_competition_fail(self):
        with self.assertRaisesRegex(ValueError, "unknown source Experience"):
            agent_evolution.evaluate(self.root, {
                "signal": "success-only", "affected_agent_ids": ["agent-primary"],
                "source_experience_ids": ["exp-missing"],
            })
        evaluation = self.candidate_evaluation()
        challenger = agent_evolution.freeze_challenger(self.root, evaluation, self.upgraded_spec())
        with self.assertRaisesRegex(ValueError, "competition digest"):
            self.start()
            agent_evolution.transact(self.root, evaluation, challenger["agent_topology_digest"])
        runtime.finalize_session(self.root, "ABORTED")

        self.seed_topology([self.agent_spec("other", "other Agent", "other") | {"agent_id": "agent-other"}])
        self.start()
        with self.assertRaisesRegex(ValueError, "stale Agent topology Champion"):
            agent_evolution.transact(self.root, evaluation)

    def test_dangling_handoff_is_rejected(self):
        self.two_agent_topology()
        self.agent_experience("agent-verification", "project-release-docs")
        path = next(agent_evolution.paths(self.root)["handoffs"].glob("*.json"))
        receipt = runtime.read_json(path)
        path.chmod(0o600)
        receipt["child_agent_id"] = "agent-missing"
        runtime.write_json(path, receipt)
        self.assertTrue(any("dangling Agent handoff" in error for error in agent_evolution.validate_state(self.root)))

    def test_partial_transaction_rolls_back_and_broken_provenance_fails(self):
        evaluation = self.candidate_evaluation()
        challenger = agent_evolution.freeze_challenger(self.root, evaluation, self.upgraded_spec())
        competition = agent_evolution.freeze_competition(
            self.root, evaluation, challenger["agent_topology_digest"],
            self.competition(evaluation["champion_digest"], challenger["agent_topology_digest"]),
        )
        self.start()
        store = runtime.Store(self.root)
        before = {path: path.read_bytes() if path.exists() else None for path in (store.decisions, store.index, store.active, agent_evolution.paths(self.root)["current"])}
        calls = 0

        def fail_second(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected Agent transaction failure")
            os.replace(source, target)

        with self.assertRaisesRegex(OSError, "injected Agent"):
            agent_evolution.transact(
                self.root, evaluation, challenger["agent_topology_digest"], competition["competition_digest"], replace=fail_second,
            )
        for path, content in before.items():
            self.assertEqual(path.read_bytes() if path.exists() else None, content)

        result = agent_evolution.transact(
            self.root, evaluation, challenger["agent_topology_digest"], competition["competition_digest"]
        )
        decisions = runtime.read_jsonl(store.decisions)
        decisions[-1]["agent_evolution"]["source_experience_ids"] = ["exp-dangling"]
        runtime.write_jsonl(store.decisions, decisions)
        self.assertTrue(any("dangling Agent Evolution Experience" in error for error in agent_evolution.validate_state(self.root)))
        self.assertEqual(result["operation"], "UPGRADE")

    def test_competition_quality_dominates_cost_and_direct_has_zero_fixed_surface(self):
        evaluation = self.candidate_evaluation()
        challenger = agent_evolution.freeze_challenger(self.root, evaluation, self.upgraded_spec())
        evidence = self.competition(evaluation["champion_digest"], challenger["agent_topology_digest"], equivalent=True)
        evidence["task_groups"][1]["challenger"]["project_check"] = False
        evidence["challenger_cost"] = {field: 0 for field in agent_evolution.COST_FIELDS}
        result = agent_evolution.freeze_competition(self.root, evaluation, challenger["agent_topology_digest"], evidence)
        self.assertEqual(result["outcome"], "KEEP_CURRENT")

        class State:
            def as_posix(self):
                return "docs/nulnul/checkpoint.json"

        block = sync_host_entry.managed_block("codex", State())
        self.assertNotIn("Agent Evolution", block)
        self.assertNotIn("agent_evolution.py", block)

        redacted = runtime.redact({"authority_boundary": "task-only", "input_tokens": 10, "access_token": "secret"})
        self.assertEqual(redacted["authority_boundary"], "task-only")
        self.assertEqual(redacted["input_tokens"], 10)
        self.assertEqual(redacted["access_token"], "[REDACTED]")


if __name__ == "__main__":
    unittest.main()
