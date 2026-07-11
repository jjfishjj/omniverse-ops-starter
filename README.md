# Omniverse Ops Starter

一個 NVIDIA Omniverse / OpenUSD 工廠數位孿生 starter project。專案用 Python 從 JSON layout 產生 `.usda` 場景，並附上一個 Omniverse Kit extension 範例，方便之後擴充成工廠監控、設備配置、物流動線或機器人模擬工具。

## 專案亮點

- 資料驅動場景：`data/factory_layout.json` 管理設備、感測器、安全區與物流流程節點
- OpenUSD 優先：有 `pxr` / `usd-core` 時使用正式 OpenUSD Python API
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
│   └── workflow.md
├── kit-extension/
│   └── exts/omniverse.ops.starter/
├── output/
│   └── .gitkeep
├── scripts/
│   ├── create_demo_stage.py
│   └── validate_stage.py
├── tests/
│   └── test_scene_contract.py
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

跑測試：

```bash
python -m unittest discover -s tests
```

## 場景內容

目前的 factory twin 包含：

- `/World/Equipment`：輸送帶、機械手臂工作站、AOI 檢測站
- `/World/Sensors`：溫度、壓力、震動感測器與 threshold metadata
- `/World/SafetyZones`：機械手臂安全區、forklift lane
- `/World/FlowMarkers`：inbound、handoff、inspection、outbound 流程節點
- `/World/Lighting` 與 `/World/Cameras`：基本展示用燈光與 overview camera

## Omniverse Kit Extension

Extension 位於：

```text
kit-extension/exts/omniverse.ops.starter
```

在 Kit-based app 中把 `kit-extension/exts` 加入 extension search path，啟用 `omniverse.ops.starter` 後，會看到 `Omniverse Ops Starter` 視窗，可按 `Create / Update Scene` 建立場景。

## 參考

- [NVIDIA Omniverse Documentation](https://docs.nvidia.com/omniverse/index.html)
- [NVIDIA Omniverse Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template)
- [OpenUSD Documentation](https://openusd.org/release/index.html)

## 授權

MIT License
