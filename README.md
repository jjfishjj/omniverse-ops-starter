# Omniverse Ops Starter

一個用來練習 NVIDIA Omniverse / OpenUSD 基本操作的入門專案。它示範如何用 Python 建立 USD 場景、驗證場景內容，並提供一個 Omniverse Kit extension 骨架，方便之後擴充成 UI 工具。

## 專案目標

- 建立一個可放上 GitHub 的 Omniverse 操作作品集專案
- 用 OpenUSD 概念建立簡單的數位孿生場景
- 提供清楚的中文操作文件
- 保留 Omniverse Kit SDK extension 的擴充入口

## 專案結構

```text
.
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
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## 快速開始

建立虛擬環境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

產生範例 USD 場景：

```bash
python scripts/create_demo_stage.py --output output/demo_factory.usda
```

驗證場景：

```bash
python scripts/validate_stage.py output/demo_factory.usda
```

## 產出的場景

`create_demo_stage.py` 會建立一個簡化的工廠數位孿生場景，包含：

- 地板
- 兩台設備
- 三個感測器節點
- 燈光
- 基本 metadata

如果環境有安裝 `pxr` / `usd-core`，腳本會使用 OpenUSD Python API 產生檔案；如果沒有，會用安全的 USDA 文字輸出作為 fallback，方便先學習與展示。

## Omniverse Kit Extension

`kit-extension/exts/omniverse.ops.starter` 是一個簡化的 Kit extension 範例，展示如何在 Omniverse Kit 裡建立一個工具視窗，並呼叫 USD stage 操作。

實際載入方式請依照 NVIDIA Kit App Template 或你自己的 Kit 應用設定 extension search path。

## 參考文件

- [NVIDIA Omniverse Docs](https://docs.nvidia.com/omniverse/index.html)
- [Omniverse Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template)
- [OpenUSD Documentation](https://openusd.org/release/index.html)

## 授權

MIT License
