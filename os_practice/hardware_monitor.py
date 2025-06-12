#!/usr/bin/env python3
"""
macOS 硬體監控程式 (macOS Hardware Monitor)

功能說明：
1. 系統硬體資訊監控
   - CPU 使用率和頻率
   - 記憶體使用情況
   - 硬碟空間分析
   - 電池狀態監控

2. 即時監控功能
   - 每 3 秒更新一次系統狀態
   - 支援優雅的程式中斷（Ctrl+C）
   - 美觀的 emoji 輸出介面

3. 系統要求：
   - macOS 作業系統
   - Python 3.6+
   - psutil 套件 (用於系統資訊收集)

技術實現：
1. 使用 psutil 進行跨平台系統監控
2. 使用 system_profiler 獲取 macOS 特定資訊

作者：[簡偉恆]
版本：1.0.0
最後更新：2025/06/12
"""

import subprocess  # 用於執行系統命令（system_profiler, powermetrics）
import json       # 用於解析系統資訊的 JSON 輸出
import time       # 用於控制監控間隔和計時
import psutil     # 用於獲取系統性能指標
from datetime import datetime  # 用於生成時間戳記

class MacHardwareMonitor:
    """
    macOS 硬體監控器核心類別
    
    主要功能：
    1. 收集系統硬體資訊
    2. 監控系統資源使用情況
    3. 提供即時系統狀態報告
    
    技術特點：
    - 使用 psutil 實現跨平台相容性
    - 整合 macOS 專用系統工具
    - 支援即時監控和數據匯出
    """
    
    def __init__(self):
        """
        初始化監控器實例
        
        執行步驟：
        1. 初始化系統資訊收集
        2. 設置監控參數
        3. 準備資料結構
        
        異常處理：
        - 如果初始化失敗，system_info 將為空字典
        """
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """
        獲取詳細的系統硬體資訊
        
        實現方式：
        1. 使用 system_profiler 命令獲取 macOS 系統詳細資訊
        2. 解析 JSON 格式的輸出
        3. 提取關鍵硬體參數
        
        返回資料結構：
        {
            'model': str,      # 機器型號（例：'MacBook Pro (13-inch, M1, 2020)'）
            'processor': str,   # 處理器資訊（例：'Apple M1'）
            'memory': str,      # 記憶體大小（例：'8 GB'）
            'serial': str       # 序號（用於識別特定裝置）
        }
        
        錯誤處理：
        - 命令執行失敗時返回空字典
        - 解析錯誤時返回空字典
        """
        try:
            # 執行 system_profiler 命令獲取系統資訊
            # SPHardwareDataType 專門用於獲取硬體資訊
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType', '-json'], 
                capture_output=True,   # 捕獲命令輸出
                text=True              # 將輸出轉換為文字
            )
            
            # 檢查命令是否成功執行
            if result.returncode == 0:
                # 解析 JSON 格式的輸出
                data = json.loads(result.stdout)
                hardware_info = data['SPHardwareDataType'][0]
                
                # 提取並返回關鍵硬體資訊
                return {
                    'model': hardware_info.get('machine_model', 'Unknown'),      # 機器型號
                    'processor': hardware_info.get('cpu_type', 'Unknown'),       # CPU 型號
                    'memory': hardware_info.get('physical_memory', 'Unknown'),   # 實體記憶體
                    'serial': hardware_info.get('serial_number', 'Unknown')      # 序號
                }
        except Exception as e:
            print(f"無法取得系統資訊: {e}")
        return {}
    
    def get_cpu_info(self):
        """
        獲取 CPU 詳細使用狀況
        
        監控指標：
        1. 每個核心的使用率
        2. 整體 CPU 使用率
        3. 當前運作頻率
        4. CPU 核心數量
        
        實現細節：
        - 使用 psutil.cpu_percent() 獲取 CPU 使用率
        - interval=1 表示等待 1 秒以獲取準確的使用率
        - percpu=True 表示獲取每個核心的數據
        
        返回資料結構：
        {
            'usage_per_core': [float, ...],  # 每個核心的使用率（百分比）
            'average_usage': float,          # 平均使用率（百分比）
            'frequency': float,              # 當前頻率（MHz）
            'cores': int                     # 核心數量
        }
        """
        # 獲取每個 CPU 核心的使用率（等待 1 秒以獲得準確數據）
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        
        # 獲取 CPU 頻率資訊（如果可用）
        cpu_freq = psutil.cpu_freq()
        
        # 獲取 CPU 核心數
        cpu_count = psutil.cpu_count()
        
        return {
            'usage_per_core': cpu_percent,                        # 列表：每個核心的使用率
            'average_usage': sum(cpu_percent) / len(cpu_percent), # 平均使用率
            'frequency': cpu_freq.current if cpu_freq else 'Unknown',  # 當前頻率
            'cores': cpu_count                                    # 邏輯核心數量
        }
    
    def get_memory_info(self):
        """
        獲取系統記憶體使用狀況
        
        監控指標：
        1. 總記憶體大小
        2. 已使用記憶體
        3. 可用記憶體
        4. 使用率百分比
        
        技術說明：
        - 使用 psutil.virtual_memory() 獲取記憶體資訊
        - 數值會自動轉換為 GB 為單位
        - 精確度保留到小數點後兩位
        
        返回資料結構：
        {
            'total_gb': float,      # 總容量（GB）
            'used_gb': float,       # 已使用（GB）
            'available_gb': float,  # 可用容量（GB）
            'usage_percent': float  # 使用率（%）
        }
        
        計算方式：
        - 1 GB = 1024³ bytes
        - 使用率 = (已使用/總容量) * 100%
        """
        # 獲取記憶體使用資訊
        memory = psutil.virtual_memory()
        
        # 轉換數值為 GB 並返回
        return {
            'total_gb': round(memory.total / (1024**3), 2),      # 總容量（GB）
            'used_gb': round(memory.used / (1024**3), 2),        # 已使用（GB）
            'available_gb': round(memory.available / (1024**3), 2), # 可用（GB）
            'usage_percent': memory.percent                       # 使用率（%）
        }
    
    def get_disk_info(self):
        """
        獲取硬碟使用狀況
        
        監控指標：
        1. 總容量
        2. 已使用空間
        3. 可用空間
        4. 使用率
        
        技術說明：
        - 使用 psutil.disk_usage() 獲取磁碟使用資訊
        - 預設監控根目錄 '/'
        - 容量單位自動轉換為 GB
        
        返回資料結構：
        {
            'total_gb': float,      # 總容量（GB）
            'used_gb': float,       # 已使用（GB）
            'free_gb': float,       # 剩餘（GB）
            'usage_percent': float  # 使用率（%）
        }
        
        注意事項：
        - 數值會自動四捨五入到小數點後兩位
        - 使用率考慮了系統保留空間
        """
        # 獲取根目錄的磁碟使用資訊
        disk = psutil.disk_usage('/')
        
        # 轉換數值為 GB 並返回
        return {
            'total_gb': round(disk.total / (1024**3), 2),        # 總容量（GB）
            'used_gb': round(disk.used / (1024**3), 2),          # 已使用（GB）
            'free_gb': round(disk.free / (1024**3), 2),          # 剩餘（GB）
            'usage_percent': round((disk.used / disk.total) * 100, 2)  # 使用率（%）
        }
    
    def get_battery_info(self):
        """
        獲取電池狀態資訊
        
        監控指標：
        1. 電池電量百分比
        2. 充電狀態
        3. 預估剩餘使用時間
        
        技術說明：
        - 使用 psutil.sensors_battery() 獲取電池資訊
        - 時間格式化為小時和分鐘
        - 支援充電狀態檢測
        
        返回資料結構：
        {
            'percent': float,     # 電量百分比（0-100）
            'charging': bool,     # 是否正在充電
            'time_left': str      # 剩餘時間（格式：'Xh Ym'）
        }
        
        特殊情況處理：
        - 無法獲取電池資訊時返回錯誤訊息
        - 充電時間可能顯示為 'Unknown'
        """
        try:
            # 獲取電池資訊
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,                    # 電量百分比
                    'charging': battery.power_plugged,            # 充電狀態
                    'time_left': str(battery.secsleft // 3600) + 'h ' + 
                                str((battery.secsleft % 3600) // 60) + 'm'  # 剩餘時間
                                if battery.secsleft != psutil.POWER_TIME_UNLIMITED 
                                else 'Unknown'
                }
        except:
            pass
        return {'error': '無法取得電池資訊'}
    
    def monitor_realtime(self, duration=30):
        """
        即時監控系統狀態
        """
        print("🔍 macOS 硬體監控程式")
        print("=" * 50)
        
        # 顯示基本系統資訊
        if self.system_info:
            print(f"💻 型號: {self.system_info.get('model', 'Unknown')}")
            print(f"🧠 處理器: {self.system_info.get('processor', 'Unknown')}")
            print(f"💾 記憶體: {self.system_info.get('memory', 'Unknown')}")
            print("=" * 50)
        
        start_time = time.time()
        
        try:
            # 監控迴圈
            while time.time() - start_time < duration:
                # 顯示時間戳記
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
                
                # 獲取並顯示 CPU 資訊
                cpu_info = self.get_cpu_info()
                print(f"🔥 CPU 使用率: {cpu_info['average_usage']:.1f}%")
                
                # 獲取並顯示記憶體資訊
                memory_info = self.get_memory_info()
                print(f"💾 記憶體: {memory_info['used_gb']:.1f}GB / {memory_info['total_gb']:.1f}GB ({memory_info['usage_percent']:.1f}%)")
                
                # 獲取並顯示硬碟資訊
                disk_info = self.get_disk_info()
                print(f"💽 硬碟: {disk_info['used_gb']:.1f}GB / {disk_info['total_gb']:.1f}GB ({disk_info['usage_percent']:.1f}%)")
                
                # 獲取並顯示電池資訊（如果可用）
                battery_info = self.get_battery_info()
                if 'error' not in battery_info:
                    charging_status = "🔌 充電中" if battery_info['charging'] else "🔋 電池"
                    print(f"{charging_status}: {battery_info['percent']}% ({battery_info['time_left']})")
                
                print("-" * 30)
                time.sleep(3)  # 暫停 3 秒後更新資訊
                
        except KeyboardInterrupt:
            print("\n\n👋 監控結束")

def main():
    """
    主程式入口
    """
    monitor = MacHardwareMonitor()
    
    # 顯示功能選單
    print("選擇功能:")
    print("1. 顯示系統資訊")
    print("2. 即時監控 (30秒)")
    print("3. 詳細硬體報告")
    
    choice = input("\n請選擇 (1-3): ").strip()
    
    # 處理使用者選擇
    if choice == "1":
        print("\n📊 系統資訊:")
        print(json.dumps(monitor.system_info, indent=2, ensure_ascii=False))
        
    elif choice == "2":
        monitor.monitor_realtime()
        
    elif choice == "3":
        print("\n📋 詳細硬體報告:")
        print("CPU:", json.dumps(monitor.get_cpu_info(), indent=2, ensure_ascii=False))
        print("Memory:", json.dumps(monitor.get_memory_info(), indent=2, ensure_ascii=False))
        print("Disk:", json.dumps(monitor.get_disk_info(), indent=2, ensure_ascii=False))
        print("Battery:", json.dumps(monitor.get_battery_info(), indent=2, ensure_ascii=False))
    
    else:
        print("❌ 無效選擇")

if __name__ == "__main__":
    main() 