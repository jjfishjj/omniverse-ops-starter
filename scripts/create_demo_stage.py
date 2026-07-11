"""Create a compact OpenUSD factory digital twin scene for Omniverse."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LAYOUT = ROOT / "data" / "factory_layout.json"
DEFAULT_OUTPUT = ROOT / "output" / "demo_factory.usda"


GROUPS = {
    "equipment": "/World/Equipment",
    "sensors": "/World/Sensors",
    "safety_zones": "/World/SafetyZones",
    "flow_markers": "/World/FlowMarkers",
}


def load_layout(path: Path) -> dict[str, Any]:
    """Read and lightly validate the scene layout manifest."""

    layout = json.loads(path.read_text(encoding="utf-8"))
    required_sections = ["equipment", "sensors", "safety_zones", "flow_markers"]
    missing = [section for section in required_sections if section not in layout]
    if missing:
        raise ValueError(f"Layout is missing required section(s): {', '.join(missing)}")
    return layout


def _as_tuple(values: list[int | float], length: int, name: str) -> tuple[float, ...]:
    if len(values) != length:
        raise ValueError(f"{name} must contain {length} numbers.")
    return tuple(float(value) for value in values)


def _iter_scene_items(layout: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    items: list[tuple[str, dict[str, Any]]] = []
    for section in GROUPS:
        for item in layout[section]:
            items.append((section, item))
    return items


def _prim_path(section: str, item_id: str) -> str:
    return f"{GROUPS[section]}/{item_id}"


def _custom_data_for(section: str, item: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {
        "ops:id": item["id"],
        "ops:section": section,
    }
    for key in ["role", "status", "unit", "value", "threshold", "opacity"]:
        if key in item:
            data[f"ops:{key}"] = item[key]
    for key, value in item.get("metrics", {}).items():
        data[f"ops:metric:{key}"] = value
    return data


def create_with_openusd(layout: dict[str, Any], output: Path) -> bool:
    """Create the stage with the pxr OpenUSD API when available."""

    try:
        from pxr import Gf, Usd, UsdGeom, UsdLux
    except ImportError:
        return False

    stage = Usd.Stage.CreateNew(str(output))
    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, float(layout.get("units", {}).get("meters_per_unit", 1)))

    stage.GetRootLayer().customLayerData = {
        "project": layout["project"],
        "title": layout["title"],
        "description": layout["description"],
    }

    for path in [*GROUPS.values(), "/World/Lighting", "/World/Cameras"]:
        UsdGeom.Xform.Define(stage, path)

    ground = UsdGeom.Cube.Define(stage, "/World/Ground")
    ground.AddTranslateOp().Set(Gf.Vec3d(0, 0, -0.035))
    ground.AddScaleOp().Set(Gf.Vec3f(5.2, 2.2, 0.035))
    ground.GetDisplayColorAttr().Set([Gf.Vec3f(0.22, 0.23, 0.24)])
    ground.GetPrim().SetCustomDataByKey("ops:id", "Factory_Floor")

    for section, item in _iter_scene_items(layout):
        kind = item.get("kind", "cube")
        path = _prim_path(section, item["id"])
        if kind == "sphere" or section == "flow_markers":
            prim = UsdGeom.Sphere.Define(stage, path)
            prim.CreateRadiusAttr(1.0)
        else:
            prim = UsdGeom.Cube.Define(stage, path)

        translation = _as_tuple(item["translation"], 3, f"{item['id']}.translation")
        scale = _as_tuple(item["scale"], 3, f"{item['id']}.scale")
        color = _as_tuple(item["color"], 3, f"{item['id']}.color")
        prim.AddTranslateOp().Set(Gf.Vec3d(*translation))
        prim.AddScaleOp().Set(Gf.Vec3f(*scale))
        prim.GetDisplayColorAttr().Set([Gf.Vec3f(*color)])
        if "opacity" in item:
            prim.GetDisplayOpacityAttr().Set([float(item["opacity"])])
        for key, value in _custom_data_for(section, item).items():
            prim.GetPrim().SetCustomDataByKey(key, value)

    key_light = UsdLux.DistantLight.Define(stage, "/World/Lighting/KeyLight")
    key_light.CreateIntensityAttr(650.0)
    key_light.CreateAngleAttr(0.65)
    key_light.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 0.0, 35.0))

    fill_light = UsdLux.SphereLight.Define(stage, "/World/Lighting/FillLight")
    fill_light.CreateIntensityAttr(180.0)
    fill_light.CreateRadiusAttr(3.0)
    fill_light.AddTranslateOp().Set(Gf.Vec3d(-2.0, -2.0, 4.0))

    camera = UsdGeom.Camera.Define(stage, "/World/Cameras/Overview")
    camera.AddTranslateOp().Set(Gf.Vec3d(4.2, -4.2, 3.1))
    camera.AddRotateXYZOp().Set(Gf.Vec3f(60.0, 0.0, 42.0))
    camera.CreateFocalLengthAttr(28.0)

    stage.GetRootLayer().Save()
    return True


def _format_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _custom_data_block(data: dict[str, Any], indent: str) -> str:
    if not data:
        return ""
    lines = [f"{indent}customData = {{"]
    for key, value in sorted(data.items()):
        usd_type = "string" if isinstance(value, str) else "double"
        lines.append(f"{indent}    {usd_type} {key} = {_format_value(value)}")
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def _scene_item_usda(section: str, item: dict[str, Any], indent: str = "        ") -> str:
    item_id = item["id"]
    prim_type = "Sphere" if item.get("kind") == "sphere" or section == "flow_markers" else "Cube"
    translation = tuple(_as_tuple(item["translation"], 3, f"{item_id}.translation"))
    scale = tuple(_as_tuple(item["scale"], 3, f"{item_id}.scale"))
    color = tuple(_as_tuple(item["color"], 3, f"{item_id}.color"))
    custom_data = _custom_data_block(_custom_data_for(section, item), indent + "    ")
    radius_line = f"\n{indent}    double radius = 1" if prim_type == "Sphere" else ""
    opacity_line = (
        f"\n{indent}    float[] primvars:displayOpacity = [{float(item['opacity'])}]"
        if "opacity" in item
        else ""
    )

    return f"""{indent}def {prim_type} "{item_id}"
{indent}{{
{custom_data}{radius_line}
{indent}    color3f[] primvars:displayColor = [{color}]{opacity_line}
{indent}    double3 xformOp:translate = {translation}
{indent}    float3 xformOp:scale = {scale}
{indent}    uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
{indent}}}"""


def create_with_usda_fallback(layout: dict[str, Any], output: Path) -> None:
    """Write a readable USDA file when pxr is not installed."""

    sections = []
    for section, group_path in GROUPS.items():
        group_name = group_path.rsplit("/", 1)[-1]
        item_blocks = "\n\n".join(_scene_item_usda(section, item) for item in layout[section])
        sections.append(
            f"""    def Xform "{group_name}"
    {{
{item_blocks}
    }}"""
        )

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
    def Cube "Ground"
    {{
        customData = {{ string ops:id = "Factory_Floor" }}
        color3f[] primvars:displayColor = [(0.22, 0.23, 0.24)]
        double3 xformOp:translate = (0, 0, -0.035)
        float3 xformOp:scale = (5.2, 2.2, 0.035)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
    }}

{chr(10).join(sections)}

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a demo USD stage for Omniverse.")
    parser.add_argument(
        "--layout",
        type=Path,
        default=DEFAULT_LAYOUT,
        help="Factory layout JSON manifest.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output USD/USDA file path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    layout = load_layout(args.layout)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    used_openusd = create_with_openusd(layout, args.output)
    if not used_openusd:
        create_with_usda_fallback(layout, args.output)

    mode = "OpenUSD Python API" if used_openusd else "USDA fallback writer"
    print(f"Created {args.output} with {mode}.")


if __name__ == "__main__":
    main()
