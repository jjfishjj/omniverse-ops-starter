"""Contract tests for the generated factory digital twin stage."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.create_demo_stage import DEFAULT_LAYOUT, create_with_usda_fallback, load_layout
from scripts.validate_stage import build_required_prims, validate_with_text


class SceneContractTests(unittest.TestCase):
    def test_layout_builds_expected_required_prims(self) -> None:
        layout = load_layout(DEFAULT_LAYOUT)
        required_prims = build_required_prims(layout)

        self.assertIn("/World/Equipment/Conveyor_A", required_prims)
        self.assertIn("/World/Sensors/Temperature_01", required_prims)
        self.assertIn("/World/SafetyZones/Robot_Cell_Safety", required_prims)
        self.assertIn("/World/FlowMarkers/Outbound", required_prims)
        self.assertEqual(23, len(required_prims))

    def test_usda_fallback_matches_contract(self) -> None:
        layout = load_layout(DEFAULT_LAYOUT)
        required_prims = build_required_prims(layout)

        with tempfile.TemporaryDirectory() as tmpdir:
            stage_path = Path(tmpdir) / "factory.usda"
            create_with_usda_fallback(layout, stage_path)
            ok, missing = validate_with_text(stage_path, required_prims)

        self.assertTrue(ok, missing)


if __name__ == "__main__":
    unittest.main()
