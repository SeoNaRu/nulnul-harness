#!/usr/bin/env python3
"""Report harness documents that are older than the sources they describe.

A fix that lands only in code is invisible to the next session. Comparing last
change times is enough: a false positive costs one warning line, a miss costs
re-deriving knowledge the project already had.

Dirty working-tree documents count as updated for the current change. Otherwise
times come from the last commit that touched each path, so a document updated in
the same commit as its code is not reported. Outside a git repository, or for a
path with no commit yet, the file modification time is used instead.
"""

import argparse
import json
import subprocess
from pathlib import Path

DOCUMENTS = ("AGENTS.md", "CLAUDE.md", "docs/nulnul/project.md", "README.md")
HOST_DOCUMENTS = {"codex": "AGENTS.md", "claude": "CLAUDE.md"}
SHARED_DOCUMENTS = ("docs/nulnul/project.md", "README.md")
SOURCE_GLOBS = ("*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.go", "*.rs", "*.rb", "*.java", "*.sh", "*.sql")


def git(root, *arguments):
    result = subprocess.run(
        ["git", "-C", str(root), *arguments], capture_output=True, text=True
    )
    return result.stdout.rstrip() if result.returncode == 0 else ""


def is_dirty(root, path):
    return bool(git(root, "status", "--porcelain", "--untracked-files=all", "--", path))


def dirty_source(root):
    output = git(root, "status", "--porcelain", "--untracked-files=all", "--", *SOURCE_GLOBS)
    for line in output.splitlines():
        if len(line) >= 4:
            return line[3:].split(" -> ")[-1].strip('"')
    return None


def sources_changed_since(root, commit):
    """Newest source file committed after `commit`, or None when there is none."""
    output = git(root, "log", f"{commit}..HEAD", "--name-only", "--format=", "--", *SOURCE_GLOBS)
    changed = [line for line in output.splitlines() if line.strip()]
    return changed[0] if changed else None


def newest_source_by_mtime(root):
    sources = [
        path for glob in SOURCE_GLOBS for path in root.rglob(glob)
        if path.is_file() and ".git" not in path.parts
    ]
    return max(sources, key=lambda path: path.stat().st_mtime) if sources else None


def check(root, documents=None, host=None):
    root = Path(root).resolve()
    documents = documents or ((HOST_DOCUMENTS[host], *SHARED_DOCUMENTS) if host else DOCUMENTS)
    newest = None
    uncommitted_source = dirty_source(root)
    stale = []
    for name in documents:
        document = root / name
        if not document.is_file():
            continue
        if is_dirty(root, name):
            source = None
        elif uncommitted_source:
            source = uncommitted_source
        else:
            document_commit = git(root, "log", "-1", "--format=%H", "--", name)
            if document_commit:
                source = sources_changed_since(root, document_commit)
            else:
                if newest is None:
                    newest = newest_source_by_mtime(root)
                source = (
                    str(newest.relative_to(root))
                    if newest is not None and newest.stat().st_mtime > document.stat().st_mtime
                    else None
                )
        if source:
            stale.append({"document": name, "newest_source": source})
    return stale


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--document", action="append", dest="documents")
    parser.add_argument("--host", choices=tuple(HOST_DOCUMENTS))
    args = parser.parse_args()
    stale = check(args.root, tuple(args.documents) if args.documents else None, args.host)
    print(json.dumps({"documentation_debt": stale}, ensure_ascii=False, indent=2))
    for entry in stale:
        print(f"stale: {entry['document']} is older than {entry['newest_source']}")
    raise SystemExit(bool(stale))


if __name__ == "__main__":
    main()
