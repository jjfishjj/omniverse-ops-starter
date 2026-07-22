# 操作流程

## 1. 調整工廠 layout

主要設定檔：

```text
data/factory_layout.json
```

你可以在這裡調整：

- `equipment`：設備 ID、角色、狀態、位置、尺寸、營運 metrics
- `sensors`：感測器數值、單位、threshold、位置
- `safety_zones`：安全區範圍、透明度、顏色
- `flow_markers`：物流或製程流程節點

## 2. 產生 USD 場景

```bash
python scripts/create_demo_stage.py --output output/demo_factory.usda
```

有安裝 `usd-core` 時會用 OpenUSD Python API 輸出；沒有安裝時會使用 USDA fallback writer。

## 3. 驗證 USD 場景

```bash
python scripts/validate_stage.py output/demo_factory.usda
```

驗證腳本會依 `data/factory_layout.json` 推導必要 prim，並檢查 metadata marker。

## 4. 產生 USD layers 與 variants

```bash
python scripts/create_layered_stage.py --output-dir output/layers
python scripts/validate_layered_stage.py output/layers/factory_composed.usda
```

`factory_composed.usda` 會透過 subLayers 組合 base、equipment、sensors、safety zones、flow markers 和 AMR scenario，並在 `/World` 提供 `opsScenario` variant set。

## 5. 啟動 live telemetry

```bash
python scripts/telemetry_server.py --scenario peak_hour
```

預設 WebSocket endpoint：

```text
ws://127.0.0.1:8766/ws
```

## 6. 在 Omniverse 中使用

有 Omniverse Kit-based app 時，可以直接開啟：

```text
output/demo_factory.usda
```

或開啟 layered composed stage：

```text
output/layers/factory_composed.usda
```

也可以載入 extension：

```text
kit-extension/exts/omniverse.ops.starter
```

啟用後按 `Create / Update Scene`，即可在目前 stage 生成工廠數位孿生範例。

## 7. 開啟網頁互動展示

```bash
python3 -m http.server 8765
```

然後打開：

```text
http://127.0.0.1:8765/web-demo/
```

Web demo 會用同一份 factory layout 顯示 KPI、感測器狀態、設備詳情、安全區、流程節點與 AMR route。若 telemetry server 有啟動，會自動顯示 live WebSocket feed；若沒有啟動，會維持 local simulation fallback。

## 8. 下一步擴充方向

- 改成讀取真實工廠設備 CSV / MES / IoT API
- 把 sensor value 做成 live update
- 加入 PhysX rigid body、碰撞與安全邊界測試
- 串 Isaac Sim differential drive controller 跑 AMR waypoint following
- 把 validation 加到 GitHub Actions
- 把 `web-demo/` 發佈成 GitHub Pages 或 Sites production demo
