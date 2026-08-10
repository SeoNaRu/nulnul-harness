#!/usr/bin/env python3
"""Repack dist/nulnul-harness-<version>.zip so it matches the plugin tree exactly.

The release test compares the archive with the plugin byte for byte, so packing by
hand drifts every time a plugin file changes after the last zip.
"""

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/nulnul-harness"


def main():
    version = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    archive = ROOT / "dist" / f"nulnul-harness-{version}.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        path for path in PLUGIN.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, f"{PLUGIN.name}/{path.relative_to(PLUGIN).as_posix()}")
    print(f"{archive.relative_to(ROOT)}: {len(files)} files")


if __name__ == "__main__":
    main()
