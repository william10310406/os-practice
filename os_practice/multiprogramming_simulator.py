#!/usr/bin/env python3
"""
多程式模擬器 (Multiprogramming Simulator)

功能說明：
1. 監控 macOS Dock 中的應用程式
2. 展示 CPU 排程（Round Robin）
3. 展示記憶體管理
4. 展示程式狀態轉換

作者：[簡偉恆]
版本：1.1.0
"""

import time
import random
import threading
import subprocess
import psutil
import json
from queue import Queue
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import os

class ProcessState(Enum):
    """程式狀態"""
    NEW = "新建"
    READY = "就緒"
    RUNNING = "運行中"
    WAITING = "等待中"
    TERMINATED = "終止"

@dataclass
class Process:
    """程式控制區塊 (PCB)"""
    pid: int                 # 程式 ID
    name: str               # 程式名稱
    priority: int           # 優先級
    memory_required: int    # 所需記憶體 (MB)
    cpu_burst: int          # CPU 執行時間 (秒)
    state: ProcessState     # 程式狀態
    remaining_time: int     # 剩餘執行時間
    memory_allocated: bool  # 記憶體分配狀態

class MemoryManager:
    """記憶體管理器"""
    def __init__(self, total_memory: int):
        self.total_memory = total_memory  # 總記憶體 (MB)
        self.available_memory = total_memory
        self.allocated_memory: Dict[int, int] = {}  # pid -> memory

    def allocate(self, pid: int, size: int) -> bool:
        """分配記憶體"""
        if self.available_memory >= size:
            self.available_memory -= size
            self.allocated_memory[pid] = size
            return True
        return False

    def deallocate(self, pid: int) -> None:
        """釋放記憶體"""
        if pid in self.allocated_memory:
            self.available_memory += self.allocated_memory[pid]
            del self.allocated_memory[pid]

class CPUScheduler:
    """CPU 排程器"""
    def __init__(self, time_quantum: int):
        self.ready_queue: Queue[Process] = Queue()  # 就緒佇列
        self.time_quantum = time_quantum            # 時間配額
        self.current_process: Process = None        # 當前運行程式
        self.processes: List[Process] = []          # 所有程式列表

    def add_process(self, process: Process) -> None:
        """添加程式到就緒佇列"""
        self.processes.append(process)
        self.ready_queue.put(process)
        process.state = ProcessState.READY

    def schedule(self) -> None:
        """排程下一個程式"""
        if self.current_process and self.current_process.state == ProcessState.RUNNING:
            if self.current_process.remaining_time > 0:
                self.ready_queue.put(self.current_process)
                self.current_process.state = ProcessState.READY

        if not self.ready_queue.empty():
            self.current_process = self.ready_queue.get()
            self.current_process.state = ProcessState.RUNNING

class DockMonitor:
    """Dock 應用程式監控器 (簡化版)"""
    def __init__(self):
        self.dock_apps = []
        self.update_dock_apps()

    def get_dock_apps(self) -> List[str]:
        """獲取 Dock 中正在執行的應用程式名稱清單"""
        script = '''
        tell application "System Events"
            set dockApps to name of every process whose background only is false
            return dockApps
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        apps = [app.strip() for app in result.stdout.strip().split(',') if app.strip()]
        return apps

    def update_dock_apps(self) -> None:
        self.dock_apps = self.get_dock_apps()

    def get_app_info(self, app_name: str) -> Optional[Dict]:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    if proc.info['name'].lower() == app_name.lower():
                        return {
                            'pid': proc.info['pid'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_mb': proc.info['memory_info'].rss / (1024 * 1024)
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue
        except Exception as e:
            print(f"獲取應用程式 {app_name} 資訊時發生錯誤: {e}")
        return None

class MultiprogrammingSimulator:
    """多程式模擬器"""
    def __init__(self, total_memory: int = 1024, time_quantum: int = 2):
        self.memory_manager = MemoryManager(total_memory)
        self.scheduler = CPUScheduler(time_quantum)
        self.running = False
        self.lock = threading.Lock()
        self.dock_monitor = DockMonitor()

    def create_process_from_dock(self, app_name: str, app_info: Dict) -> Process:
        """從 Dock 應用程式創建程序"""
        app_status = self.dock_monitor.dock_apps.get(app_name, {})
        app_details = self.dock_monitor.get_app_info(app_name)
        
        if app_details:
            return Process(
                pid=app_details['pid'],
                name=app_name,
                priority=random.randint(1, 3),  # 隨機優先級
                memory_required=int(app_details['memory_mb']),
                cpu_burst=random.randint(2, 5),  # 模擬執行時間
                state=ProcessState.RUNNING if app_status.get('running', False) else ProcessState.TERMINATED,
                remaining_time=random.randint(2, 5),
                memory_allocated=True
            )
        return None

    def display_status(self) -> None:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n=== macOS Dock 應用程式監控 ===")
        print(f"可用記憶體: {self.memory_manager.available_memory}MB / {self.memory_manager.total_memory}MB")
        print("\nDock 上正在執行的應用程式:")
        print("PID\t名稱\t\tCPU%\t記憶體(MB)")
        print("-" * 50)
        self.dock_monitor.update_dock_apps()
        if not self.dock_monitor.dock_apps:
            print("無法獲取 Dock 應用程式列表，請確認權限設定。")
        else:
            for app_name in self.dock_monitor.dock_apps:
                app_details = self.dock_monitor.get_app_info(app_name)
                if app_details:
                    print(f"{app_details['pid']}\t{app_name:<15}\t{app_details['cpu_percent']:.1f}%\t{app_details['memory_mb']:.1f}")
        print("\n系統資源使用:")
        print(f"CPU 使用率: {psutil.cpu_percent()}%")
        print(f"記憶體使用率: {psutil.virtual_memory().percent}%")
        print("=" * 50)

    def start(self) -> None:
        """啟動模擬器"""
        self.running = True
        print("開始監控 Dock 應用程式...")
        
        while self.running:
            try:
                self.display_status()
                time.sleep(2)  # 每 2 秒更新一次
            except KeyboardInterrupt:
                print("\n停止監控")
                self.running = False
            except Exception as e:
                print(f"\n發生錯誤: {e}")
                self.running = False

def main():
    """主程式"""
    print("啟動 Dock 應用程式監控器...")
    simulator = MultiprogrammingSimulator()
    
    try:
        simulator.start()
    except KeyboardInterrupt:
        print("\n監控器已停止")
    except Exception as e:
        print(f"\n發生錯誤: {e}")

if __name__ == "__main__":
    main() 