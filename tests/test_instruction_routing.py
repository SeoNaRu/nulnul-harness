import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('instruction_ab', ROOT / 'evals/instruction-routing/run_ab.py')
AB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AB)


def passing_pairs():
    rows = []
    for round_index in range(1, 5):
        for arm in (('champion', 'candidate') if round_index % 2 else ('candidate', 'champion')):
            rows.append({
                'phase': 'paired', 'round': round_index, 'arm': arm, 'case': AB.FAST,
                'correct': True, 'behavior_check_exit_code': 0,
                'command_audit': {'status': 'verified'},
                'input_tokens': 100 if arm == 'champion' else 80, 'elapsed_seconds': 10,
                'telemetry': {'completion_check_invocations_by_kind': {'checkpoint_runner': 1, 'direct': 0}},
                'checkpoint_truth': {'product_mutated': True, 'fresh_resume_accepted': True,
                    'unverified_mutated_repository_state_accepted_for_fast_resume': False},
            })
    return rows


class InstructionRoutingTests(unittest.TestCase):
    def test_behavior_cost_and_missing_evidence_cannot_gain_promotion(self):
        rows = passing_pairs()
        self.assertEqual(AB.score(rows)['decision'], 'ELIGIBLE_FOR_INDEPENDENT_GATE')
        for field, value in [('correct', False), ('behavior_check_exit_code', 1),
                             ('input_tokens', None), ('input_tokens', 120), ('elapsed_seconds', 12)]:
            changed = copy.deepcopy(rows)
            for row in changed:
                if row['arm'] == 'candidate':
                    row[field] = value
            self.assertEqual(AB.score(changed)['decision'], 'NO_PROMOTION', field)
        self.assertEqual(AB.score(rows[:-1])['decision'], 'NO_PROMOTION')
        self.assertEqual(AB.score(list(reversed(rows)))['decision'], 'NO_PROMOTION')

    def test_duplicate_checks_and_stale_resume_fail_even_with_passing_product(self):
        row = passing_pairs()[1]
        for key, value in [('product_mutated', False), ('fresh_resume_accepted', False),
                          ('unverified_mutated_repository_state_accepted_for_fast_resume', True)]:
            changed = copy.deepcopy(row)
            changed['checkpoint_truth'][key] = value
            self.assertFalse(AB.exact_fast_run(changed))
        row['telemetry']['completion_check_invocations_by_kind']['direct'] = 1
        self.assertFalse(AB.exact_fast_run(row))

    def test_trace_audit_rejects_ambiguous_reads_duplicate_checks_and_missing_events(self):
        def trace(commands):
            commands = [f'python3 {AB.SKILL}/scripts/validate_checkpoint.py {AB.CHECKPOINT}', *commands]
            return '\n'.join([*(json.dumps({'type': 'item.completed', 'item': {
                'id': str(i), 'type': 'command_execution', 'command': command, 'exit_code': 0,
            }}) for i, command in enumerate(commands)), json.dumps({'type': 'turn.completed'})])

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name, content in AB.activation.CASES[AB.FAST]['files'].items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            auditor = AB.trace_auditor(root)
            runner = f'python3 {AB.SKILL}/scripts/run_checkpoint_check.py {AB.CHECKPOINT} --root .'
            good = trace(['cat app.py test_app.py', runner])
            self.assertEqual(auditor(good)['status'], 'verified')
            self.assertNotEqual(auditor(good.split('\n', 1)[1])['status'], 'verified')
            self.assertNotEqual(auditor(trace([f'python3 {AB.SKILL}/scripts/validate_checkpoint.py {AB.CHECKPOINT}', runner]))['status'], 'verified')
            self.assertEqual(auditor(trace([f"/bin/bash -lc '{runner}'"]))['status'], 'verified')
            for bad in [
                'cat AGENTS.md', 'cat docs/nulnul/project.md', 'cat docs/nulnul/proj*.md',
                'cat ../outside', 'cat /etc/passwd', 'cat $(echo app.py)',
                'cat app.py > copy.py', 'cat app.py && cat docs/nulnul/project.md',
                'python3 -c "print(1)"', runner + ' --help',
                'python3 -c pass ' + AB.SKILL + '/scripts/run_checkpoint_check.py',
            ]:
                with self.subTest(bad=bad):
                    self.assertNotEqual(auditor(trace([bad, runner]))['status'], 'verified')
            duplicate = auditor(trace([runner, 'python3 -B -m unittest -q']))
            self.assertEqual(duplicate['completion_check_invocations_by_kind'], {
                'checkpoint_runner': 1, 'direct': 1})
            self.assertEqual(auditor(trace(['echo app.py', runner]))['read_paths'], [])
            self.assertNotEqual(auditor(trace(['echo ' + runner]))['status'], 'verified')
            for invalid in [good + '\n' + good, good.replace('"exit_code": 0', '"exit_code": 1'),
                            good.rsplit('\n', 1)[0], good + '\nnot-json',
                            good + '\n' + json.dumps({'type': 'item.started', 'item': {'id': 'unfinished'}}),
                            good + '\n' + json.dumps({'type': 'item.completed', 'item': {'id': 'x', 'type': 'mcp_tool_call'}})]:
                self.assertNotEqual(auditor(invalid)['status'], 'verified')
            link = root / 'alias.py'
            link.symlink_to(root / 'app.py')
            self.assertNotEqual(auditor(trace(['cat alias.py', runner]))['status'], 'verified')

    def test_protected_files_checkpoint_fields_and_check_order_cannot_pass(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name, content in AB.activation.CASES[AB.FAST]['files'].items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            auditor = AB.trace_auditor(root)
            events = [
                {'type': 'item.completed', 'item': {'id': 'read', 'type': 'command_execution',
                    'command': 'cat app.py', 'exit_code': 0}},
                {'type': 'item.completed', 'item': {'id': 'edit', 'type': 'file_change',
                    'changes': [{'path': str(root / 'app.py'), 'kind': 'update'}], 'status': 'completed'}},
                {'type': 'item.completed', 'item': {'id': 'check', 'type': 'command_execution',
                    'command': f'python3 {AB.SKILL}/scripts/run_checkpoint_check.py {AB.CHECKPOINT}', 'exit_code': 0}},
                {'type': 'turn.completed'},
            ]
            events[0]['item']['command'] = f'python3 {AB.SKILL}/scripts/validate_checkpoint.py {AB.CHECKPOINT}'
            good = '\n'.join(map(json.dumps, events))
            self.assertEqual(auditor(good)['status'], 'verified')
            self.assertNotEqual(auditor('\n'.join(map(json.dumps, [events[0], events[2], events[1], events[3]])))['status'], 'verified')
            for protected in ['CLAUDE.md', 'docs/nulnul/checkpoint.verification.json', AB.SKILL + '/scripts/run_checkpoint_check.py']:
                changed = copy.deepcopy(events)
                changed[1]['item']['changes'][0]['path'] = protected
                self.assertNotEqual(auditor('\n'.join(map(json.dumps, changed)))['status'], 'verified')
            checkpoint_path = root / AB.CHECKPOINT
            original = json.loads(checkpoint_path.read_text())
            for field in ['goal', 'completion_check', 'verification_files', 'permission_constraints', 'approved_permissions']:
                checkpoint_path.write_text(json.dumps(dict(original, **{field: 'changed'})))
                self.assertNotEqual(auditor(good)['status'], 'verified', field)
            checkpoint_path.write_text(json.dumps(original))
            (root / 'AGENTS.md').write_text('replacement')
            self.assertNotEqual(auditor(good)['status'], 'verified')

    def test_independent_gate_cannot_replace_the_worker_check(self):
        case = {'category': 'covered-task', 'expect_activation': False,
                'files': {'app.py': 'def add(a,b): return a-b\n',
                          'check.py': 'from app import add\nassert add(2,3)==5\n'},
                'prompt': 'local synthetic test', 'completion_check': 'python3 check.py',
                'gate_check': ['python3', '-B', 'check.py']}
        original_run = subprocess.run
        for worker_command, edit_recorded in [(None, True), (['python3', '-B', 'check.py'], True),
                (['python3', '-m', 'unittest', '-q'], True), (['python3', '-B', 'check.py'], False)]:
            def fake_codex(command, **kwargs):
                if command[0] != 'codex':
                    return original_run(command, **kwargs)
                root = Path(command[command.index('-C') + 1])
                (root / 'app.py').write_text('def add(a,b): return a+b\n')
                events = [{'type': 'item.completed', 'item': {'id': 'edit', 'type': 'file_change',
                    'status': 'completed', 'changes': [{'path': 'app.py', 'kind': 'update'}]}}]
                if not edit_recorded:
                    events = []
                if worker_command:
                    result = original_run(worker_command, cwd=root, capture_output=True)
                    events.append({'type': 'item.completed', 'item': {'id': 'check', 'type': 'command_execution',
                        'command': ' '.join(worker_command), 'exit_code': result.returncode}})
                events.append({'type': 'turn.completed'})
                return subprocess.CompletedProcess(command, 0, '\n'.join(map(json.dumps, events)), '')
            with mock.patch.object(AB.activation.subprocess, 'run', side_effect=fake_codex):
                row = AB.activation.run_case('local-control', case, 'candidate', None, 'unused', 'high', 10, 1,
                    audit_factory=lambda root: AB.trace_auditor(root, fast=False))
            self.assertEqual(AB.exact_control_run(row), edit_recorded and worker_command == ['python3', '-B', 'check.py'])
        row['telemetry']['completion_check_invocations_by_kind']['direct'] = 0
        self.assertFalse(AB.exact_control_run(row))

    def test_independent_oracle_rejects_unchanged_or_wrong_product(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / 'app.py'
            for source, expected in [
                ('def add(a, b): return a + b\n', False),
                ('def sum_values(a, b): return a - b\n', False),
                ('def sum_values(a, b): return a + b\n', True),
            ]:
                path.write_text(source)
                command = [AB.RENAME_ORACLE[0], '-B', *AB.RENAME_ORACLE[1:]]
                result = subprocess.run(command, cwd=raw, capture_output=True, timeout=10)
                self.assertEqual(result.returncode == 0, expected)

    def test_fast_case_checks_actual_product_and_checkpoint_with_the_new_audit(self):
        case = copy.deepcopy(AB.activation.CASES[AB.FAST])
        case['gate_check'] = AB.RENAME_ORACLE
        original_run = subprocess.run

        def fake_codex(command, **kwargs):
            if command[0] != 'codex':
                return original_run(command, **kwargs)
            root = Path(command[command.index('-C') + 1])
            validate = ['python3', f'{AB.SKILL}/scripts/validate_checkpoint.py', AB.CHECKPOINT]
            validated = original_run(validate, cwd=root, capture_output=True)
            for name in ('app.py', 'test_app.py'):
                path = root / name
                path.write_text(path.read_text().replace('add', 'sum_values'))
            check = ['python3', '-B', f'{AB.SKILL}/scripts/run_checkpoint_check.py', AB.CHECKPOINT, '--root', '.']
            completed = original_run(check, cwd=root, capture_output=True)
            events = [
                {'type': 'item.completed', 'item': {'id': 'read', 'type': 'command_execution', 'exit_code': 0,
                    'command': f'cat {AB.SKILL}/SKILL.md {AB.CHECKPOINT} app.py test_app.py'}},
                {'type': 'item.completed', 'item': {'id': 'validate', 'type': 'command_execution',
                    'command': ' '.join(validate), 'exit_code': validated.returncode}},
                {'type': 'item.completed', 'item': {'id': 'edit', 'type': 'file_change', 'status': 'completed',
                    'changes': [{'path': name, 'kind': 'update'} for name in ('app.py', 'test_app.py')]}},
                {'type': 'item.completed', 'item': {'id': 'check', 'type': 'command_execution',
                    'command': ' '.join(check), 'exit_code': completed.returncode}},
                {'type': 'turn.completed'},
            ]
            return subprocess.CompletedProcess(command, 0, '\n'.join(map(json.dumps, events)), '')

        with mock.patch.object(AB.activation.subprocess, 'run', side_effect=fake_codex):
            row = AB.activation.run_case(AB.FAST, case, 'candidate',
                ROOT / 'plugins/nulnul-harness/skills/nulnul-harness', 'unused', 'high', 10, 1,
                audit_factory=AB.trace_auditor)
        self.assertTrue(AB.exact_fast_run(row), row)

    def test_model_execution_requires_explicit_operator_authorization(self):
        result = subprocess.run(['python3', str(ROOT / 'evals/instruction-routing/run_ab.py'),
                                 '--champion', '/tmp/no-champion', '--candidate', '/tmp/no-candidate',
                                 '--out', '/tmp/unused-ab-result.json'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Explicit user authorization', result.stderr)

    def test_prior_invalid_calls_exhaust_allowance_before_login_or_execution(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            plugin = root / 'plugin'
            plugin.mkdir()
            (plugin / 'manifest').write_text('frozen')
            (root / 'prior.json').write_text('{}')
            documents = {
                'candidate-v2.json': {'champion_plugin_sha256': AB.tree_digest(plugin),
                    'candidate_plugin_sha256': AB.tree_digest(plugin), 'evaluation_sha256': {}},
                'preregistration-v2.json': {'episode_id': 'local-negative',
                    'prior_attempts': {'count': 6, 'evidence': str(root / 'prior.json'), 'sha256': AB.sha(root / 'prior.json')},
                    'budget': {'model': 'unused', 'reasoning_effort': 'high', 'max_external_model_invocations': 17}},
                'authorization.json': {'max_external_model_invocations': 12},
            }
            for name, payload in documents.items():
                (root / name).write_text(json.dumps(payload))
            argv = ['run_ab.py', '--champion', str(plugin), '--candidate', str(plugin),
                    '--out', str(root / 'result.json'), '--authorized-model-calls']
            with mock.patch.object(AB, 'HERE', root), mock.patch.object(sys, 'argv', argv), \
                    mock.patch.object(AB.shutil, 'copyfile') as credentials, \
                    mock.patch.object(AB.activation, 'run_case') as execute, \
                    mock.patch.object(sys, 'stderr'):
                with self.assertRaises(SystemExit) as stopped:
                    AB.main()
                self.assertEqual(stopped.exception.code, 2)
                credentials.assert_not_called()
                execute.assert_not_called()
                self.assertFalse((root / 'result.json').exists())


if __name__ == '__main__':
    unittest.main()
