"""Minimal Omniverse Kit extension for creating a demo operations scene."""

from __future__ import annotations

import omni.ext
import omni.kit.viewport.utility
import omni.ui as ui
import omni.usd
from pxr import Gf, UsdGeom, UsdLux


class OmniverseOpsStarterExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str) -> None:
        self._window = ui.Window("Omniverse Ops Starter", width=340, height=160)
        with self._window.frame:
            with ui.VStack(spacing=8, height=0):
                ui.Label("Demo Factory Scene", height=24)
                ui.Button("Create Scene", clicked_fn=self._create_scene)
                ui.Button("Frame Stage", clicked_fn=self._frame_stage)

    def on_shutdown(self) -> None:
        self._window = None

    def _create_scene(self) -> None:
        context = omni.usd.get_context()
        stage = context.get_stage()
        if stage is None:
            context.new_stage()
            stage = context.get_stage()

        UsdGeom.Xform.Define(stage, "/World")
        UsdGeom.Xform.Define(stage, "/World/Equipment")
        UsdGeom.Xform.Define(stage, "/World/Sensors")
        UsdGeom.Xform.Define(stage, "/World/Lighting")

        ground = UsdGeom.Cube.Define(stage, "/World/Ground")
        ground.AddTranslateOp().Set(Gf.Vec3d(0, 0, -0.03))
        ground.AddScaleOp().Set(Gf.Vec3f(5, 3, 0.03))
        ground.GetDisplayColorAttr().Set([Gf.Vec3f(0.22, 0.23, 0.24)])

        conveyor = UsdGeom.Cube.Define(stage, "/World/Equipment/Conveyor_A")
        conveyor.AddTranslateOp().Set(Gf.Vec3d(-2.5, 0, 0.45))
        conveyor.AddScaleOp().Set(Gf.Vec3f(1.8, 0.35, 0.35))
        conveyor.GetDisplayColorAttr().Set([Gf.Vec3f(0.10, 0.35, 0.85)])

        robot_cell = UsdGeom.Cube.Define(stage, "/World/Equipment/Robot_Cell_B")
        robot_cell.AddTranslateOp().Set(Gf.Vec3d(2, 0.4, 0.7))
        robot_cell.AddScaleOp().Set(Gf.Vec3f(0.8, 0.8, 0.7))
        robot_cell.GetDisplayColorAttr().Set([Gf.Vec3f(0.85, 0.35, 0.10)])

        for name, position, color in [
            ("Temperature_01", Gf.Vec3d(-3, -0.8, 1.25), Gf.Vec3f(0.95, 0.15, 0.20)),
            ("Pressure_01", Gf.Vec3d(0, 1.1, 1.15), Gf.Vec3f(0.15, 0.80, 0.35)),
            ("Vibration_01", Gf.Vec3d(2.5, -0.8, 1.4), Gf.Vec3f(0.95, 0.78, 0.12)),
        ]:
            sensor = UsdGeom.Sphere.Define(stage, f"/World/Sensors/{name}")
            sensor.CreateRadiusAttr(0.15)
            sensor.AddTranslateOp().Set(position)
            sensor.GetDisplayColorAttr().Set([color])

        light = UsdLux.DistantLight.Define(stage, "/World/Lighting/KeyLight")
        light.CreateIntensityAttr(450.0)
        light.CreateAngleAttr(0.7)
        light.AddRotateXYZOp().Set(Gf.Vec3f(-45, 0, 35))

    def _frame_stage(self) -> None:
        viewport = omni.kit.viewport.utility.get_active_viewport()
        if viewport:
            viewport.frame_all()
