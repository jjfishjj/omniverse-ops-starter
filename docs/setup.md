# 環境設定

## 基本需求

這個專案分成兩種使用方式：

1. 純 Python / OpenUSD：適合先練習 USD 檔案建立與驗證。
2. Omniverse Kit：適合在 NVIDIA Omniverse Kit SDK 應用內載入 extension。

## Python 環境

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

如果要使用正式 OpenUSD Python API：

```bash
python -m pip install -e ".[usd]"
```

## Omniverse / Kit SDK 注意事項

NVIDIA 目前的 Omniverse 開發重點以 Kit SDK、OpenUSD、API 與工作流為主。舊的 Launcher、USD Composer、USD Explorer 文件已被 NVIDIA 歸在 legacy documentation。

建議新專案從 Kit App Template 開始：

```bash
git clone https://github.com/NVIDIA-Omniverse/kit-app-template.git
cd kit-app-template
./repo.sh template new
```

Windows 則使用：

```powershell
.\repo.bat template new
```

建立 Kit app 後，把本專案的 extension 路徑加入 extension search path，即可載入 `omniverse.ops.starter`。
