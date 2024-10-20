import serial
# 后面要整合到大程序之中
# 蓝牙串口设备名称（根据实际情况修改）
bluetooth_port = 'COMX'  # 例如 'COM5'

# 打开蓝牙串口连接
ser = serial.Serial(bluetooth_port, baudrate=9600, timeout=1)

# 假设从另一个运行的 Python 代码获取数据的函数
def get_data_from_other_code():
    return "Some data"

while True:
    data = get_data_from_other_code()
    ser.write(data.encode())
    # 可以添加一些延迟，避免过于频繁地发送数据
    import time
    time.sleep(1)