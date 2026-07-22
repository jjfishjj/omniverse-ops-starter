"""Validate the layered USD stage with scenario variants and AMR content."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = ROOT / "data" / "ops_scenarios.json"
DEFAULT_AMR_ROUTES = ROOT / "data" / "amr_routes.json"

REQUIRED_PRIMS = [
    "/World",
    "/World/Ground",
    "/World/Equipment",
    "/World/Sensors",
    "/World/SafetyZones",
    "/World/FlowMarkers",
    "/World/Robots",
    "/World/Robots/AMR_01",
    "/World/AMRRoute",
    "/World/IsaacScenario",
    "/World/ScenarioState",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_with_openusd(
    stage_path: Path,
    scenarios: dict[str, Any],
    amr_routes: dict[str, Any],
) -> tuple[bool, list[str]] | None:
    try:
        from pxr import Usd
    except ImportError:
        return None

    stage = Usd.Stage.Open(str(stage_path))
    if not stage:
        return False, [f"Cannot open stage: {stage_path}"]

    missing = [path for path in REQUIRED_PRIMS if not stage.GetPrimAtPath(path).IsValid()]
    world = stage.GetPrimAtPath("/World")
    variant_set = world.GetVariantSet("opsScenario")
    variant_names = set(variant_set.GetVariantNames())
    expected_variants = {variant["id"] for variant in scenarios["variants"]}
    missing.extend(f"variant: {name}" for name in sorted(expected_variants - variant_names))

    for robot in amr_routes["robots"]:
        if not stage.GetPrimAtPath(robot["usd_path"]).IsValid():
            missing.append(robot["usd_path"])
    for waypoint in amr_routes["waypoints"]:
        if not stage.GetPrimAtPath(f"/World/AMRRoute/{waypoint['id']}").IsValid():
            missing.append(f"/World/AMRRoute/{waypoint['id']}")

    return not missing, missing


def validate_with_text(
    stage_path: Path,
    scenarios: dict[str, Any],
    amr_routes: dict[str, Any],
) -> tuple[bool, list[str]]:
    text = stage_path.read_text(encoding="utf-8")
    missing = []
    markers = [
        "subLayers = [",
        'variantSet "opsScenario"',
        "@factory_base.usda@",
        "@equipment.usda@",
        "@sensors.usda@",
        "@safety_zones.usda@",
        "@flow_markers.usda@",
        "@amr_scenario.usda@",
    ]
    for marker in markers:
        if marker not in text:
            missing.append(f"text marker: {marker}")

    for variant in scenarios["variants"]:
        if f'"{variant["id"]}" {{' not in text:
            missing.append(f"variant: {variant['id']}")

    amr_text = stage_path.with_name("amr_scenario.usda").read_text(encoding="utf-8")
    names = set(re.findall(r'def\s+\w+\s+"([^"]+)"', amr_text))
    for robot in amr_routes["robots"]:
        if robot["id"] not in names:
            missing.append(robot["usd_path"])
    for waypoint in amr_routes["waypoints"]:
        if waypoint["id"] not in names:
            missing.append(f"/World/AMRRoute/{waypoint['id']}")

    return not missing, missing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a layered Omniverse/OpenUSD stage.")
    parser.add_argument("stage", type=Path, help="Path to factory_composed.usda.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS, help="Scenario variants JSON.")
    parser.add_argument("--amr-routes", type=Path, default=DEFAULT_AMR_ROUTES, help="AMR route JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.stage.exists():
        raise SystemExit(f"File not found: {args.stage}")

    scenarios = load_json(args.scenarios)
    amr_routes = load_json(args.amr_routes)
    result = validate_with_openusd(args.stage, scenarios, amr_routes)
    mode = "OpenUSD Python API"
    if result is None:
        result = validate_with_text(args.stage, scenarios, amr_routes)
        mode = "USDA text validator"

    ok, missing = result
    if not ok:
        print(f"Layered validation failed with {mode}. Missing required content:")
        for item in missing:
            print(f"- {item}")
        raise SystemExit(1)

    print(f"Layered validation passed with {mode}: {args.stage}")
    print(f"Checked {len(scenarios['variants'])} variants and {len(amr_routes['waypoints'])} AMR waypoints.")


if __name__ == "__main__":
    main()
