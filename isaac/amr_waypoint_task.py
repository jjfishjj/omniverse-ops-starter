"""Isaac Sim starter script for creating the AMR waypoint scenario.

Run this inside Isaac Sim's Script Editor or as part of a Kit-based Isaac app.
The script intentionally creates proxy geometry first; replace /World/Robots/AMR_01
with a production wheeled robot asset when you wire in a controller.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMR_ROUTES = ROOT / "data" / "amr_routes.json"


def load_routes(path: Path = AMR_ROUTES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def create_amr_waypoint_task(routes: dict | None = None) -> None:
    try:
        import omni.usd
        from pxr import Gf, UsdGeom
    except ImportError as exc:
        raise RuntimeError("Run this script inside Isaac Sim or an Omniverse Kit Python environment.") from exc

    routes = routes or load_routes()
    context = omni.usd.get_context()
    stage = context.get_stage()
    if stage is None:
        context.new_stage()
        stage = context.get_stage()

    UsdGeom.Xform.Define(stage, "/World")
    UsdGeom.Xform.Define(stage, "/World/Robots")
    UsdGeom.Xform.Define(stage, "/World/AMRRoute")
    scenario = UsdGeom.Xform.Define(stage, "/World/IsaacScenario")
    scenario.GetPrim().SetCustomDataByKey("isaac:scenario", "amr_material_run")
    scenario.GetPrim().SetCustomDataByKey("isaac:preferred_lane", routes["safety"]["preferred_lane"])
    scenario.GetPrim().SetCustomDataByKey("isaac:min_clearance_m", routes["safety"]["min_clearance_m"])

    for robot in routes["robots"]:
        proxy = UsdGeom.Cube.Define(stage, robot["usd_path"])
        proxy.AddTranslateOp().Set(Gf.Vec3d(*robot["base_pose"]))
        proxy.AddScaleOp().Set(Gf.Vec3f(*robot["scale"]))
        proxy.GetDisplayColorAttr().Set([Gf.Vec3f(*robot["color"])])
        proxy.GetPrim().SetCustomDataByKey("ops:id", robot["id"])
        proxy.GetPrim().SetCustomDataByKey("ops:section", "robots")
        proxy.GetPrim().SetCustomDataByKey("ops:role", robot["role"])
        proxy.GetPrim().SetCustomDataByKey("ops:payload_kg", robot["payload_kg"])
        proxy.GetPrim().SetCustomDataByKey("ops:max_speed_mps", robot["max_speed_mps"])
        proxy.GetPrim().SetCustomDataByKey("isaac:robot_type", robot["isaac"]["robot_type"])
        proxy.GetPrim().SetCustomDataByKey("isaac:controller", robot["isaac"]["controller"])

    for waypoint in routes["waypoints"]:
        marker = UsdGeom.Sphere.Define(stage, f"/World/AMRRoute/{waypoint['id']}")
        marker.CreateRadiusAttr(1.0)
        marker.AddTranslateOp().Set(Gf.Vec3d(*waypoint["translation"]))
        marker.AddScaleOp().Set(Gf.Vec3f(0.11, 0.11, 0.11))
        marker.GetDisplayColorAttr().Set([Gf.Vec3f(0.18, 0.20, 0.24)])
        marker.GetPrim().SetCustomDataByKey("ops:id", waypoint["id"])
        marker.GetPrim().SetCustomDataByKey("ops:section", "amr_waypoints")
        marker.GetPrim().SetCustomDataByKey("ops:task", waypoint["task"])
        marker.GetPrim().SetCustomDataByKey("ops:wait_seconds", waypoint["wait_seconds"])


if __name__ == "__main__":
    create_amr_waypoint_task()
