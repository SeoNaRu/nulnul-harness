#!/usr/bin/env python3
"""Bounded, read-only operational status. Recorded activity is not process liveness."""

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

import capability_pack
import foundation_runtime as runtime
import trace_evidence


PLUGIN = Path(__file__).resolve().parents[3]
COMPONENTS = (".codex-plugin/plugin.json", "skills/nulnul-harness/SKILL.md") + tuple(
    "skills/nulnul-harness/scripts/" + name for name in (
        "foundation_runtime.py", "capability_pack.py", "run_checkpoint_check.py",
        "validate_checkpoint.py", "trace_evidence.py", "harness_status.py",
    )
)
MAX_PLUGIN_ENTRIES = 4096
MAX_PLUGIN_BYTES = 16 * 1024 * 1024


def read_bytes(root, relative, limit=1024 * 1024):
    root = Path(root).resolve()
    path = root / relative
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise ValueError("unsafe evidence path")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError("unsafe evidence file")
        data = source.read(limit + 1)
    if len(data) > limit:
        raise ValueError("evidence exceeds the bounded read limit")
    return data


def read_json(root, relative):
    value = json.loads(read_bytes(root, relative))
    if not isinstance(value, dict):
        raise ValueError("expected one evidence object")
    return value


def shipped_identity(root):
    """Hash the packer's shipped-file scope, with bounded traversal and reads."""
    root = Path(root).absolute()
    if any(path.is_symlink() for path in (root, *root.parents)):
        raise ValueError("unsafe plugin root")
    root = root.resolve()
    pending, files, entries, total = [root], [], 0, 0
    while pending:
        directory = pending.pop()
        if directory.is_symlink() or not directory.resolve().is_relative_to(root):
            raise ValueError("unsafe plugin directory")
        with os.scandir(directory) as children:
            for child in children:
                entries += 1
                if entries > MAX_PLUGIN_ENTRIES:
                    raise ValueError("plugin entry limit exceeded")
                path = Path(child.path)
                if child.name == "__pycache__" or (path.suffix == ".pyc" and not child.is_dir(follow_symlinks=False)):
                    continue
                if child.is_symlink():
                    raise ValueError("unsafe plugin path")
                if child.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif child.is_file(follow_symlinks=False):
                    data = read_bytes(root, path.relative_to(root), min(1024 * 1024, MAX_PLUGIN_BYTES - total))
                    total += len(data)
                    files.append((path.relative_to(root).as_posix(), hashlib.sha256(data).hexdigest()))
                else:
                    raise ValueError("unsafe plugin file")
    digest = hashlib.sha256(json.dumps(sorted(files), ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
    return {"shipped_digest": digest, "shipped_file_count": len(files), "shipped_bytes": total}


def plugin_identity(root, full_tree=False):
    result = {"version": "unknown", "component_digest": None, "shipped_digest": None,
              "shipped_file_count": None, "shipped_bytes": None}
    if root is None:
        return result
    try:
        manifest = read_json(root, COMPONENTS[0])
        if manifest.get("name") != "nulnul-harness":
            return result
        result["version"] = trace_evidence.revision(manifest.get("version"))
    except (OSError, ValueError, UnicodeError, RuntimeError):
        return result
    try:
        digest = hashlib.sha256()
        for name in COMPONENTS:
            digest.update(name.encode() + b"\0" + read_bytes(root, name) + b"\0")
        result["component_digest"] = digest.hexdigest()
    except (OSError, ValueError, UnicodeError, RuntimeError):
        pass
    if full_tree:
        try:
            result.update(shipped_identity(root))
        except (OSError, ValueError, UnicodeError, RuntimeError):
            pass
    return result


def bounded_text(value):
    text = runtime.redact(value) if isinstance(value, str) else ""
    return " ".join(str(text).split())[:180]


def receipt_result(root, session_id, task_id, pack, events):
    """Verify the historical receipt and ordered identities, never today's whole tree."""
    attributed = [e for e in events if e["kind"] == "CAPABILITY_EXPERIENCE_ATTRIBUTED"]
    if not attributed:
        return "unknown"
    event = attributed[-1]
    check_id = event.get("details", {}).get("check_id")
    if not isinstance(check_id, str) or not trace_evidence.DIGEST.fullmatch(check_id):
        return "invalid"
    try:
        check = read_json(root, "docs/nulnul/.runtime/pack-checks/" + check_id + ".json")
        fields = ("session_id", "task_id", "pack_id", "pack_digest", "capability_id",
                  "capability_digest", "project_check_identity", "command_hash", "product_state_id",
                  "exit_code", "result", "output_digest", "completed_event_id", "created_at")
        if capability_pack.canonical_digest({key: check[key] for key in fields}) != check_id:
            return "invalid"
        refs = pack["capability_refs"]
        if len(refs) != 1:
            return "unknown"
        ref = refs[0]
        expected = {"schema_version": 1, "check_id": check_id, "status": "CHECKED",
                    "session_id": session_id, "task_id": task_id, "pack_id": pack["pack_id"],
                    "pack_digest": pack["pack_digest"], "capability_id": ref["capability_id"],
                    "capability_digest": ref["body_digest"],
                    "project_check_identity": ref["project_check_identity"]}
        if any(check.get(key) != value for key, value in expected.items()):
            return "invalid"
        if (not isinstance(check.get("command"), str)
                or check["command"] != ref["project_check_command"]
                or hashlib.sha256(check["command"].encode()).hexdigest() != check["command_hash"]
                or type(check["exit_code"]) is not int
                or check["result"] != ("pass" if check["exit_code"] == 0 else "fail")):
            return "invalid"
        chain = []
        for kind in ("CAPABILITY_SELECTED", "CAPABILITY_PACK_CREATED", "CAPABILITY_BODY_INCLUDED",
                     "WORK_SESSION_STARTED", "CHECK_STARTED", "CHECK_COMPLETED",
                     "CAPABILITY_EXPERIENCE_ATTRIBUTED"):
            matches = [e for e in events if e["kind"] == kind and e.get("details", {}).get("pack_id") == pack["pack_id"]]
            if len(matches) != 1:
                return "invalid"
            chain.append(matches[0])
        if any(a["event_id"] >= b["event_id"] for a, b in zip(chain, chain[1:])):
            return "invalid"
        if (chain[4]["event_id"] != check["started_event_id"]
                or chain[5]["event_id"] != check["completed_event_id"]
                or chain[5]["details"].get("result") != check["result"]
                or chain[5]["details"].get("exit_code") != check["exit_code"]
                or chain[6]["details"].get("check_id") != check_id
                or any(chain[i]["details"].get("capability_id") != ref["capability_id"] for i in (4, 5, 6))):
            return "invalid"
        selected = [ref["capability_id"]]
        if any(chain[i]["details"].get("capability_ids") != selected for i in (0, 1, 2)):
            return "invalid"
        if chain[1]["details"].get("pack_digest") != pack["pack_digest"]:
            return "invalid"
        completed = [e for e in events if e["kind"] == "CHECK_COMPLETED"]
        if not completed or completed[-1]["event_id"] != check["completed_event_id"]:
            return "invalid"
        ended = [e for e in events if e["kind"] in {"TASK_COMPLETED", "TASK_FAILED"}]
        if not ended or ended[-1]["event_id"] <= chain[-1]["event_id"]:
            return "unknown"
        return "historical_pass" if check["result"] == "pass" else "historical_fail"
    except (OSError, ValueError, UnicodeError, KeyError, TypeError):
        return "invalid"


def snapshot(root, session_id=None, host_session_key=None, installed_plugin=None):
    root = Path(root).resolve()
    requested = installed_plugin is not None
    source, installed = plugin_identity(PLUGIN, requested), plugin_identity(installed_plugin, requested)
    try:
        same_path = requested and Path(installed_plugin).resolve() == PLUGIN
    except (OSError, RuntimeError):
        same_path = False
    match = "unknown"
    if source["component_digest"] and installed["component_digest"]:
        match = "same_components" if source["component_digest"] == installed["component_digest"] else "different_components"
        if same_path:
            match = "same_path_not_install_proof"
    installation_status, installation_action = "unknown", "inspect_registered_copy"
    if requested:
        installation_action = "check_copy_evidence"
        if same_path:
            installation_action = "inspect_registered_copy"
        elif source["shipped_digest"] and installed["shipped_digest"]:
            installation_status = "same" if source["shipped_digest"] == installed["shipped_digest"] else "stale"
            installation_action = "verify_fresh_session" if installation_status == "same" else "refresh_registered_copy"
    result = {"schema_version": 1, "source": source, "installed_copy": installed,
              "installation_comparison": match, "installation_status": installation_status,
              "installation_next_action": installation_action, "installation_requested": requested,
              "binding": "unknown", "session_id": None,
              "recorded_status": "unknown", "task": "unknown", "task_id": None,
              "capabilities": [], "selection": "unknown", "selection_reason": "",
              "body_loaded": False, "last_event": None, "reported_revision": "unknown",
              "producer_matches_observer": None, "check_attempts": 0, "repeated_checks": 0,
              "recorded_check": "unknown", "receipt": "unknown", "changes": [], "warnings": [],
              "limits": "Records do not prove process liveness, current-code freshness, token savings or causal benefit."}
    if session_id is not None and not re.fullmatch(r"ses-[A-Za-z0-9-]{1,150}", session_id):
        result["warnings"].append("invalid_session_id")
        return result
    try:
        try:
            session = read_json(root, "docs/nulnul/.runtime/active-session.json")
        except FileNotFoundError:
            session = {}
        if session_id and session.get("session_id") != session_id:
            session = read_json(root, "docs/nulnul/memory/sessions/" + session_id + ".json")
        if not session:
            return result
        if session_id and session.get("session_id") != session_id:
            raise ValueError("session identity mismatch")
        if host_session_key:
            if session.get("trace_host_session_key") != host_session_key:
                result["warnings"].append("host_session_mismatch")
                return result
            result["binding"] = "host_bound"
        elif session_id:
            result["binding"] = "explicit_record_not_current_host"
        else:
            result["warnings"].append("host_session_unknown")
            return result
        identity = session["session_id"]
        if not isinstance(identity, str) or not re.fullmatch(r"ses-[A-Za-z0-9-]{1,150}", identity):
            raise ValueError("invalid stored session identity")
        result["session_id"] = identity
        result["reported_revision"] = trace_evidence.revision(session.get("nulnul_revision"))
        tasks = session.get("tasks", [])
        if not isinstance(tasks, list) or any(not isinstance(task, dict) for task in tasks):
            raise ValueError("invalid session tasks")
        task = tasks[-1] if tasks else {}
        result.update(task=bounded_text(task.get("goal")) or "unknown", task_id=task.get("task_id"),
                      recorded_status=bounded_text(task.get("status")) or "unknown",
                      changes=[bounded_text(x) for x in session.get("important_changes", [])[:5]])
        data = read_bytes(root, "docs/nulnul/.runtime/events/" + identity + ".jsonl")
        rows = [json.loads(line) for line in data.splitlines() if line.strip()]
        if len(rows) > 4096:
            raise ValueError("event limit exceeded")
        previous = 0
        for row in rows:
            if (not isinstance(row, dict) or row.get("session_id") != identity
                    or type(row.get("event_id")) is not int or row["event_id"] <= previous
                    or not isinstance(row.get("details", {}), dict) or not isinstance(row.get("kind"), str)):
                raise ValueError("invalid or conflicting event sequence")
            previous = row["event_id"]
        events = [e for e in rows if e.get("task_id") == task.get("task_id")]
        if not any(e["kind"] == "TASK_STARTED" for e in events):
            raise ValueError("task start evidence is missing")
        result["last_event"] = events[-1]["kind"] if events else None
        projections = [e["trace"] for e in events if isinstance(e.get("trace"), dict)]
        hashes = {p.get("producer_digest") for p in projections}
        if hashes:
            result["producer_matches_observer"] = hashes == {trace_evidence.producer_digest()}
        checks = [e for e in events if e["kind"] == "CHECK_COMPLETED"]
        result["check_attempts"] = len(checks)
        command_hashes = [e["details"].get("command_hash") for e in checks]
        known = [h for h in command_hashes if isinstance(h, str) and trace_evidence.DIGEST.fullmatch(h)]
        result["repeated_checks"] = len(known) - len(set(known))
        if checks:
            exit_code = checks[-1]["details"].get("exit_code")
            if type(exit_code) is int and checks[-1]["details"].get("result") == ("pass" if exit_code == 0 else "fail"):
                result["recorded_check"] = "pass" if exit_code == 0 else "fail"
        created = [e for e in events if e["kind"] == "CAPABILITY_PACK_CREATED"]
        if created:
            pack_id = created[-1]["details"].get("pack_id")
            if not isinstance(pack_id, str) or not capability_pack.PACK_ID.fullmatch(pack_id):
                raise ValueError("invalid pack identity")
            pack = read_json(root, "docs/nulnul/.runtime/capability-packs/" + pack_id + ".json")
            if (pack.get("pack_id") != pack_id or pack.get("task_id") != task.get("task_id")
                    or pack.get("status") != "READY" or pack.get("pack_digest") != created[-1]["details"].get("pack_digest")
                    or pack.get("pack_digest") != capability_pack.canonical_digest({k:v for k,v in pack.items() if k != "pack_digest"})):
                raise ValueError("pack evidence mismatch")
            result["capabilities"] = [bounded_text(ref["capability_id"]) for ref in pack["capability_refs"]]
            result["selection"] = "selected" if result["capabilities"] else "direct"
            result["selection_reason"] = bounded_text(pack.get("selection_evidence"))
            included = [e for e in events if e["kind"] == "CAPABILITY_BODY_INCLUDED" and e["details"].get("pack_id") == pack_id]
            if included:
                result["body_loaded"] = (
                    len(included) == 1 and bool(pack["capability_refs"])
                    and included[0]["event_id"] > created[-1]["event_id"]
                    and included[0]["details"].get("capability_ids") == [ref["capability_id"] for ref in pack["capability_refs"]]
                )
                if not result["body_loaded"]:
                    result["warnings"].append("invalid_body_evidence")
            result["receipt"] = receipt_result(root, identity, task["task_id"], pack, events)
    except (OSError, ValueError, UnicodeError, KeyError, TypeError, IndexError):
        result.update(recorded_check="unknown", receipt="unknown", selection="unknown", body_loaded=False)
        result["warnings"].append("missing_invalid_or_oversized_evidence")
    return result


def render(report, lang="en"):
    labels = ("Source / inspected copy", "Session binding / recorded state", "Task", "Capability / recorded reason", "Check record / historical receipt", "Changes")
    words = {}
    counts = "attempts={0}, known repeats={1}"
    limit = "Recorded evidence only; not process liveness or a fresh check of today's code."
    if lang == "ko":
        labels = ("소스 / 검사한 설치 사본", "세션 연결 / 기록상 상태", "작업", "선택 능력 / 기록된 이유", "검사 기록 / 과거 영수증", "변경")
        words = {"unknown": "미확인", "ACTIVE": "진행 중으로 기록됨", "COMPLETED": "완료로 기록됨",
                 "BLOCKED": "진행 보류로 기록됨", "FAILED": "실패로 기록됨", "host_bound": "현재 호스트 세션과 연결됨",
                 "explicit_record_not_current_host": "지정한 기록(현재 실행 여부 미확인)",
                 "same_components": "비교한 구성요소 일치", "different_components": "구성요소 불일치",
                 "same_path_not_install_proof": "개발 소스 자체(설치 증거 아님)", "selected": "선택됨",
                 "direct": "능력 미선택이 명시됨", "pass": "통과 기록", "fail": "실패 기록",
                 "historical_pass": "검증된 과거 통과 영수증", "historical_fail": "검증된 과거 실패 영수증",
                 "invalid": "영수증 불일치", "host_session_unknown": "호스트 세션 정보 없음",
                 "host_session_mismatch": "다른 호스트의 세션 기록", "invalid_session_id": "유효하지 않은 세션 ID",
                 "invalid_body_evidence": "스킬 본문 로드 근거 불일치",
                 "missing_invalid_or_oversized_evidence": "근거 누락·손상·범위 초과"}
        counts = "검사 {0}회, 식별된 반복 {1}회"
        limit = "기록 기준입니다. 프로세스 생존 여부나 현재 코드 전체의 통과 판정은 아닙니다."
    def word(value):
        return words.get(value, value)
    values = (word(report["source"]["version"]) + " / " + word(report["installed_copy"]["version"]) + " (" + word(report["installation_comparison"]) + ")",
              word(report["binding"]) + " / " + word(report["recorded_status"]), word(report["task"]),
              (", ".join(report["capabilities"]) or word(report["selection"])) + " / " + (report["selection_reason"] or word("unknown")),
              word(report["recorded_check"]) + " / " + word(report["receipt"]) + " (" + counts.format(report["check_attempts"], report["repeated_checks"]) + ")",
              ", ".join(report["changes"]) or word("unknown"))
    lines = [label + ": " + value for label, value in zip(labels, values)]
    if report.get("installation_requested"):
        listing = "codex plugin list --marketplace nulnul-harness --json"
        refresh = "codex plugin add nulnul-harness@nulnul-harness --json"
        states = {"same": "same shipped files", "stale": "stale relative to source (different shipped files)",
                  "unknown": "unknown (full comparison unavailable or not a separate copy)"}
        actions = {
            "inspect_registered_copy": f"Locate the registered cache with `{listing}`, then compare that separate directory using --installed-plugin.",
            "check_copy_evidence": "Check the supplied copy for missing, unsafe or oversized files, then repeat --installed-plugin; do not infer a match from component or version equality.",
            "verify_fresh_session": "Verify skill loading in a fresh host session; matching disk files do not prove what an open thread loaded.",
            "refresh_registered_copy": f"Confirm the intended checkout with `{listing}`; with approval, refresh using `{refresh}`, compare again, then verify loading in a fresh host session.",
        }
        if lang == "ko":
            states = {"same": "전체 배포 파일 일치", "stale": "소스와 불일치(버전 선후 관계는 미확인)",
                      "unknown": "미확인(전체 비교 불가 또는 별도 설치 사본 아님)"}
            actions = {
                "inspect_registered_copy": f"`{listing}`에서 등록된 캐시를 확인하고, 별도 설치 경로를 --installed-plugin으로 비교하세요.",
                "check_copy_evidence": "지정한 사본의 누락·안전하지 않은 경로·크기 초과를 확인한 뒤 --installed-plugin으로 재검사하세요. 구성요소나 버전 일치만으로 전체 일치를 판단하지 마세요.",
                "verify_fresh_session": "새 호스트 세션에서 스킬 본문 로드를 확인하세요. 디스크 일치는 기존 대화가 읽은 본문의 증거가 아닙니다.",
                "refresh_registered_copy": f"`{listing}`에서 의도한 소스인지 확인하고, 승인 후 `{refresh}`로 갱신하세요. 다시 비교한 뒤 새 호스트 세션에서 본문 로드를 확인하세요.",
            }
        lines[1:1] = [("설치 파일: " if lang == "ko" else "Installed files: ") + states[report["installation_status"]],
                      ("다음 작업: " if lang == "ko" else "Next action: ") + actions[report["installation_next_action"]]]
    if report["warnings"]:
        lines.append(("주의: " if lang == "ko" else "Warning: ") + ", ".join(word(w) for w in report["warnings"]))
    return "\n".join(lines + [limit])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--session-id")
    parser.add_argument("--host-session", default=os.environ.get("NULNUL_TRACE_SESSION") or os.environ.get("CODEX_THREAD_ID"))
    parser.add_argument("--installed-plugin", type=Path)
    parser.add_argument("--lang", choices=("en", "ko"), default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = snapshot(args.root, args.session_id, args.host_session, args.installed_plugin)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report, args.lang))


if __name__ == "__main__":
    main()
