import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "run_activation", ROOT / "evals/benchmarks/activation/run_activation.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ActivationBenchmarkTests(unittest.TestCase):
    def test_matrix_covers_both_routing_directions_and_fast_path(self):
        cases = MODULE.CASES.values()
        self.assertGreaterEqual(len(MODULE.CASES), 10)
        self.assertGreaterEqual(sum(not case["expect_activation"] for case in cases), 4)
        self.assertGreaterEqual(sum(case["expect_activation"] for case in cases), 4)
        fast = MODULE.CASES["verified-checkpoint-fast-path"]
        self.assertIn("docs/nulnul/checkpoint.json", fast["required_reads"])
        self.assertIn("docs/nulnul/project.md", fast["forbidden_reads"])

    def test_command_trace_ignores_paths_only_printed_by_a_read(self):
        stdout = "\n".join([
            json.dumps({"item": {"command": "sed -n '1,80p' .agents/skills/nulnul-harness/SKILL.md"}}),
            json.dumps({"item": {"output": "Read references/baseline-kernel.md later"}}),
        ])
        trace = MODULE.command_trace(stdout)
        self.assertIn("nulnul-harness/SKILL.md", trace)
        self.assertNotIn("references/baseline-kernel.md", trace)

    def test_telemetry_counts_tools_without_storing_commands(self):
        stdout = "\n".join([
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "command": "sed -n '1,20p' app.py"
            }}),
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "command": "python3 -m unittest -q"
            }}),
            json.dumps({"type": "item.completed", "item": {"type": "reasoning"}}),
        ])
        telemetry = MODULE.execution_telemetry(stdout)
        self.assertEqual(telemetry["tool_calls"], 2)
        self.assertEqual(telemetry["shell_commands"], 2)
        self.assertEqual(telemetry["read_commands"], 1)
        self.assertEqual(telemetry["test_commands"], 1)
        self.assertNotIn("commands", telemetry)

    def test_paired_comparison_uses_matching_rounds(self):
        records = []
        for round_index, champion_tokens, candidate_tokens in ((1, 100, 90), (2, 200, 220), (3, 300, 240)):
            for arm, tokens in (("champion", champion_tokens), ("candidate", candidate_tokens)):
                records.append({
                    "round": round_index, "case": "fast", "arm": arm, "correct": True,
                    "elapsed_seconds": tokens / 10, "input_tokens": tokens,
                    "output_tokens": tokens / 10, "reasoning_output_tokens": tokens / 20,
                })
        comparison = MODULE.paired_comparison(records, "champion", "candidate")
        self.assertEqual(comparison["pairs"], 3)
        self.assertEqual(comparison["eligible_pairs"], 3)
        self.assertEqual(comparison["champion_correct"], 3)
        self.assertEqual(comparison["candidate_correct"], 3)
        self.assertEqual(comparison["paired_change_percent"]["input_tokens"], -10.0)

    def test_paired_comparison_excludes_a_failed_baseline_pair(self):
        records = []
        for round_index, champion_correct in ((1, True), (2, False), (3, True), (4, True)):
            for arm in ("champion", "candidate"):
                records.append({
                    "round": round_index, "case": "fast", "arm": arm,
                    "correct": champion_correct if arm == "champion" else True,
                    "elapsed_seconds": 10, "input_tokens": 100,
                    "output_tokens": 10, "reasoning_output_tokens": 5,
                })
        comparison = MODULE.paired_comparison(records, "champion", "candidate")
        self.assertEqual(comparison["eligible_pairs"], 3)
        self.assertEqual(comparison["excluded_pairs"][0]["round"], 2)

    def test_summary_fails_on_one_wrong_or_full_contract_run(self):
        records = []
        for round_index in range(3):
            records.append({
                "round": round_index + 1,
                "case": "verified-checkpoint-fast-path",
                "category": "fast-path",
                "arm": "current",
                "expected_activation": True,
                "activated": True,
                "correct": round_index != 2,
                "elapsed_seconds": 2 + round_index,
                "input_tokens": 100 + round_index,
                "output_tokens": 10,
                "reasoning_output_tokens": 5,
            })
        summary = MODULE.summarize(records)
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["arms"][0]["fast_path_correct_runs"], 2)

    def test_runner_keeps_a_bounded_agent_error(self):
        source = (ROOT / "evals/benchmarks/activation/run_activation.py").read_text(encoding="utf-8")
        self.assertIn('process.stderr.strip()[-2000:]', source)
        self.assertIn("round_index % 2", source)
        self.assertIn("paired runs require an even round count", source)


if __name__ == "__main__":
    unittest.main()
