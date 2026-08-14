import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
SCRIPT = SKILL / "scripts/compact_evolution_state.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("compact_evolution_state", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EvolutionCompactionTests(unittest.TestCase):
    def test_real_state_compacts_without_losing_history(self):
        source = ROOT / "docs/nulnul/evolution.json"
        original = MODULE.read_full(source)
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "evolution.json"
            state.write_text(json.dumps(original, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = MODULE.compact(state)
            active = json.loads(state.read_text(encoding="utf-8"))
            archive = MODULE.load_archive(state, active)
            rebuilt = MODULE.reconstruct(active, archive)

            self.assertLess(result["active_bytes_after"], result["active_bytes_before"] // 4)
            for name in MODULE.COLLECTIONS:
                self.assertEqual(
                    {row["id"]: row for row in rebuilt[name]},
                    {row["id"]: row for row in original[name]},
                )
            self.assertEqual(
                {key: value for key, value in rebuilt.items() if key not in MODULE.COLLECTIONS},
                {key: value for key, value in original.items() if key not in MODULE.COLLECTIONS},
            )
            self.assertEqual(MODULE.check(state)["valid"], True)

            once = state.read_bytes(), state.with_name("evolution.archive.json").read_bytes()
            MODULE.compact(state)
            self.assertEqual(
                once,
                (state.read_bytes(), state.with_name("evolution.archive.json").read_bytes()),
            )

            archive_path = state.with_name("evolution.archive.json")
            broken = copy.deepcopy(archive)
            broken["records"]["feedback"][0]["observed"] = "tampered"
            archive_path.write_text(MODULE.encoded(broken), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest does not match"):
                MODULE.check(state)

            archive_path.write_text(MODULE.encoded(archive), encoding="utf-8")
            active["archive"]["counts"]["feedback"] += 1
            state.write_text(MODULE.encoded(active), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "counts do not match"):
                MODULE.check(state)

    def test_legacy_state_without_episodes_remains_supported(self):
        template = json.loads(
            (SKILL / "assets/evolution-state.template.json").read_text(encoding="utf-8")
        )
        template["schema_version"] = 2
        template.pop("autonomous_episodes")
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "evolution.json"
            state.write_text(MODULE.encoded(template), encoding="utf-8")
            self.assertEqual(MODULE.compact(state)["status"], "unchanged")


if __name__ == "__main__":
    unittest.main()
