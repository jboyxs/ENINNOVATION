import serial
import serial.tools.list_ports

def list_available_ports():
    """列出所有可用的串口"""
    ports = serial.tools.list_ports.comports()
    available_ports = [port.device for port in ports]
    return available_ports

def connect_to_stm32(port, baudrate=384000, timeout=1):
    """连接到 STM32 单片机"""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"已连接到 {port}")
        return ser
    except serial.SerialException as e:
        print(f"连接串口时发生错误: {e}")
        return None

def send_data(ser, data_list):
    """发送数据到 STM32 单片机并接收返回值"""
    if ser is not None:
        try:
            # 将每个整数转换为4位字符串，前导补0，并拼接成一个完整的字符串
            data_str = ''.join(f"{int(data):04d}" for data in data_list)
            ser.write(data_str.encode('utf-8'))
            print(f"已发送数据: {data_str}")
            
            # 接收单片机返回值
            #response = ser.readline().decode('utf-8').strip()
            #print(f"单片机返回的数据: {response}")
            #return response

        except serial.SerialException as e:
            print(f"发送数据时发生错误: {e}")
            return None
        
    else:
        print("无法发送数据，串口未连接。")
        return None

if __name__ == "__main__":
    import serial
    import serial.tools.list_ports

   

    # 列出所有可用的串口
    available_ports = list_available_ports()
    print("可用的串口：", available_ports)

    # 连接到 STM32 单片机
    port = 'COM6'  # 根据实际情况修改端口号
    ser = connect_to_stm32(port, baudrate=384000)

    # 发送数据并接收返回值
    data_to_send = [0, 0, 0, 0, 0, 0]  # 确保数据是整数列表
    response = send_data(ser, data_to_send)
    print("接收到的返回值:", response)