# Live Telemetry WebSocket

`scripts/telemetry_server.py` 會用 Python 標準庫提供一個小型 WebSocket feed，讓 web demo 從 local animation 升級成 live digital twin dashboard。

## 啟動 telemetry server

```bash
python scripts/telemetry_server.py --scenario peak_hour
```

預設會啟動：

```text
ws://127.0.0.1:8766/ws
```

## 啟動 web demo

建議用靜態 server 開啟，這樣前端可以讀取 `data/*.json`：

```bash
python3 -m http.server 8765
```

然後打開：

```text
http://127.0.0.1:8765/web-demo/
```

Web demo 會自動嘗試連到 `ws://127.0.0.1:8766/ws`。

## Telemetry payload

每筆訊息包含：

- `scenario`：目前情境
- `kpis`：throughput、OEE、alert load
- `sensors`：感測器即時值、threshold、狀態
- `equipment`：設備情境狀態
- `amr`：AMR 位置、下一個 waypoint、任務、載重

如果 telemetry server 沒有啟動，web demo 會自動維持 local simulation fallback。
