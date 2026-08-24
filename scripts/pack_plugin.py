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


def pack(plugin, archive):
    archive.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        path for path in plugin.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            info = zipfile.ZipInfo(
                f"{plugin.name}/{path.relative_to(plugin).as_posix()}",
                date_time=(1980, 1, 1, 0, 0, 0),
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes(), compresslevel=9)
    return len(files)


def main():
    version = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    archive = ROOT / "dist" / f"nulnul-harness-{version}.zip"
    print(f"{archive.relative_to(ROOT)}: {pack(PLUGIN, archive)} files")


if __name__ == "__main__":
    main()
