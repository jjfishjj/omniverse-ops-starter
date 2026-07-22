"""Contract tests for the generated factory digital twin stage."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.create_demo_stage import DEFAULT_LAYOUT, create_with_usda_fallback, load_layout
from scripts.create_layered_stage import (
    DEFAULT_AMR_ROUTES,
    DEFAULT_SCENARIOS,
    create_layered_stage,
    load_json,
)
from scripts.telemetry_server import telemetry_payload
from scripts.validate_layered_stage import validate_with_text as validate_layered_with_text
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

    def test_layered_stage_contains_variants_and_amr_route(self) -> None:
        layout = load_layout(DEFAULT_LAYOUT)
        scenarios = load_json(DEFAULT_SCENARIOS)
        amr_routes = load_json(DEFAULT_AMR_ROUTES)

        with tempfile.TemporaryDirectory() as tmpdir:
            stage_path = create_layered_stage(layout, scenarios, amr_routes, Path(tmpdir))
            ok, missing = validate_layered_with_text(stage_path, scenarios, amr_routes)

        self.assertTrue(ok, missing)

    def test_telemetry_payload_streams_scenario_and_amr_state(self) -> None:
        layout = load_layout(DEFAULT_LAYOUT)
        scenarios = load_json(DEFAULT_SCENARIOS)
        amr_routes = load_json(DEFAULT_AMR_ROUTES)

        payload = telemetry_payload(layout, scenarios, amr_routes, "peak_hour", 7)

        self.assertEqual("telemetry", payload["type"])
        self.assertEqual("peak_hour", payload["scenario"])
        self.assertEqual("AMR_01", payload["amr"]["id"])
        self.assertEqual(3, len(payload["sensors"]))
        self.assertGreater(payload["kpis"]["throughput_per_hour"], 900)


if __name__ == "__main__":
    unittest.main()
