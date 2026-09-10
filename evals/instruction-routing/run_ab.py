#!/usr/bin/env python3
"""Bounded instruction A/B using the existing activation runner; never run by unittest."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location(
    "activation", ROOT / "evals/benchmarks/activation/run_activation.py"
)
activation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(activation)
FAST = "verified-checkpoint-fast-path"
RENAME_ORACLE = [
    "python3", "-c",
    "import app; assert app.sum_values(2, 3) == 5; assert not hasattr(app, 'add')",
]
SKILL = '.agents/skills/nulnul-harness'
CHECKPOINT = 'docs/nulnul/checkpoint.json'
TRACE_CONTRACT = (
    '\nEvaluation trace contract (identical for both arms): use separate literal cat commands '
    'for file reads, the native apply_patch tool for edits, and literal python3 commands for '
    'the documented validators/checks. Do not use shell compound commands, globs, redirection, '
    'substitutions, inline Python, or additional tools. The evaluator fails closed on syntax '
    'outside this bounded grammar. Preserve fixed checkpoint goal, completion_check, '
    'verification_files and permission fields; only refresh stale progress/verification fields.'
)


def trace_auditor(workspace, fast=True):
    """Audit a constrained DEV trace, not arbitrary shell execution or an OS syscall log."""
    workspace = workspace.resolve()
    allowed_reads = {'app.py', 'test_app.py', CHECKPOINT, SKILL + '/SKILL.md'} if fast else {
        'TASK.md', 'app.py', 'check.py'}
    allowed_edits = {'app.py', 'test_app.py', CHECKPOINT} if fast else {'app.py'}
    runtime_writes = allowed_edits | ({'docs/nulnul/checkpoint.verification.json'} if fast else set())

    def files():
        return {str(p.relative_to(workspace)): ('symlink' if p.is_symlink() else sha(p))
                for p in workspace.rglob('*') if p.is_file() or p.is_symlink()
                if '__pycache__' not in p.parts and p.suffix != '.pyc'}

    initial_files = files()
    initial_checkpoint = json.loads((workspace / CHECKPOINT).read_text()) if fast else None

    def relative(value):
        path = workspace / value
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != workspace.parent):
            raise ValueError('symlink path')
        return path.resolve().relative_to(workspace).as_posix()

    def audit(stdout):
        reads, forbidden, reasons, seen, started = set(), set(), [], set(), set()
        edited_paths = set()
        counts = {'checkpoint_runner': 0, 'direct': 0}
        last_edit, last_check, turns = -1, -1, 0
        first_edit, validator_events = float('inf'), []
        for index, line in enumerate(stdout.splitlines()):
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError('event is not an object')
                item = event.get('item', {})
                if event.get('type') == 'turn.completed':
                    turns += 1
                if event.get('type') == 'item.started':
                    started.add(item['id'])
                if event.get('type') != 'item.completed':
                    if event.get('type') not in {'thread.started', 'turn.started', 'turn.completed',
                                                 'item.started', 'item.updated'}:
                        raise ValueError('unsupported event')
                    continue
                identity = item['id']
                if identity in seen:
                    raise ValueError('duplicate event')
                seen.add(identity)
                kind = item['type']
                if kind in {'agent_message', 'reasoning'}:
                    continue
                if kind == 'file_change':
                    if item.get('status') != 'completed' or not item.get('changes'):
                        raise ValueError('incomplete edit')
                    for change in item['changes']:
                        changed_path = relative(change['path'])
                        if changed_path not in allowed_edits:
                            raise ValueError('unapproved edit')
                        edited_paths.add(changed_path)
                    last_edit = index
                    first_edit = min(first_edit, index)
                    continue
                if kind != 'command_execution' or item.get('exit_code') != 0:
                    raise ValueError('unsupported or unsuccessful execution')
                command = item['command']
                tokens = shlex.split(command)
                if len(tokens) == 3 and tokens[0] in {'bash', '/bin/bash', 'sh', '/bin/sh'} and tokens[1] in {'-c', '-lc'}:
                    command = tokens[2]
                    tokens = shlex.split(command)
                # ponytail: a closed command grammar; unsupported syntax gets no evidence credit.
                if not tokens or any(c in command for c in '$`*?[]{}();\n|&<>\\~#'):
                    raise ValueError('unsupported shell syntax')
                if tokens[0] in {'cat', '/bin/cat', '/usr/bin/cat'}:
                    operands = tokens[1:]
                    if operands[:1] == ['--']:
                        operands = operands[1:]
                    if not operands or any(p.startswith('-') for p in operands):
                        raise ValueError('unsupported reader options')
                    for operand in operands:
                        path = relative(operand)
                        if not (workspace / path).is_file():
                            raise ValueError('missing read target')
                        reads.add(path)
                        if path not in allowed_reads:
                            forbidden.add(path)
                elif tokens[0] in {'echo', 'pwd'}:
                    if tokens[0] == 'pwd' and len(tokens) != 1:
                        raise ValueError('unsupported pwd options')
                else:
                    if tokens[0] not in {'python', 'python3', '/usr/bin/python3', '/usr/bin/python'}:
                        raise ValueError('unsupported executable')
                    args = activation.python_command(tokens)[1:]
                    if fast and args == ['-m', 'unittest', '-q']:
                        counts['direct'] += 1
                        last_check = index
                    elif not fast and len(args) == 1 and relative(args[0]) == 'check.py':
                        counts['direct'] += 1
                        last_check = index
                    elif fast and len(args) in {2, 4}:
                        script, checkpoint = relative(args[0]), relative(args[1])
                        if (checkpoint != CHECKPOINT or script not in {
                                SKILL + '/scripts/validate_checkpoint.py',
                                SKILL + '/scripts/run_checkpoint_check.py'} or
                                (len(args) == 4 and (args[2] != '--root' or relative(args[3]) != '.'))):
                            raise ValueError('unsupported check arguments')
                        if script.endswith('/run_checkpoint_check.py'):
                            counts['checkpoint_runner'] += 1
                            last_check = index
                        else:
                            validator_events.append(index)
                    else:
                        raise ValueError('unsupported Python invocation')
            except (ValueError, KeyError, TypeError, OSError):
                reasons.append({'event': index, 'code': 'unsupported_or_invalid_event'})
        current_files = files()
        changed = {p for p in initial_files.keys() | current_files.keys()
                   if initial_files.get(p) != current_files.get(p)}
        if changed - runtime_writes:
            reasons.append({'code': 'protected_file_changed'})
        if changed & (allowed_edits - {CHECKPOINT}) - edited_paths:
            reasons.append({'code': 'missing_native_edit_evidence'})
        if any(v == 'symlink' for v in current_files.values()):
            reasons.append({'code': 'symlink_present'})
        fixed_fields = True
        if fast:
            try:
                current = json.loads((workspace / CHECKPOINT).read_text())
                fixed_fields = all(current.get(k) == initial_checkpoint.get(k) for k in (
                    'goal', 'completion_check', 'verification_files', 'permission_constraints', 'approved_permissions'))
            except (OSError, ValueError, AttributeError):
                fixed_fields = False
        if turns != 1 or started - seen:
            reasons.append({'code': 'incomplete_trace'})
        if last_check <= last_edit or last_check < 0:
            reasons.append({'code': 'worker_check_missing_after_edit'})
        if fast and (len(validator_events) != 1 or validator_events[0] >= first_edit):
            reasons.append({'code': 'initial_validator_missing_repeated_or_late'})
        if not fixed_fields:
            reasons.append({'code': 'fixed_checkpoint_field_changed'})
        return {'schema_version': 2, 'status': 'unknown' if reasons else 'failed' if forbidden else 'verified',
                'read_paths': sorted(reads & allowed_reads),
                'forbidden_read_paths': sorted(forbidden), 'reasons': reasons,
                'completion_check_invocations_by_kind': counts,
                'initial_validator_invocations': len(validator_events),
                'fixed_checkpoint_fields_preserved': fixed_fields,
                'scope': 'closed DEV command grammar; conflict/inactive-host transfer cases not exercised'}

    return audit


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root):
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob('*') if p.is_file()
                       and '__pycache__' not in p.parts and p.suffix != '.pyc'):
        name = path.relative_to(root).as_posix().encode()
        content = path.read_bytes()
        digest.update(len(name).to_bytes(4, 'big') + name)
        digest.update(len(content).to_bytes(8, 'big') + content)
    return digest.hexdigest()


def exact_fast_run(row):
    truth = row.get('checkpoint_truth') or {}
    counts = row.get('telemetry', {}).get('completion_check_invocations_by_kind', {})
    return (row.get('correct') is True and row.get('behavior_check_exit_code') == 0
            and row.get('command_audit', {}).get('status') == 'verified'
            and truth.get('product_mutated') is True
            and truth.get('fresh_resume_accepted') is True
            and truth.get('unverified_mutated_repository_state_accepted_for_fast_resume') is False
            and counts == {'checkpoint_runner': 1, 'direct': 0})


def exact_control_run(row):
    return (row.get('correct') is True and row.get('behavior_check_exit_code') == 0
            and row.get('activated') is False
            and row.get('command_audit', {}).get('status') == 'verified'
            and row.get('telemetry', {}).get('completion_check_invocations_by_kind') == {
                'checkpoint_runner': 0, 'direct': 1})


def score(rows):
    paired = [dict(row, correct=exact_fast_run(row)) for row in rows if row.get('phase') == 'paired']
    expected = [(r, arm) for r in range(1, 5)
                for arm in (('champion', 'candidate') if r % 2 else ('candidate', 'champion'))]
    if [(row['round'], row['arm']) for row in paired] != expected:
        return {'decision': 'NO_PROMOTION', 'reason': 'incomplete or incorrect paired order'}
    comparison = activation.paired_comparison(paired, 'champion', 'candidate')
    changes = comparison['paired_change_percent']
    eligible = comparison['eligible_pairs'] == 4 and comparison['candidate_correct'] == 4
    costs = (isinstance(changes['input_tokens'], (int, float)) and changes['input_tokens'] < 0
             and isinstance(changes['elapsed_seconds'], (int, float))
             and changes['elapsed_seconds'] <= 10)
    champion = [r for r in paired if r['arm'] == 'champion']
    return {'decision': 'ELIGIBLE_FOR_INDEPENDENT_GATE' if eligible and costs else 'NO_PROMOTION',
            'comparison': comparison,
            'simple_retry_baseline': {'attempts': 4, 'completed': sum(r['correct'] for r in champion),
                                      'all_attempt_input_tokens': sum(r.get('input_tokens') or 0 for r in champion)},
            'claim_boundary': 'Four same-model paired DEV/VALIDATION tasks; no holdout, transfer or release credit.'}


def write(path, payload):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--champion', type=Path, required=True, help='Frozen plugin root')
    parser.add_argument('--candidate', type=Path, required=True, help='Frozen plugin root')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--phase', choices=('paired', 'controls', 'live'), default='paired')
    parser.add_argument('--authorized-model-calls', action='store_true',
                        help='Operator must already have user authorization; this flag grants none')
    args = parser.parse_args()
    if not args.authorized_model_calls:
        parser.error('Explicit user authorization for external model calls is required')
    frozen = json.loads((HERE / 'candidate-v2.json').read_text())
    for arm in ('champion', 'candidate'):
        if tree_digest(getattr(args, arm)) != frozen[arm + '_plugin_sha256']:
            parser.error('Frozen ' + arm + ' tree changed')
    for name, digest in frozen['evaluation_sha256'].items():
        if sha(ROOT / name) != digest:
            parser.error('Frozen evaluation changed: ' + name)
    registered = json.loads((HERE / 'preregistration-v2.json').read_text())
    authorization = json.loads((HERE / 'authorization.json').read_text())
    prior = registered['prior_attempts']
    if sha(ROOT / prior['evidence']) != prior['sha256']:
        parser.error('Prior attempt accounting changed')
    budget = registered['budget']
    payload = json.loads(args.out.read_text()) if args.out.exists() else {
        'schema_version': 2, 'episode_id': registered['episode_id'], 'model': budget['model'],
        'effort': budget['reasoning_effort'], 'records': [], 'learning_verdicts': [],
        'prior_external_model_invocations': prior['count'],
        'raw_transcripts_retained': False, 'candidate': frozen,
    }
    if payload['candidate'] != frozen:
        parser.error('Output belongs to a different candidate')
    if any(r['phase'] == args.phase for r in payload['records']):
        parser.error('Phase already attempted; preserve exposure and inspect its result')
    if args.phase == 'live' and payload.get('gate', {}).get('decision') != 'PROVISIONAL':
        parser.error('An independent provisional Gate decision is required before the live cycle')
    schedule = ([(r, arm) for r in range(1, 5)
                 for arm in (('champion', 'candidate') if r % 2 else ('candidate', 'champion'))]
                if args.phase == 'paired' else [(1, 'candidate')] if args.phase == 'live'
                else [(1, 'champion'), (1, 'candidate')])
    total = prior['count'] + len(payload['records']) + len(schedule)
    if total > min(budget['max_external_model_invocations'], authorization['max_external_model_invocations']):
        parser.error('Cumulative approved/preregistered invocation budget cannot cover this phase')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Isolate personal skills/config while using only the explicitly authorized login.
    with tempfile.TemporaryDirectory(prefix='nulnul-eval-home-') as temporary_home:
        auth = Path.home() / '.codex/auth.json'
        if not auth.is_file():
            parser.error('Existing Codex login is unavailable')
        shutil.copyfile(auth, Path(temporary_home) / 'auth.json')
        os.chmod(Path(temporary_home) / 'auth.json', 0o600)
        previous = os.environ.get('CODEX_HOME')
        os.environ['CODEX_HOME'] = temporary_home
        try:
            for round_index, arm in schedule:
                case_name = FAST if args.phase != 'controls' else 'instruction-local-repair'
                case = copy.deepcopy(activation.CASES[FAST])
                case['gate_check'] = RENAME_ORACLE
                if args.phase == 'controls':
                    case = {
                        'category': 'covered-task', 'expect_activation': False,
                        'files': {'app.py': 'def add(a, b):\n    return a - b\n',
                                  'check.py': 'from app import add\nassert add(2, 3) == 5\n',
                                  'TASK.md': '# Repair\nFix app.py addition. Standard library, local files only. Completion: python3 check.py.\n'},
                        'prompt': 'Implement the repair in TASK.md, run its check, and finish. No network, installation, or publication.',
                        'completion_check': 'python3 check.py',
                        'gate_check': ['python3', '-c', 'import app; assert app.add(-2, 3) == 1; assert app.add(2, 3) == 5'],
                        'forbidden_reads': ('/references/', 'personal_adaptation.py', 'generalization_core.py'),
                    }
                case['prompt'] += TRACE_CONTRACT
                row = {'phase': args.phase, 'round': round_index, 'arm': arm, 'status': 'started'}
                payload['records'].append(row)
                payload['cumulative_external_model_invocations'] = prior['count'] + len(payload['records'])
                write(args.out, payload)  # Count an attempt before calling the model.
                try:
                    observed = activation.run_case(case_name, case, arm,
                        getattr(args, arm) / 'skills/nulnul-harness', budget['model'],
                        budget['reasoning_effort'], budget['max_model_seconds_per_call'], round_index,
                        audit_factory=lambda workspace: trace_auditor(workspace, args.phase != 'controls'))
                    observed.pop('agent_error', None)
                    row.update(observed, status='completed')
                    row['correct'] = (exact_control_run(row) if args.phase == 'controls' else exact_fast_run(row))
                    if 'experience_digest' in row:
                        row['experience_digest']['verification_result'] = (
                            'verified' if row['correct'] else 'failed')
                except (OSError, ValueError, RuntimeError, activation.subprocess.TimeoutExpired) as error:
                    row.update(status='failed', correct=False, error_type=type(error).__name__)
                if row.get('correct') is not True:
                    payload['learning_verdicts'].append({
                        'id': f"{args.phase}-{round_index}-{arm}", 'status': 'failed',
                        'feedback_id': registered['feedback_id'], 'proposal_ids': [registered['proposal_id']]})
                write(args.out, payload)
                print(json.dumps({'phase': args.phase, 'round': round_index, 'arm': arm,
                                  'correct': row.get('correct')}), flush=True)
                if row.get('correct') is not True:
                    break  # Preserve exposure; diagnose any nonpass before spending another call.
        finally:
            if previous is None:
                os.environ.pop('CODEX_HOME', None)
            else:
                os.environ['CODEX_HOME'] = previous
    payload['comparison'] = score(payload['records'])
    write(args.out, payload)


if __name__ == '__main__':
    main()
