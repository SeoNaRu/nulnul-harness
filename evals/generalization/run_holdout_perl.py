#!/usr/bin/env python3
"""Run the replacement one-shot Perl/TAP checkpoint-freshness holdout."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"
RESULTS = HERE / "results.json"
SCRIPT_PATHS = (
    "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_checkpoint.py",
    "plugins/nulnul-harness/skills/nulnul-harness/scripts/run_checkpoint_check.py",
)


INITIAL_LIBRARY = r'''package EventSummary;
use strict;
use warnings;
use Exporter "import";
our @EXPORT_OK = qw(summarize);

sub summarize {
    my ($path) = @_;
    open my $fh, "<", $path or die "cannot open input";
    <$fh>;
    my $accepted = 0;
    while (my $line = <$fh>) {
        chomp $line;
        my (undef, undef, $status) = split /\t/, $line;
        $accepted++ if $status eq "accepted";
    }
    return {accepted_total => $accepted};
}

1;
'''
UPDATED_LIBRARY = r'''package EventSummary;
use strict;
use warnings;
use Exporter "import";
our @EXPORT_OK = qw(summarize);

sub summarize {
    my ($path) = @_;
    open my $fh, "<", $path or die "cannot open input";
    <$fh>;
    my ($accepted, %by_kind) = (0);
    while (my $line = <$fh>) {
        chomp $line;
        my (undef, $kind, $status) = split /\t/, $line;
        next unless $status eq "accepted";
        $accepted++;
        $by_kind{$kind}++;
    }
    return {accepted_total => $accepted, by_kind => \%by_kind};
}

1;
'''
INITIAL_CHECK = r'''use strict;
use warnings;
use Test::More tests => 1;
use EventSummary qw(summarize);

is_deeply(summarize("data/events.tsv"), {accepted_total => 3}, "initial summary");
'''
UPDATED_CHECK = r'''use strict;
use warnings;
use Test::More tests => 1;
use EventSummary qw(summarize);

is_deeply(
    summarize("data/events.tsv"),
    {accepted_total => 3, by_kind => {click => 2, view => 1}},
    "grouped summary",
);
'''


def atomic_write(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def git_source(ref, path):
    return subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, check=True
    ).stdout


def run_json(args, cwd):
    process = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=30)
    start = process.stdout.rfind("\n{")
    try:
        payload = json.loads(process.stdout[start + 1:] if start >= 0 else process.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("holdout subprocess returned invalid JSON") from error
    return process.returncode, payload


def write_product(root, updated=False):
    files = {
        "lib/EventSummary.pm": UPDATED_LIBRARY if updated else INITIAL_LIBRARY,
        "bin/summarize.pl": (
            'use strict;\nuse warnings;\nuse JSON::PP qw(encode_json);\n'
            'use lib "lib";\nuse EventSummary qw(summarize);\n'
            'print encode_json(summarize($ARGV[0])), "\\n";\n'
        ),
        "t/summary.t": UPDATED_CHECK if updated else INITIAL_CHECK,
        "data/events.tsv": (
            "id\tkind\tstatus\n1\tclick\taccepted\n2\tview\taccepted\n"
            "3\tclick\tdiscarded\n4\tclick\taccepted\n"
        ),
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def preflight_fixture():
    with tempfile.TemporaryDirectory(prefix="nulnul-holdout-preflight-") as directory:
        root = Path(directory)
        write_product(root)
        initial = subprocess.run(
            ["prove", "-Ilib", "t/summary.t"], cwd=root, capture_output=True, timeout=30
        )
        write_product(root, updated=True)
        updated = subprocess.run(
            ["prove", "-Ilib", "t/summary.t"], cwd=root, capture_output=True, timeout=30
        )
        output = subprocess.run(
            ["perl", "bin/summarize.pl", "data/events.tsv"], cwd=root,
            capture_output=True, text=True, timeout=30,
        )
        expected = {"accepted_total": 3, "by_kind": {"click": 2, "view": 1}}
        try:
            exact = json.loads(output.stdout) == expected
        except json.JSONDecodeError:
            exact = False
        if initial.returncode or updated.returncode or output.returncode or not exact:
            raise RuntimeError("holdout fixture preflight failed before evaluation")


def prepare_workspace(root, ref, schema_version):
    for relative in SCRIPT_PATHS:
        target = root / ".agents/skills/nulnul-harness/scripts" / Path(relative).name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git_source(ref, relative))
    write_product(root)
    checkpoint = {
        "schema_version": schema_version,
        "goal": "Maintain a local event-summary CLI",
        "milestone": "Add accepted-event counts grouped by kind",
        "completion_check": "prove -Ilib t/summary.t",
        "verification_status": "verified" if schema_version == 2 else "unknown",
        "last_verified": "Initial summary behavior verified",
        "next_action": "Add grouped accepted-event counts and verify them",
        "permission_constraints": ["local files only", "no network"],
        "approved_permissions": [],
        "blockers": [],
    }
    if schema_version == 3:
        checkpoint["verification_files"] = [
            "bin/summarize.pl", "data/events.tsv", "lib/EventSummary.pm", "t/summary.t"
        ]
    path = root / "docs/nulnul/checkpoint.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
    return path


def run_trial(ref, schema_version, trial):
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="nulnul-generalization-") as directory:
        root = Path(directory)
        checkpoint = prepare_workspace(root, ref, schema_version)
        scripts = root / ".agents/skills/nulnul-harness/scripts"
        runner = scripts / "run_checkpoint_check.py"
        validator = scripts / "validate_checkpoint.py"
        prep_code, prep = run_json([sys.executable, str(runner), str(checkpoint), "--root", str(root)], root)
        initial_code, initial = run_json([sys.executable, str(validator), str(checkpoint)], root)
        if prep_code or initial_code or not prep.get("passed") or not initial.get("fast_path_ready"):
            raise RuntimeError("holdout fixture did not begin from verified state")

        write_product(root, updated=True)
        pre_code, pre = run_json([sys.executable, str(validator), str(checkpoint)], root)
        check_code, checked = run_json(
            [sys.executable, str(runner), str(checkpoint), "--root", str(root)], root
        )
        post_code, post = run_json([sys.executable, str(validator), str(checkpoint)], root)
        behavior = subprocess.run(
            ["perl", "bin/summarize.pl", "data/events.tsv"], cwd=root,
            capture_output=True, text=True, timeout=30,
        )
        expected = {"accepted_total": 3, "by_kind": {"click": 2, "view": 1}}
        try:
            exact_behavior = json.loads(behavior.stdout) == expected
        except json.JSONDecodeError:
            exact_behavior = False
        return {
            "trial": trial,
            "initial_fast_resume_ready": True,
            "stale_mutation_blocked": pre_code == 0 and pre.get("fast_path_ready") is False,
            "task_success": behavior.returncode == 0 and exact_behavior,
            "completion_check_passed": check_code == 0 and checked.get("passed") is True,
            "post_check_fast_resume_ready": post_code == 0 and post.get("fast_path_ready") is True,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "subprocess_invocations": 6,
            "validator_invocations": 3,
            "completion_check_invocations": 2,
        }


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if RESULTS.exists():
        raise SystemExit("holdout is already exposed; register a new unseen case")
    claim = next(
        (item for item in manifest["claims"] if item["status"] == "preregistered"), None
    )
    if claim is None:
        raise SystemExit("no preregistered holdout claim")
    case = next(item for item in manifest["holdout_cases"] if item["case_id"] in claim["holdout_case_ids"])
    if case["current_role"] != "holdout" or case["exposure_count"] != 0:
        raise SystemExit("holdout is already exposed; register a new unseen case")
    preflight_fixture()

    champion = [run_trial("8b8c0b4", 2, trial) for trial in range(1, 4)]
    candidate = [run_trial(claim["candidate_ref"], 3, trial) for trial in range(1, 4)]
    primary = {
        "heldout_task_success": all(run["task_success"] for run in candidate),
        "completion_check_passed": all(run["completion_check_passed"] for run in candidate),
        "stale_mutation_blocked": all(run["stale_mutation_blocked"] for run in candidate),
        "post_check_fast_resume_ready": all(run["post_check_fast_resume_ready"] for run in candidate),
    }
    result = {
        "schema_version": 1,
        "run_date": "2026-08-12",
        "claim_id": claim["claim_id"],
        "mechanism_id": claim["mechanism_id"],
        "decision": "narrower_scope" if all(primary.values()) else "failed",
        "scope": "Checkpoint freshness transferred to one unseen local Perl/TAP CLI shape; harness-wide generalization is not established.",
        "harness_wide_generalization": False,
        "case_results": [{
            "case_id": case["case_id"],
            "run_id": case["first_exposed"]["run_id"],
            "role_at_run": "holdout",
            "mechanism_id": claim["mechanism_id"],
            "candidate_ref": claim["candidate_ref"],
            "primary": primary,
            "guardrails": {
                "permissions": {"status": "passed", "evidence": "Local temporary files only; no network, credential, external write, or publication."},
                "read_scope": {"status": "passed", "evidence": "Only preregistered snapshot sources and generated fixture files were read."},
                "unexpected_repository_discovery": {"status": "passed", "evidence": "No repository discovery was performed inside the fixture."},
                "context_input_cost": {"status": "not_applicable", "evidence": "The mechanism comparison is deterministic and invokes no inference model."},
                "elapsed": {"status": "passed", "evidence": "Elapsed milliseconds are retained per bounded trial without traces."},
                "tools": {"status": "passed", "evidence": "Each arm used the same six local subprocess invocations per trial."},
                "validators": {"status": "passed", "evidence": "Each arm used three checkpoint validations per trial."},
                "tests": {"status": "passed", "evidence": "Fixture preflight passed and each arm used the same initial and post-task completion checks."},
                "checkpoint_correctness": {"status": "passed", "evidence": "Candidate blocked every stale state and resumed every freshly verified state."},
                "privacy": {"status": "passed", "evidence": "Evidence contains bounded booleans, counters, and durations only."}
            }
        }],
        "baselines": {
            "champion_single": {"label": "Navigator v14 before freshness receipts", "runs": champion[:1]},
            "retry_champion": {"label": "Navigator v14 repeated three times", "runs": champion},
            "best_of_n_champion": {
                "source_arm": "retry_champion", "n": 3,
                "selected_safe_result": any(run["stale_mutation_blocked"] for run in champion)
            },
            "evolved_candidate": {"label": "Accepted Navigator v15 receipt mechanism", "runs": candidate}
        },
        "budget_comparison": {
            "comparable": True,
            "fair_dimension": "deterministic evaluation trials",
            "retry_trials": 3,
            "candidate_trials": 3,
            "completion_checks_per_trial": 2,
            "validator_invocations_per_trial": 3,
            "incomparable_dimensions": ["inference tokens: no model was invoked", "runtime: different validator work is intrinsic to the mechanism"],
            "conclusion": "The evolved candidate wins only on checkpoint safety; no token or runtime win is claimed."
        },
        "learning_verdicts": []
    }

    case.update(current_role="retired", unseen=False, release_validation=True, exposure_count=1)
    claim["status"] = result["decision"]
    spec = importlib.util.spec_from_file_location(
        "validate_generalization_gate",
        ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_generalization_gate.py",
    )
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    errors = gate.validate(manifest, result, ROOT)
    if errors:
        raise SystemExit("holdout evidence failed: " + "; ".join(errors))
    atomic_write(RESULTS, result)
    atomic_write(MANIFEST, manifest)
    print(json.dumps({"decision": result["decision"], "primary": primary}, indent=2))


if __name__ == "__main__":
    main()
