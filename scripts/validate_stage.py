"""Validate the demo USD scene expected by this project."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LAYOUT = ROOT / "data" / "factory_layout.json"


GROUPS = {
    "equipment": "/World/Equipment",
    "sensors": "/World/Sensors",
    "safety_zones": "/World/SafetyZones",
    "flow_markers": "/World/FlowMarkers",
}


BASE_REQUIRED_PRIMS = [
    "/World",
    "/World/Ground",
    "/World/Lighting",
    "/World/Lighting/KeyLight",
    "/World/Lighting/FillLight",
    "/World/Cameras",
    "/World/Cameras/Overview",
]


def load_layout(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_required_prims(layout: dict[str, Any]) -> list[str]:
    required = list(BASE_REQUIRED_PRIMS)
    for section, group_path in GROUPS.items():
        required.append(group_path)
        required.extend(f"{group_path}/{item['id']}" for item in layout[section])
    return required


def validate_with_openusd(stage_path: Path, required_prims: list[str]) -> tuple[bool, list[str]] | None:
    try:
        from pxr import Usd
    except ImportError:
        return None

    stage = Usd.Stage.Open(str(stage_path))
    if not stage:
        return False, [f"Cannot open stage: {stage_path}"]

    missing = [path for path in required_prims if not stage.GetPrimAtPath(path).IsValid()]
    return not missing, missing


def validate_with_text(stage_path: Path, required_prims: list[str]) -> tuple[bool, list[str]]:
    text = stage_path.read_text(encoding="utf-8")
    names = set(re.findall(r'def\s+\w+\s+"([^"]+)"', text))
    missing = [path for path in required_prims if path.rsplit("/", 1)[-1] not in names]

    for required_text in [
        'defaultPrim = "World"',
        'customLayerData = {',
        'string project = "omniverse-ops-starter"',
        "ops:id",
        "ops:section",
    ]:
        if required_text not in text:
            missing.append(f"text marker: {required_text}")

    return not missing, missing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the demo Omniverse/OpenUSD stage.")
    parser.add_argument("stage", type=Path, help="Path to a USD/USDA stage.")
    parser.add_argument(
        "--layout",
        type=Path,
        default=DEFAULT_LAYOUT,
        help="Factory layout JSON manifest used to build expected prims.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.stage.exists():
        raise SystemExit(f"File not found: {args.stage}")

    layout = load_layout(args.layout)
    required_prims = build_required_prims(layout)
    result = validate_with_openusd(args.stage, required_prims)
    mode = "OpenUSD Python API"
    if result is None:
        result = validate_with_text(args.stage, required_prims)
        mode = "USDA text validator"

    ok, missing = result
    if not ok:
        print(f"Validation failed with {mode}. Missing required content:")
        for item in missing:
            print(f"- {item}")
        raise SystemExit(1)

    print(f"Validation passed with {mode}: {args.stage}")
    print(f"Checked {len(required_prims)} prims from {args.layout}.")


if __name__ == "__main__":
    main()
