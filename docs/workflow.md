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

## 4. 在 Omniverse 中使用

有 Omniverse Kit-based app 時，可以直接開啟：

```text
output/demo_factory.usda
```

也可以載入 extension：

```text
kit-extension/exts/omniverse.ops.starter
```

啟用後按 `Create / Update Scene`，即可在目前 stage 生成工廠數位孿生範例。

## 5. 開啟網頁互動展示

```bash
open web-demo/index.html
```

Web demo 會用同一份 factory layout 顯示 KPI、感測器狀態、設備詳情、安全區與流程節點。若透過本機檔案直接開啟而無法 fetch JSON，前端會使用內建 fallback layout。

## 6. 下一步擴充方向

- 改成讀取真實工廠設備 CSV / MES / IoT API
- 把 sensor value 做成 live update
- 加入 PhysX rigid body、碰撞與安全邊界測試
- 串 Isaac Sim 做 AMR 或機械手臂訓練場景
- 把 validation 加到 GitHub Actions
- 把 `web-demo/` 發佈成 GitHub Pages 或 Sites production demo
