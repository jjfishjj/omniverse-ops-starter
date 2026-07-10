"""Validate the demo USD scene expected by this project."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_PRIMS = [
    "/World",
    "/World/Ground",
    "/World/Equipment",
    "/World/Equipment/Conveyor_A",
    "/World/Equipment/Robot_Cell_B",
    "/World/Sensors",
    "/World/Sensors/Temperature_01",
    "/World/Sensors/Pressure_01",
    "/World/Sensors/Vibration_01",
    "/World/Lighting",
    "/World/Lighting/KeyLight",
]


def validate_with_openusd(stage_path: Path) -> tuple[bool, list[str]] | None:
    try:
        from pxr import Usd
    except ImportError:
        return None

    stage = Usd.Stage.Open(str(stage_path))
    if not stage:
        return False, [f"Cannot open stage: {stage_path}"]

    missing = [path for path in REQUIRED_PRIMS if not stage.GetPrimAtPath(path).IsValid()]
    return not missing, missing


def validate_with_text(stage_path: Path) -> tuple[bool, list[str]]:
    text = stage_path.read_text(encoding="utf-8")
    names = set(re.findall(r'def\s+\w+\s+"([^"]+)"', text))
    missing = [path for path in REQUIRED_PRIMS if path.rsplit("/", 1)[-1] not in names]
    return not missing, missing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the demo Omniverse/OpenUSD stage.")
    parser.add_argument("stage", type=Path, help="Path to a USD/USDA stage.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.stage.exists():
        raise SystemExit(f"File not found: {args.stage}")

    result = validate_with_openusd(args.stage)
    mode = "OpenUSD Python API"
    if result is None:
        result = validate_with_text(args.stage)
        mode = "USDA text validator"

    ok, missing = result
    if not ok:
        print(f"Validation failed with {mode}. Missing prims:")
        for item in missing:
            print(f"- {item}")
        raise SystemExit(1)

    print(f"Validation passed with {mode}: {args.stage}")


if __name__ == "__main__":
    main()
