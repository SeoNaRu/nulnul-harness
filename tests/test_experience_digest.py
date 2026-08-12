import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load("run_activation", ROOT / "evals/benchmarks/activation/run_activation.py")
VALIDATOR = load(
    "validate_experience_digest",
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_experience_digest.py",
)


class ExperienceDigestTests(unittest.TestCase):
    def test_exact_completion_checks_are_attributed_without_commands(self):
        stdout = "\n".join(json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "command": command,
        }}) for command in (
            "sed -n '1,80p' run_checkpoint_check.py",
            "python3 -m unittest -q",
            "python3 -B tools/run_checkpoint_check.py docs/nulnul/checkpoint.json --root .",
        ))
        telemetry = RUNNER.execution_telemetry(stdout, "python3 -m unittest -q")
        self.assertEqual(telemetry["test_commands"], 3)
        self.assertEqual(telemetry["completion_check_invocations"], 2)
        self.assertEqual(
            telemetry["completion_check_invocations_by_kind"],
            {"checkpoint_runner": 1, "direct": 1},
        )
        self.assertNotIn("commands", telemetry)

    def test_exact_completion_check_unwraps_shell_lc(self):
        commands = [
            "/bin/bash -lc 'python .agents/skills/nulnul-harness/scripts/"
            "run_checkpoint_check.py docs/nulnul/checkpoint.json'"
        ]
        self.assertEqual(
            RUNNER.completion_check_counts(commands, "python3 -m unittest -q"),
            {"checkpoint_runner": 1, "direct": 0},
        )

    def test_digest_rejects_bad_stage_and_trace_fields(self):
        digest = RUNNER.experience_digest(
            "fast:champion:r1", "fast", "fast-path", "champion", 1.2, 0.1,
            {
                "tool_calls": 2, "read_commands": 1, "validator_commands": 1,
                "test_commands": 2, "completion_check_invocations": 2,
            },
            {"input_tokens": 100, "output_tokens": 10}, 0, True,
        )
        self.assertEqual(VALIDATOR.validate(digest), [])
        self.assertEqual(digest["signals"], ["completion_check_repeated"])
        digest["stages"][0]["stage"] = "thinking"
        digest["raw_transcript"] = "private"
        digest["machine_path"] = "/tmp/private"
        errors = VALIDATOR.validate(digest)
        self.assertIn("stages[0].stage is invalid", errors)
        self.assertIn("digest.raw_transcript is prohibited", errors)
        self.assertIn("digest fields are not allowed: machine_path, raw_transcript", errors)

    def test_first_divergence_stays_unknown_without_a_structural_difference(self):
        left = {"stages": [{"stage": "resume", "completion_check_invocations": 1}]}
        self.assertEqual(
            RUNNER.first_divergence(left, json.loads(json.dumps(left)))["status"],
            "unknown",
        )
        right = {"stages": [{"stage": "resume", "completion_check_invocations": 2}]}
        self.assertEqual(RUNNER.first_divergence(left, right), {
            "status": "verified", "stage": "resume", "signal": "completion_check_invocations",
        })

    def test_lifecycle_signals_only_count_verification_after_implementation(self):
        def event(item_type, **fields):
            return json.dumps({"type": "item.completed", "item": {"type": item_type, **fields}})

        before_only = "\n".join((
            event("command_execution", command="python3 tools/validate_checkpoint.py checkpoint.json"),
            event("file_change"),
            event("agent_message", text="done"),
        ))
        self.assertEqual(RUNNER.lifecycle_signals(before_only, "python3 -m unittest -q", True), [
            "implementation_completed", "final_synthesis_observed",
            "final_synthesis_without_verification",
        ])

        after = "\n".join((
            event("file_change"),
            event("command_execution", command=(
                "python3 .agents/skills/nulnul-harness/scripts/run_checkpoint_check.py "
                "docs/nulnul/checkpoint.json --root ."
            )),
            event("agent_message", text="done"),
        ))
        self.assertEqual(RUNNER.lifecycle_signals(after, "python3 -m unittest -q", True), [
            "implementation_completed", "verification_stage_entered",
            "wrapper_invocation_observed", "final_synthesis_observed",
        ])


if __name__ == "__main__":
    unittest.main()
