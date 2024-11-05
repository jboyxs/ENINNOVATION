import serial
import serial.tools.list_ports

def send_bluetooth_data_multiple(data_list, port='COM3', baudrate=9600):
    """
    通过蓝牙串口同时发送多个数据给 STM32 单片机。

    参数:
        data_list (list): 要发送的字符串数据列表，例如 ["data1", "data2", ..., "data6"]。
        port (str): 串口端口名称，默认为 'COM3'。
        baudrate (int): 波特率，默认为 9600。
    """
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            for data in data_list:
                ser.write(data.encode('utf-8') + b'\n')  # 添加换行符分隔数据
                print(f"已发送数据: {data}")
    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except Exception as e:
        print(f"发送数据时发生错误: {e}")

# 使用示例
if __name__ == "__main__":
    messages = ["Data1", "Data2", "Data3", "Data4", "Data5", "Data6"]
    send_bluetooth_data_multiple(messages, port='COM5', baudrate=115200)