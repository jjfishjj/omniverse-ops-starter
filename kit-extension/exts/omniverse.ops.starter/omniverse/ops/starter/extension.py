"""Omniverse Kit extension for creating a compact operations digital twin scene."""

from __future__ import annotations

import omni.ext
import omni.kit.viewport.utility
import omni.ui as ui
import omni.usd
from pxr import Gf, UsdGeom, UsdLux


EQUIPMENT = [
    {
        "id": "Conveyor_A",
        "role": "inbound conveyor",
        "status": "running",
        "translation": (-2.7, 0.0, 0.38),
        "scale": (1.9, 0.32, 0.28),
        "color": (0.10, 0.35, 0.85),
    },
    {
        "id": "Robot_Cell_B",
        "role": "pick and place cell",
        "status": "ready",
        "translation": (1.35, 0.55, 0.72),
        "scale": (0.72, 0.72, 0.72),
        "color": (0.85, 0.35, 0.10),
    },
    {
        "id": "Inspection_C",
        "role": "vision quality gate",
        "status": "watch",
        "translation": (3.2, -0.1, 0.52),
        "scale": (0.62, 0.48, 0.52),
        "color": (0.22, 0.62, 0.44),
    },
]

SENSORS = [
    {
        "id": "Temperature_01",
        "role": "temperature",
        "unit": "C",
        "value": 37.4,
        "threshold": 45.0,
        "translation": (-3.15, -0.78, 1.16),
        "scale": (0.15, 0.15, 0.15),
        "color": (0.95, 0.15, 0.20),
    },
    {
        "id": "Pressure_01",
        "role": "air pressure",
        "unit": "bar",
        "value": 5.8,
        "threshold": 6.2,
        "translation": (0.0, 1.05, 1.08),
        "scale": (0.15, 0.15, 0.15),
        "color": (0.15, 0.80, 0.35),
    },
    {
        "id": "Vibration_01",
        "role": "vibration",
        "unit": "mm/s",
        "value": 2.1,
        "threshold": 4.5,
        "translation": (2.45, -0.78, 1.25),
        "scale": (0.15, 0.15, 0.15),
        "color": (0.95, 0.78, 0.12),
    },
]

SAFETY_ZONES = [
    {
        "id": "Robot_Cell_Safety",
        "translation": (1.35, 0.55, 0.04),
        "scale": (1.25, 1.05, 0.035),
        "color": (0.95, 0.78, 0.12),
        "opacity": 0.32,
    },
    {
        "id": "Forklift_Lane",
        "translation": (0.0, -1.55, 0.035),
        "scale": (4.6, 0.22, 0.025),
        "color": (0.15, 0.62, 0.95),
        "opacity": 0.28,
    },
]

FLOW_MARKERS = [
    ("Inbound", (-3.9, 0.0, 0.18), (0.10, 0.35, 0.85)),
    ("Robot_Handoff", (-0.55, 0.0, 0.18), (0.85, 0.35, 0.10)),
    ("Inspection", (2.4, -0.08, 0.18), (0.22, 0.62, 0.44)),
    ("Outbound", (4.05, -0.08, 0.18), (0.95, 0.78, 0.12)),
]


def _set_transform(schema, translation, scale=None, rotation=None) -> None:
    xformable = UsdGeom.Xformable(schema.GetPrim())
    xformable.ClearXformOpOrder()
    xformable.AddTranslateOp().Set(Gf.Vec3d(*translation))
    if rotation is not None:
        xformable.AddRotateXYZOp().Set(Gf.Vec3f(*rotation))
    if scale is not None:
        xformable.AddScaleOp().Set(Gf.Vec3f(*scale))


def _set_display(schema, color, opacity=None) -> None:
    schema.GetDisplayColorAttr().Set([Gf.Vec3f(*color)])
    if opacity is not None:
        schema.GetDisplayOpacityAttr().Set([float(opacity)])


def _set_ops_metadata(prim, section: str, item: dict) -> None:
    prim.SetCustomDataByKey("ops:id", item["id"])
    prim.SetCustomDataByKey("ops:section", section)
    for key in ["role", "status", "unit", "value", "threshold", "opacity"]:
        if key in item:
            prim.SetCustomDataByKey(f"ops:{key}", item[key])


class OmniverseOpsStarterExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str) -> None:
        self._status_label = None
        self._window = ui.Window("Omniverse Ops Starter", width=360, height=188)
        with self._window.frame:
            with ui.VStack(spacing=8, height=0):
                ui.Label("Factory Digital Twin", height=24)
                ui.Button("Create / Update Scene", clicked_fn=self._create_scene)
                ui.Button("Frame Stage", clicked_fn=self._frame_stage)
                self._status_label = ui.Label("Ready", height=22)

    def on_shutdown(self) -> None:
        self._window = None
        self._status_label = None

    def _create_scene(self) -> None:
        context = omni.usd.get_context()
        stage = context.get_stage()
        if stage is None:
            context.new_stage()
            stage = context.get_stage()

        world = UsdGeom.Xform.Define(stage, "/World")
        stage.SetDefaultPrim(world.GetPrim())
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)

        for path in [
            "/World/Equipment",
            "/World/Sensors",
            "/World/SafetyZones",
            "/World/FlowMarkers",
            "/World/Lighting",
            "/World/Cameras",
        ]:
            UsdGeom.Xform.Define(stage, path)

        ground = UsdGeom.Cube.Define(stage, "/World/Ground")
        _set_transform(ground, (0, 0, -0.035), (5.2, 2.2, 0.035))
        _set_display(ground, (0.22, 0.23, 0.24))
        ground.GetPrim().SetCustomDataByKey("ops:id", "Factory_Floor")

        for item in EQUIPMENT:
            equipment = UsdGeom.Cube.Define(stage, f"/World/Equipment/{item['id']}")
            _set_transform(equipment, item["translation"], item["scale"])
            _set_display(equipment, item["color"])
            _set_ops_metadata(equipment.GetPrim(), "equipment", item)

        for item in SENSORS:
            sensor = UsdGeom.Sphere.Define(stage, f"/World/Sensors/{item['id']}")
            sensor.CreateRadiusAttr(1.0)
            _set_transform(sensor, item["translation"], item["scale"])
            _set_display(sensor, item["color"])
            _set_ops_metadata(sensor.GetPrim(), "sensors", item)

        for item in SAFETY_ZONES:
            zone = UsdGeom.Cube.Define(stage, f"/World/SafetyZones/{item['id']}")
            _set_transform(zone, item["translation"], item["scale"])
            _set_display(zone, item["color"], item["opacity"])
            _set_ops_metadata(zone.GetPrim(), "safety_zones", item)

        for marker_id, translation, color in FLOW_MARKERS:
            marker = UsdGeom.Sphere.Define(stage, f"/World/FlowMarkers/{marker_id}")
            marker.CreateRadiusAttr(1.0)
            _set_transform(marker, translation, (0.16, 0.16, 0.16))
            _set_display(marker, color)
            marker.GetPrim().SetCustomDataByKey("ops:id", marker_id)
            marker.GetPrim().SetCustomDataByKey("ops:section", "flow_markers")

        key_light = UsdLux.DistantLight.Define(stage, "/World/Lighting/KeyLight")
        key_light.CreateIntensityAttr(650.0)
        key_light.CreateAngleAttr(0.65)
        _set_transform(key_light, (0, 0, 0), rotation=(-45, 0, 35))

        fill_light = UsdLux.SphereLight.Define(stage, "/World/Lighting/FillLight")
        fill_light.CreateIntensityAttr(180.0)
        fill_light.CreateRadiusAttr(3.0)
        _set_transform(fill_light, (-2.0, -2.0, 4.0))

        camera = UsdGeom.Camera.Define(stage, "/World/Cameras/Overview")
        camera.CreateFocalLengthAttr(28.0)
        _set_transform(camera, (4.2, -4.2, 3.1), rotation=(60, 0, 42))

        if self._status_label:
            self._status_label.text = "Scene updated"

    def _frame_stage(self) -> None:
        viewport = omni.kit.viewport.utility.get_active_viewport()
        if viewport:
            viewport.frame_all()
