import serial
import time

# 设置蓝牙虚拟串口，替换为你的蓝牙模块对应的串口
# 在 Windows 上可能是 'COMx'，在 Linux 上可能是 '/dev/rfcomm0'
bluetooth_port = 'COM5'  # 修改为你的虚拟串口
baud_rate = 9600  # 通信波特率，需与 STM32 上的蓝牙模块波特率匹配

# 初始化串口通信
def init_serial_connection():
    try:
        ser = serial.Serial(bluetooth_port, baud_rate, timeout=1)
        print(f"成功连接到蓝牙串口: {bluetooth_port} @ {baud_rate}bps")
        return ser
    except serial.SerialException as e:
        print(f"无法连接到蓝牙串口: {e}")
        return None

# 发送数据
def send_data(ser, data):
    if ser.is_open:
        ser.write(data.encode())  # 将字符串编码为字节并发送
        print(f"发送数据: {data}")
    else:
        print("串口未打开，无法发送数据")

# 接收数据
def receive_data(ser):
    if ser.is_open:
        data = ser.readline().decode('utf-8').strip()  # 读取一行数据
        if data:
            print(f"接收到的数据: {data}")
            return data
        else:
            return None
    else:
        print("串口未打开，无法接收数据")
        return None

# 主程序
if __name__ == '__main__':
    ser = init_serial_connection()
    
    if ser:
        try:
            while True:
                # 示例: 发送数据
                send_data(ser, "Hello STM32")
                
                # 示例: 接收 STM32 的返回数据
                received = receive_data(ser)
                
                if received:
                    print(f"STM32 发送的数据: {received}")
                
                time.sleep(1)  # 每隔 1 秒发送一次
        except KeyboardInterrupt:
            print("用户中断程序")
        finally:
            if ser.is_open:
                ser.close()
                print("串口已关闭")
