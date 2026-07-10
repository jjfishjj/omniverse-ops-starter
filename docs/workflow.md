# 操作流程

## 1. 建立 USD 場景

```bash
python scripts/create_demo_stage.py --output output/demo_factory.usda
```

你會得到一個簡化工廠場景：

- `/World/Ground`
- `/World/Equipment/Conveyor_A`
- `/World/Equipment/Robot_Cell_B`
- `/World/Sensors/Temperature_01`
- `/World/Sensors/Pressure_01`
- `/World/Sensors/Vibration_01`
- `/World/Lighting/KeyLight`

## 2. 驗證 USD 場景

```bash
python scripts/validate_stage.py output/demo_factory.usda
```

驗證腳本會檢查必要 prim 是否存在，並回報檔案是否符合專案基本要求。

## 3. 在 Omniverse 中開啟

有 Omniverse Kit-based app 時，可以直接開啟 `output/demo_factory.usda`。建議用新的 Kit SDK workflow 或依照你建立的 Kit app 載入。

## 4. 下一步擴充方向

- 把設備位置改成讀取 CSV 或 JSON
- 加入工廠設備 metadata
- 加入材質與燈光 preset
- 把 validation 做成 CI 檢查
- 在 Kit extension 中加入按鈕，一鍵產生或更新場景
