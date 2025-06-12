# macOS 硬體監控程式

這是一個用 Python 編寫的 macOS 系統硬體監控工具，提供即時的系統資源使用情況監控。

## 功能特點

### 1. 系統資訊監控
- 🖥️ CPU 使用率和頻率
- 💾 記憶體使用情況
- 💽 硬碟空間分析
- 🔋 電池狀態監控

### 2. 即時監控
- ⏱️ 每 3 秒自動更新系統狀態
- ⌨️ 支援 Ctrl+C 優雅退出
- 🎨 美觀的 emoji 輸出介面

### 3. 多種監控模式
- 基本系統資訊顯示
- 即時監控（30 秒）
- 詳細硬體報告

## 系統需求

- macOS 作業系統
- Python 3.6+
- psutil 套件

## 安裝步驟

1. 確保已安裝 Python 3.6 或更高版本：
```bash
python3 --version
```

2. 安裝必要的套件：
```bash
pip3 install psutil
```

3. 克隆專案：
```bash
git clone https://github.com/william10310406/os-practice
cd os-practice
```

## 使用方法

執行程式：
```bash
python3 hardware_monitor.py
```

選擇功能：
1. 顯示系統資訊 - 查看基本硬體配置
2. 即時監控 - 持續 30 秒的系統監控
3. 詳細硬體報告 - 完整的系統狀態報告

## 程式架構

```
hardware_monitor.py
├── MacHardwareMonitor 類別
│   ├── get_system_info() - 獲取基本系統資訊
│   ├── get_cpu_info() - CPU 使用率和頻率
│   ├── get_memory_info() - 記憶體使用情況
│   ├── get_disk_info() - 硬碟使用情況
│   ├── get_battery_info() - 電池狀態
│   └── monitor_realtime() - 即時監控功能
└── main() - 主程式入口
```

## 輸出範例

### 系統資訊
```json
{
  "model": "MacBook Pro (M1, 2020)",
  "processor": "Apple M1",
  "memory": "16 GB"
}
```

### 即時監控
```
🔍 macOS 硬體監控程式
==================================================
💻 型號: MacBook Pro (M1, 2020)
🧠 處理器: Apple M1
💾 記憶體: 16 GB
==================================================

⏰ 14:30:45
🔥 CPU 使用率: 25.5%
💾 記憶體: 8.5GB / 16.0GB (53.1%)
💽 硬碟: 150.5GB / 500.0GB (30.1%)
🔌 充電中: 100% (充電完成)
------------------------------
```

## 技術實現

- 使用 `psutil` 進行跨平台系統監控
- 使用 `system_profiler` 獲取 macOS 特定資訊
- 使用 `subprocess` 執行系統命令
- 支援優雅的例外處理

## 貢獻

歡迎提交 Pull Request 或建立 Issue 來改進這個專案。

## 授權

本專案採用 MIT 授權條款 - 詳見 LICENSE 檔案 