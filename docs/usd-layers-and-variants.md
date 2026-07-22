# USD Layers and Variants

這個專案現在支援 layered OpenUSD 輸出，用來展示 Omniverse 專案常見的 composition workflow。

## 產生 layered stage

```bash
python scripts/create_layered_stage.py --output-dir output/layers
```

產出內容：

```text
output/layers/
├── factory_base.usda
├── equipment.usda
├── sensors.usda
├── safety_zones.usda
├── flow_markers.usda
├── amr_scenario.usda
└── factory_composed.usda
```

`factory_composed.usda` 使用 `subLayers` 組合其他 layer，並在 `/World` 上提供 `opsScenario` variant set。

## 驗證

```bash
python scripts/validate_layered_stage.py output/layers/factory_composed.usda
```

若安裝了 `usd-core`，validator 會用 OpenUSD Python API 打開 composed stage，檢查：

- layer composition 能否解析
- `/World` 是否有 `opsScenario`
- baseline / peak_hour / maintenance variants 是否存在
- AMR robot 與 waypoints 是否存在

## Variant 設定來源

```text
data/ops_scenarios.json
```

目前 variants：

- `baseline`：正常營運
- `peak_hour`：尖峰產能壓力
- `maintenance`：Robot cell 維護，AMR 改走 bypass flow
