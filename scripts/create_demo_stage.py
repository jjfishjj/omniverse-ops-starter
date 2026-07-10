"""Create a small OpenUSD scene for Omniverse learning workflows."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SceneObject:
    path: str
    kind: str
    translation: tuple[float, float, float]
    scale: tuple[float, float, float]
    color: tuple[float, float, float]


EQUIPMENT = [
    SceneObject(
        "/World/Equipment/Conveyor_A",
        "cube",
        (-2.5, 0.0, 0.45),
        (1.8, 0.35, 0.35),
        (0.10, 0.35, 0.85),
    ),
    SceneObject(
        "/World/Equipment/Robot_Cell_B",
        "cube",
        (2.0, 0.4, 0.7),
        (0.8, 0.8, 0.7),
        (0.85, 0.35, 0.10),
    ),
]

SENSORS = [
    SceneObject(
        "/World/Sensors/Temperature_01",
        "sphere",
        (-3.0, -0.8, 1.25),
        (0.15, 0.15, 0.15),
        (0.95, 0.15, 0.20),
    ),
    SceneObject(
        "/World/Sensors/Pressure_01",
        "sphere",
        (0.0, 1.1, 1.15),
        (0.15, 0.15, 0.15),
        (0.15, 0.80, 0.35),
    ),
    SceneObject(
        "/World/Sensors/Vibration_01",
        "sphere",
        (2.5, -0.8, 1.4),
        (0.15, 0.15, 0.15),
        (0.95, 0.78, 0.12),
    ),
]


def create_with_openusd(output: Path) -> bool:
    """Create the stage with the pxr OpenUSD API when available."""

    try:
        from pxr import Gf, Usd, UsdGeom, UsdLux
    except ImportError:
        return False

    stage = Usd.Stage.CreateNew(str(output))
    stage.SetDefaultPrim(UsdGeom.Xform.Define(stage, "/World").GetPrim())
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    stage.GetRootLayer().customLayerData = {
        "project": "omniverse-ops-starter",
        "description": "Demo factory digital twin scene",
    }

    UsdGeom.Xform.Define(stage, "/World/Equipment")
    UsdGeom.Xform.Define(stage, "/World/Sensors")
    UsdGeom.Xform.Define(stage, "/World/Lighting")

    ground = UsdGeom.Cube.Define(stage, "/World/Ground")
    ground.AddTranslateOp().Set(Gf.Vec3d(0, 0, -0.03))
    ground.AddScaleOp().Set(Gf.Vec3f(5.0, 3.0, 0.03))
    ground.GetDisplayColorAttr().Set([Gf.Vec3f(0.22, 0.23, 0.24)])

    for item in EQUIPMENT + SENSORS:
        if item.kind == "sphere":
            prim = UsdGeom.Sphere.Define(stage, item.path)
            prim.CreateRadiusAttr(1.0)
        else:
            prim = UsdGeom.Cube.Define(stage, item.path)

        prim.AddTranslateOp().Set(Gf.Vec3d(*item.translation))
        prim.AddScaleOp().Set(Gf.Vec3f(*item.scale))
        prim.GetDisplayColorAttr().Set([Gf.Vec3f(*item.color)])
        prim.GetPrim().SetCustomDataByKey("ops:asset_role", item.path.split("/")[-1])

    key_light = UsdLux.DistantLight.Define(stage, "/World/Lighting/KeyLight")
    key_light.CreateIntensityAttr(450.0)
    key_light.CreateAngleAttr(0.7)
    key_light.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 0.0, 35.0))

    stage.GetRootLayer().Save()
    return True


def create_with_usda_fallback(output: Path) -> None:
    """Write a readable USDA file when pxr is not installed."""

    output.write_text(
        """#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Z"
    customLayerData = {
        string project = "omniverse-ops-starter"
        string description = "Demo factory digital twin scene"
    }
)

def Xform "World"
{
    def Cube "Ground"
    {
        color3f[] primvars:displayColor = [(0.22, 0.23, 0.24)]
        double3 xformOp:translate = (0, 0, -0.03)
        float3 xformOp:scale = (5, 3, 0.03)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
    }

    def Xform "Equipment"
    {
        def Cube "Conveyor_A"
        {
            customData = { string ops:asset_role = "Conveyor_A" }
            color3f[] primvars:displayColor = [(0.10, 0.35, 0.85)]
            double3 xformOp:translate = (-2.5, 0, 0.45)
            float3 xformOp:scale = (1.8, 0.35, 0.35)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }

        def Cube "Robot_Cell_B"
        {
            customData = { string ops:asset_role = "Robot_Cell_B" }
            color3f[] primvars:displayColor = [(0.85, 0.35, 0.10)]
            double3 xformOp:translate = (2, 0.4, 0.7)
            float3 xformOp:scale = (0.8, 0.8, 0.7)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }
    }

    def Xform "Sensors"
    {
        def Sphere "Temperature_01"
        {
            customData = { string ops:asset_role = "Temperature_01" }
            double radius = 1
            color3f[] primvars:displayColor = [(0.95, 0.15, 0.20)]
            double3 xformOp:translate = (-3, -0.8, 1.25)
            float3 xformOp:scale = (0.15, 0.15, 0.15)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }

        def Sphere "Pressure_01"
        {
            customData = { string ops:asset_role = "Pressure_01" }
            double radius = 1
            color3f[] primvars:displayColor = [(0.15, 0.80, 0.35)]
            double3 xformOp:translate = (0, 1.1, 1.15)
            float3 xformOp:scale = (0.15, 0.15, 0.15)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }

        def Sphere "Vibration_01"
        {
            customData = { string ops:asset_role = "Vibration_01" }
            double radius = 1
            color3f[] primvars:displayColor = [(0.95, 0.78, 0.12)]
            double3 xformOp:translate = (2.5, -0.8, 1.4)
            float3 xformOp:scale = (0.15, 0.15, 0.15)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }
    }

    def Xform "Lighting"
    {
        def DistantLight "KeyLight"
        {
            float inputs:angle = 0.7
            float inputs:intensity = 450
            float3 xformOp:rotateXYZ = (-45, 0, 35)
            uniform token[] xformOpOrder = ["xformOp:rotateXYZ"]
        }
    }
}
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a demo USD stage for Omniverse.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/demo_factory.usda"),
        help="Output USD/USDA file path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    used_openusd = create_with_openusd(args.output)
    if not used_openusd:
        create_with_usda_fallback(args.output)

    mode = "OpenUSD Python API" if used_openusd else "USDA fallback writer"
    print(f"Created {args.output} with {mode}.")


if __name__ == "__main__":
    main()
