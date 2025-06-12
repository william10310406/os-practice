#!/usr/bin/env python3
"""
Arduino 硬體介面程式 (Arduino Hardware Interface)
功能：
1. 與 Arduino 開發板建立串口通訊
2. 控制 Arduino 上的 LED 和讀取感測器數據
3. 提供模擬模式用於測試和展示

作者：[您的名字]
版本：1.0
日期：2024

需求：
- pyserial 套件 (pip install pyserial)
- Arduino 開發板（選配，無實體硬體也可使用模擬模式）
"""

import serial     # 用於串口通訊
import time       # 用於延時操作
import json       # 用於處理 JSON 格式資料
from datetime import datetime  # 用於時間戳記

class ArduinoInterface:
    """
    Arduino 通訊介面類別
    處理與 Arduino 開發板的所有通訊操作
    """
    
    def __init__(self, port='/dev/cu.usbmodem*', baudrate=9600):
        """
        初始化 Arduino 通訊介面
        
        參數：
            port (str): Arduino 串口位置（macOS 上通常是 /dev/cu.usbmodem*）
            baudrate (int): 串口通訊速率，需要與 Arduino 程式設定相同
        """
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        
    def find_arduino_port(self):
        """
        自動尋找已連接的 Arduino 設備
        
        返回：
            str or None: 找到的 Arduino 串口位置，如果沒找到則返回 None
        """
        import glob
        # 在 macOS 上搜尋可能的 Arduino 串口
        ports = glob.glob('/dev/cu.usbmodem*') + glob.glob('/dev/cu.usbserial*')
        if ports:
            return ports[0]
        return None
    
    def connect(self):
        """
        建立與 Arduino 的連接
        
        返回：
            bool: 連接成功返回 True，失敗返回 False
        """
        try:
            if self.port == '/dev/cu.usbmodem*':
                self.port = self.find_arduino_port()
                if not self.port:
                    raise Exception("找不到 Arduino 裝置")
            
            # 建立串口連接
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # 等待 Arduino 重置完成
            print(f"✅ 成功連接到 Arduino: {self.port}")
            return True
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def disconnect(self):
        """
        關閉與 Arduino 的連接
        安全地釋放串口資源
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("🔌 已斷開 Arduino 連接")
    
    def send_command(self, command):
        """
        向 Arduino 發送指令
        
        參數：
            command (str): 要發送的指令
            
        返回：
            str or None: Arduino 的回應，如果發送失敗則返回 None
        """
        if not self.connection or not self.connection.is_open:
            print("❌ 未連接到 Arduino")
            return None
        
        try:
            # 發送指令並等待回應
            self.connection.write(f"{command}\n".encode())
            time.sleep(0.1)  # 給 Arduino 處理時間
            
            # 讀取 Arduino 回應
            if self.connection.in_waiting:
                response = self.connection.readline().decode().strip()
                return response
        except Exception as e:
            print(f"❌ 通訊錯誤: {e}")
        return None
    
    def read_sensor_data(self):
        """
        讀取 Arduino 感測器資料
        
        返回：
            dict: 包含感測器數據的字典，格式取決於 Arduino 程式的實作
        """
        response = self.send_command("READ_SENSORS")
        if response:
            try:
                # 嘗試解析 JSON 格式的感測器資料
                return json.loads(response)
            except:
                return {"raw_data": response}
        return None
    
    def control_led(self, state):
        """
        控制 Arduino 上的 LED
        
        參數：
            state (bool): True 開啟 LED，False 關閉 LED
            
        返回：
            bool: 操作是否成功
        """
        command = "LED_ON" if state else "LED_OFF"
        response = self.send_command(command)
        return response == "OK"
    
    def read_temperature(self):
        """
        讀取溫度感測器數據
        
        返回：
            float or None: 溫度值（攝氏度），讀取失敗返回 None
        """
        response = self.send_command("GET_TEMP")
        if response and response.replace('.', '').replace('-', '').isdigit():
            return float(response)
        return None

def demo_arduino_without_hardware():
    """
    Arduino 功能演示（模擬模式）
    不需要實際的 Arduino 硬體即可運行
    用於測試和展示目的
    """
    print("🔧 Arduino 硬體介面演示 (模擬模式)")
    print("=" * 50)
    
    # 使用隨機數據模擬感測器讀數
    import random
    
    for i in range(10):
        timestamp = datetime.now().strftime("%H:%M:%S")
        temp = round(random.uniform(20, 30), 1)      # 模擬溫度 20-30°C
        humidity = round(random.uniform(40, 80), 1)  # 模擬濕度 40-80%
        light = random.randint(0, 1023)              # 模擬光感數值 0-1023
        
        # 顯示模擬數據
        print(f"⏰ {timestamp}")
        print(f"🌡️  溫度: {temp}°C")
        print(f"💧 濕度: {humidity}%")
        print(f"💡 光感: {light}")
        print("-" * 30)
        time.sleep(2)

def main():
    """
    主程式入口
    提供使用者介面和功能選單
    """
    print("Arduino 硬體介面選項:")
    print("1. 連接真實 Arduino (需要硬體)")
    print("2. 模擬演示 (無需硬體)")
    
    choice = input("\n請選擇 (1-2): ").strip()
    
    if choice == "1":
        # 建立 Arduino 連接並進入互動模式
        arduino = ArduinoInterface()
        
        if arduino.connect():
            try:
                print("\n🎮 Arduino 控制介面")
                print("指令: 'led on/off', 'temp', 'sensors', 'quit'")
                
                while True:
                    cmd = input("\n> ").strip().lower()
                    
                    # 處理使用者指令
                    if cmd == "quit":
                        break
                    elif cmd == "led on":
                        if arduino.control_led(True):
                            print("💡 LED 已開啟")
                        else:
                            print("❌ LED 控制失敗")
                    elif cmd == "led off":
                        if arduino.control_led(False):
                            print("💡 LED 已關閉")
                        else:
                            print("❌ LED 控制失敗")
                    elif cmd == "temp":
                        temp = arduino.read_temperature()
                        if temp is not None:
                            print(f"🌡️ 溫度: {temp}°C")
                        else:
                            print("❌ 無法讀取溫度")
                    elif cmd == "sensors":
                        data = arduino.read_sensor_data()
                        if data:
                            print("📊 感測器資料:")
                            print(json.dumps(data, indent=2, ensure_ascii=False))
                        else:
                            print("❌ 無法讀取感測器")
                    else:
                        print("❓ 未知指令")
                        
            except KeyboardInterrupt:
                print("\n\n👋 結束程式")
            finally:
                arduino.disconnect()
        else:
            print("💡 提示: 請確認 Arduino 已連接並安裝驅動程式")
            
    elif choice == "2":
        demo_arduino_without_hardware()
    
    else:
        print("❌ 無效選擇")

# Arduino 程式碼參考 (需要上傳到 Arduino 板子)
arduino_code_example = '''
/*
對應的 Arduino 程式碼範例
此程式需要上傳到 Arduino 開發板才能與 Python 程式互動

功能：
1. 控制板載 LED (Pin 13)
2. 模擬溫度感測器讀數
3. 回傳 JSON 格式的感測器資料

作者：[您的名字]
日期：2024
*/

void setup() {
  Serial.begin(9600);        // 設定串口通訊速率
  pinMode(13, OUTPUT);       // 設定 LED 腳位為輸出模式
}

void loop() {
  if (Serial.available()) {  // 檢查是否有新指令
    String command = Serial.readString();
    command.trim();          // 移除多餘空白
    
    // 處理 LED 控制指令
    if (command == "LED_ON") {
      digitalWrite(13, HIGH);
      Serial.println("OK");
    }
    else if (command == "LED_OFF") {
      digitalWrite(13, LOW);
      Serial.println("OK");
    }
    // 處理溫度讀取指令
    else if (command == "GET_TEMP") {
      // 這裡使用模擬數據，實際應用中應該讀取真實感測器
      float temp = 25.6;
      Serial.println(temp);
    }
    // 處理所有感測器讀取指令
    else if (command == "READ_SENSORS") {
      // 回傳 JSON 格式的感測器資料
      Serial.println("{\\"temp\\": 25.6, \\"humidity\\": 60.2, \\"light\\": 512}");
    }
  }
  delay(100);  // 短暫延遲以避免 CPU 過載
}
*/
'''

if __name__ == "__main__":
    main()
    print("\n" + arduino_code_example) 