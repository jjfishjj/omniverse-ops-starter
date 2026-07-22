"""Create a layered OpenUSD stage with scenario variants and an AMR route."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from create_demo_stage import DEFAULT_LAYOUT, _as_tuple, _custom_data_for, load_layout
except ImportError:
    from scripts.create_demo_stage import DEFAULT_LAYOUT, _as_tuple, _custom_data_for, load_layout


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = ROOT / "data" / "ops_scenarios.json"
DEFAULT_AMR_ROUTES = ROOT / "data" / "amr_routes.json"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "layers"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def vec(values: list[int | float] | tuple[int | float, ...]) -> str:
    return f"({', '.join(str(value) for value in values)})"


def string(value: str) -> str:
    return json.dumps(value)


def custom_data(data: dict[str, Any], indent: str) -> str:
    if not data:
        return ""
    lines = [f"{indent}customData = {{"]
    lines.extend(custom_data_entries(data, indent + "    "))
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def custom_data_entries(data: dict[str, Any], indent: str) -> list[str]:
    lines: list[str] = []
    nested: dict[str, dict[str, Any]] = {}
    for key, value in sorted(data.items()):
        if ":" in key:
            head, tail = key.split(":", 1)
            nested.setdefault(head, {})[tail] = value
            continue
        lines.append(f"{indent}{usd_type(value)} {key} = {usd_value(value)}")

    for key, value in sorted(nested.items()):
        lines.append(f"{indent}dictionary {key} = {{")
        lines.extend(custom_data_entries(value, indent + "    "))
        lines.append(f"{indent}}}")
    return lines


def usd_type(value: Any) -> str:
    if isinstance(value, str):
        return "string"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    return "double"


def usd_value(value: Any) -> str:
    if isinstance(value, str):
        return string(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def scene_item_usda(section: str, item: dict[str, Any], indent: str = "        ") -> str:
    item_id = item["id"]
    prim_type = "Sphere" if item.get("kind") == "sphere" or section == "flow_markers" else "Cube"
    translation = vec(_as_tuple(item["translation"], 3, f"{item_id}.translation"))
    scale = vec(_as_tuple(item["scale"], 3, f"{item_id}.scale"))
    color = vec(_as_tuple(item["color"], 3, f"{item_id}.color"))
    data = custom_data(_custom_data_for(section, item), indent + "    ")
    radius_line = f"\n{indent}    double radius = 1" if prim_type == "Sphere" else ""
    opacity_line = (
        f"\n{indent}    float[] primvars:displayOpacity = [{float(item['opacity'])}]"
        if "opacity" in item
        else ""
    )
    return f"""{indent}def {prim_type} "{item_id}" (
{data}
{indent})
{indent}{{{radius_line}
{indent}    color3f[] primvars:displayColor = [{color}]{opacity_line}
{indent}    double3 xformOp:translate = {translation}
{indent}    float3 xformOp:scale = {scale}
{indent}    uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
{indent}}}"""


def write_base_layer(layout: dict[str, Any], output: Path) -> None:
    output.write_text(
        f"""#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = {layout.get("units", {}).get("meters_per_unit", 1)}
    upAxis = "{layout.get("units", {}).get("up_axis", "Z")}"
    customLayerData = {{
        string project = "{layout["project"]}"
        string title = "{layout["title"]}"
        string description = "{layout["description"]}"
    }}
)

def Xform "World"
{{
    def Cube "Ground" (
        customData = {{
            dictionary ops = {{
                string id = "Factory_Floor"
                string section = "base"
            }}
        }}
    )
    {{
        color3f[] primvars:displayColor = [(0.22, 0.23, 0.24)]
        double3 xformOp:translate = (0, 0, -0.035)
        float3 xformOp:scale = (5.2, 2.2, 0.035)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
    }}

    def Xform "Lighting"
    {{
        def DistantLight "KeyLight"
        {{
            float inputs:angle = 0.65
            float inputs:intensity = 650
            float3 xformOp:rotateXYZ = (-45, 0, 35)
            uniform token[] xformOpOrder = ["xformOp:rotateXYZ"]
        }}

        def SphereLight "FillLight"
        {{
            float inputs:intensity = 180
            float inputs:radius = 3
            double3 xformOp:translate = (-2, -2, 4)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }}
    }}

    def Xform "Cameras"
    {{
        def Camera "Overview"
        {{
            float focalLength = 28
            double3 xformOp:translate = (4.2, -4.2, 3.1)
            float3 xformOp:rotateXYZ = (60, 0, 42)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ"]
        }}
    }}
}}
""",
        encoding="utf-8",
    )


def write_collection_layer(
    output: Path,
    section: str,
    group_name: str,
    items: list[dict[str, Any]],
) -> None:
    item_blocks = "\n\n".join(scene_item_usda(section, item) for item in items)
    output.write_text(
        f"""#usda 1.0

over "World"
{{
    def Xform "{group_name}"
    {{
{item_blocks}
    }}
}}
""",
        encoding="utf-8",
    )


def write_amr_layer(amr_routes: dict[str, Any], output: Path) -> None:
    robot_blocks = []
    for robot in amr_routes["robots"]:
        route = ", ".join(string(item) for item in robot["route"])
        data = custom_data(
            {
                "ops:id": robot["id"],
                "ops:section": "robots",
                "ops:role": robot["role"],
                "ops:payload_kg": robot["payload_kg"],
                "ops:max_speed_mps": robot["max_speed_mps"],
                "isaac:robot_type": robot["isaac"]["robot_type"],
                "isaac:controller": robot["isaac"]["controller"],
            },
            "            ",
        )
        robot_blocks.append(
            f"""        def Capsule "{robot["id"]}" (
{data}
        )
        {{
            double radius = 0.34
            double height = 0.42
            color3f[] primvars:displayColor = [{vec(robot["color"])}]
            string[] ops:route = [{route}]
            double3 xformOp:translate = {vec(robot["base_pose"])}
            float3 xformOp:scale = {vec(robot["scale"])}
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }}"""
        )

    waypoint_blocks = []
    for waypoint in amr_routes["waypoints"]:
        data = custom_data(
            {
                "ops:id": waypoint["id"],
                "ops:section": "amr_waypoints",
                "ops:task": waypoint["task"],
                "ops:wait_seconds": waypoint["wait_seconds"],
            },
            "            ",
        )
        waypoint_blocks.append(
            f"""        def Sphere "{waypoint["id"]}" (
{data}
        )
        {{
            double radius = 1
            color3f[] primvars:displayColor = [(0.18, 0.2, 0.24)]
            double3 xformOp:translate = {vec(waypoint["translation"])}
            float3 xformOp:scale = (0.11, 0.11, 0.11)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }}"""
        )

    safety = amr_routes["safety"]
    output.write_text(
        f"""#usda 1.0

over "World"
{{
    def Xform "Robots"
    {{
{chr(10).join(robot_blocks)}
    }}

    def Xform "AMRRoute"
    {{
{chr(10).join(waypoint_blocks)}
    }}

    def Xform "IsaacScenario" (
        customData = {{
            dictionary isaac = {{
                string scenario = "amr_material_run"
                string preferred_lane = "{safety["preferred_lane"]}"
                double min_clearance_m = {safety["min_clearance_m"]}
                string avoid_zones = "{", ".join(safety["avoid_zones"])}"
            }}
        }}
    )
    {{
    }}
}}
""",
        encoding="utf-8",
    )


def scenario_variant_block(scenario: dict[str, Any], indent: str = "        ") -> str:
    equipment_children = []
    for equipment_id, status in scenario["equipment_status"].items():
        equipment_children.append(
            f"""{indent}        over "{equipment_id}" (
{indent}            customData = {{
{indent}                dictionary ops = {{
{indent}                    string scenario_status = "{status}"
{indent}                }}
{indent}            }}
{indent}        )
{indent}        {{
{indent}        }}"""
        )

    sensor_children = []
    for sensor_id, offset in scenario["sensor_offsets"].items():
        sensor_children.append(
            f"""{indent}        over "{sensor_id}" (
{indent}            customData = {{
{indent}                dictionary ops = {{
{indent}                    double scenario_offset = {offset}
{indent}                }}
{indent}            }}
{indent}        )
{indent}        {{
{indent}        }}"""
        )

    equipment_overrides = f"""{indent}    over "Equipment"
{indent}    {{
{chr(10).join(equipment_children)}
{indent}    }}"""
    sensor_overrides = f"""{indent}    over "Sensors"
{indent}    {{
{chr(10).join(sensor_children)}
{indent}    }}"""

    return f"""{indent}"{scenario["id"]}" {{
{indent}    def Xform "ScenarioState" (
{indent}        customData = {{
{indent}            dictionary ops = {{
{indent}                string scenario_id = "{scenario["id"]}"
{indent}                string label = "{scenario["label"]}"
{indent}                string description = "{scenario["description"]}"
{indent}                double throughput_multiplier = {scenario["throughput_multiplier"]}
{indent}                double oee_delta = {scenario["oee_delta"]}
{indent}            }}
{indent}        }}
{indent}    )
{indent}    {{
{indent}    }}
{equipment_overrides}
{sensor_overrides}
{indent}}}"""


def write_composed_stage(scenarios: dict[str, Any], layer_names: list[str], output: Path) -> None:
    sublayers = ",\n        ".join(f"@{name}@" for name in layer_names)
    variants = "\n".join(scenario_variant_block(variant) for variant in scenarios["variants"])
    output.write_text(
        f"""#usda 1.0
(
    defaultPrim = "World"
    subLayers = [
        {sublayers}
    ]
)

over "World" (
    variants = {{
        string opsScenario = "{scenarios["default"]}"
    }}
    prepend variantSets = "opsScenario"
)
{{
    variantSet "opsScenario" = {{
{variants}
    }}
}}
""",
        encoding="utf-8",
    )


def create_layered_stage(
    layout: dict[str, Any],
    scenarios: dict[str, Any],
    amr_routes: dict[str, Any],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_base_layer(layout, output_dir / "factory_base.usda")
    write_collection_layer(output_dir / "equipment.usda", "equipment", "Equipment", layout["equipment"])
    write_collection_layer(output_dir / "sensors.usda", "sensors", "Sensors", layout["sensors"])
    write_collection_layer(output_dir / "safety_zones.usda", "safety_zones", "SafetyZones", layout["safety_zones"])
    write_collection_layer(output_dir / "flow_markers.usda", "flow_markers", "FlowMarkers", layout["flow_markers"])
    write_amr_layer(amr_routes, output_dir / "amr_scenario.usda")
    write_composed_stage(
        scenarios,
        [
            "factory_base.usda",
            "equipment.usda",
            "sensors.usda",
            "safety_zones.usda",
            "flow_markers.usda",
            "amr_scenario.usda",
        ],
        output_dir / "factory_composed.usda",
    )
    return output_dir / "factory_composed.usda"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create layered USD files with scenario variants.")
    parser.add_argument("--layout", type=Path, default=DEFAULT_LAYOUT, help="Factory layout JSON.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS, help="Scenario variants JSON.")
    parser.add_argument("--amr-routes", type=Path, default=DEFAULT_AMR_ROUTES, help="AMR route JSON.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output layer folder.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    composed_stage = create_layered_stage(
        load_layout(args.layout),
        load_json(args.scenarios),
        load_json(args.amr_routes),
        args.output_dir,
    )
    print(f"Created layered stage: {composed_stage}")


if __name__ == "__main__":
    main()
