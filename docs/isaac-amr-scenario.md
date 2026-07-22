# Isaac Sim AMR Scenario

這個專案加入了一個 AMR material-run scenario，讓 Omniverse factory twin 可以往 Isaac Sim 機器人模擬延伸。

## AMR route data

```text
data/amr_routes.json
```

目前包含：

- `AMR_01`：line-side material runner
- 4 個 waypoint：Inbound dock、Conveyor drop、Inspection pickup、Outbound dock
- safety policy：避開 `Robot_Cell_Safety`，優先使用 `Forklift_Lane`

## 產生 Isaac-ready proxy layer

```bash
python scripts/create_layered_stage.py --output-dir output/layers
```

AMR 相關內容會輸出在：

```text
output/layers/amr_scenario.usda
```

Composed stage：

```text
output/layers/factory_composed.usda
```

## 在 Isaac Sim 中延伸

這個 repo 先提供 Isaac scenario proxy。進入完整 Isaac Sim 專案時，可以把 `/World/Robots/AMR_01` 的 capsule proxy 換成真實 wheeled robot asset，並沿用：

- `/World/AMRRoute/*` waypoints
- `/World/IsaacScenario` metadata
- `data/amr_routes.json` route order
- `Forklift_Lane` preferred lane
- `Robot_Cell_Safety` avoid zone

也可以在 Isaac Sim Script Editor 中執行：

```text
isaac/amr_waypoint_task.py
```

它會在目前 stage 建立 `/World/Robots/AMR_01`、`/World/AMRRoute/*` 和 `/World/IsaacScenario` metadata。

## 下一步可做

- 用 Isaac Sim differential drive controller 跑 waypoint following
- 加入 obstacle prims 與 safety-zone collision checks
- 輸出 AMR mission log 到 `output/amr_mission_report.json`
- 將 AMR position stream 寫回 telemetry WebSocket，讓 web demo 顯示 live robot movement
