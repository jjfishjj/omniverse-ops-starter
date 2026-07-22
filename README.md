# Omniverse Ops Starter

一個 NVIDIA Omniverse / OpenUSD 工廠數位孿生 starter project。專案用 Python 從 JSON layout 產生 `.usda` 場景，並附上一個 Omniverse Kit extension 範例，方便之後擴充成工廠監控、設備配置、物流動線或機器人模擬工具。

## 專案亮點

- 資料驅動場景：`data/factory_layout.json` 管理設備、感測器、安全區與物流流程節點
- OpenUSD 優先：有 `pxr` / `usd-core` 時使用正式 OpenUSD Python API
- USD composition：產生 base / equipment / sensors / flow / AMR layers 與 `opsScenario` variant set
- Live telemetry：標準庫 WebSocket server 串接 web dashboard
- Isaac-ready AMR：提供 AMR route、waypoints 與 Isaac scenario proxy layer
- 可離線展示：沒有 OpenUSD runtime 時會輸出 readable USDA fallback
- Kit extension：可在 Omniverse Kit-based app 中一鍵建立 / 更新場景
- 驗證工具：依 layout contract 檢查必要 prim 與 metadata

## 專案結構

```text
.
├── data/
│   └── factory_layout.json
├── docs/
│   ├── setup.md
│   ├── isaac-amr-scenario.md
│   ├── live-telemetry.md
│   ├── usd-layers-and-variants.md
│   └── workflow.md
├── isaac/
│   └── amr_waypoint_task.py
├── kit-extension/
│   └── exts/omniverse.ops.starter/
├── output/
│   └── .gitkeep
├── scripts/
│   ├── create_demo_stage.py
│   ├── create_layered_stage.py
│   ├── telemetry_server.py
│   ├── validate_layered_stage.py
│   └── validate_stage.py
├── tests/
│   └── test_scene_contract.py
├── web-demo/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── pyproject.toml
└── README.md
```

## 快速開始

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[usd]"
```

產生範例 USD 場景：

```bash
python scripts/create_demo_stage.py --output output/demo_factory.usda
```

驗證場景：

```bash
python scripts/validate_stage.py output/demo_factory.usda
```

產生 layered USD + variants + AMR scenario：

```bash
python scripts/create_layered_stage.py --output-dir output/layers
python scripts/validate_layered_stage.py output/layers/factory_composed.usda
```

啟動 live telemetry：

```bash
python scripts/telemetry_server.py --scenario peak_hour
```

跑測試：

```bash
python -m unittest discover -s tests
```

開啟網頁互動展示：

```bash
open web-demo/index.html
```

## 場景內容

目前的 factory twin 包含：

- `/World/Equipment`：輸送帶、機械手臂工作站、AOI 檢測站
- `/World/Sensors`：溫度、壓力、震動感測器與 threshold metadata
- `/World/SafetyZones`：機械手臂安全區、forklift lane
- `/World/FlowMarkers`：inbound、handoff、inspection、outbound 流程節點
- `/World/Lighting` 與 `/World/Cameras`：基本展示用燈光與 overview camera
- `/World/Robots/AMR_01`：Isaac-ready AMR proxy
- `/World/AMRRoute`：AMR mission waypoints

## Omniverse Kit Extension

Extension 位於：

```text
kit-extension/exts/omniverse.ops.starter
```

在 Kit-based app 中把 `kit-extension/exts` 加入 extension search path，啟用 `omniverse.ops.starter` 後，會看到 `Omniverse Ops Starter` 視窗，可按 `Create / Update Scene` 建立場景。

## Web Demo

`web-demo/index.html` 是一個純靜態互動展示端，適合放在 GitHub Pages 或直接用瀏覽器開啟。它會優先讀取 `data/factory_layout.json`，並提供內建 fallback，讓 demo 在本機檔案模式也能正常展示。

若啟動 `scripts/telemetry_server.py`，web demo 會自動切換成 live telemetry dashboard，顯示 WebSocket 狀態、即時感測器值、KPI 與 AMR mission progress。

## 延伸文件

- [USD Layers and Variants](docs/usd-layers-and-variants.md)
- [Live Telemetry WebSocket](docs/live-telemetry.md)
- [Isaac Sim AMR Scenario](docs/isaac-amr-scenario.md)

## 參考

- [NVIDIA Omniverse Documentation](https://docs.nvidia.com/omniverse/index.html)
- [NVIDIA Omniverse Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template)
- [OpenUSD Documentation](https://openusd.org/release/index.html)

## 授權

MIT License
