# 環境設定

## 基本需求

這個專案分成兩種使用方式：

1. 純 Python / OpenUSD：產生與驗證 `.usda` 場景。
2. Omniverse Kit extension：在 Kit-based app 中建立同樣的工廠數位孿生場景。

## Python 環境

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[usd]"
```

如果暫時不想安裝 `usd-core`，也可以只跑：

```bash
python -m pip install -e .
```

此時 `scripts/create_demo_stage.py` 會使用 USDA fallback writer 產生文字格式場景。

## 產生與驗證

```bash
python scripts/create_demo_stage.py --output output/demo_factory.usda
python scripts/validate_stage.py output/demo_factory.usda
python -m unittest discover -s tests
```

## Omniverse / Kit SDK

建議新專案從 NVIDIA Kit App Template 開始：

```bash
git clone https://github.com/NVIDIA-Omniverse/kit-app-template.git
cd kit-app-template
./repo.sh template new
```

Windows 則使用：

```powershell
.\repo.bat template new
```

建立 Kit app 後，把本專案的 extension 路徑加入 extension search path：

```text
kit-extension/exts
```

再啟用 extension：

```text
omniverse.ops.starter
```
