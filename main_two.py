import os
import psutil
import numpy as np
import cv2
import time
import threading
import queue
from lock_17.pidchanged_three import PID  # 更新后的 PID 类
from lock_17 import link as link
from lock_17 import guide as gu
from resolve import gongchuang2 as re

# 设置队列大小
FRAME_QUEUE_SIZE = 10
DISPLAY_QUEUE_SIZE = 10

# 初始化队列
frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
display_queue = queue.Queue(maxsize=DISPLAY_QUEUE_SIZE)

# 定义共享变量和锁
latest_position = None
position_lock = threading.Lock()

# 定义停止信号
stop_event = threading.Event()

def set_thread_priority(thread, priority):
    """
    设置进程的优先级（注意：Python不支持单独设置线程优先级）。
    这里设置整个进程的优先级。
    
    :param thread: 线程对象（未使用，因为无法单独设置线程优先级）
    :param priority: 优先级常量，参考psutil文档
    """
    p = psutil.Process(os.getpid())
    try:
        p.nice(priority)
        print(f"进程优先级已设置为 {priority}")
    except AttributeError:
        print("设置线程优先级失败，该平台可能不支持。")

def detect_ball(roi, last_time, last_position, lower_blue, upper_blue):
    """
    检测ROI中的蓝色小球，并返回更新后的时间、位置和处理结果。

    :param roi: 感兴趣区域图像
    :param last_time: 上一次检测到小球的时间
    :param last_position: 上一次检测到小球的位置
    :param lower_blue: 蓝色下限HSV
    :param upper_blue: 蓝色上限HSV
    :return: (last_time, last_position, mask)
    """
    # 转换为 HSV 颜色空间
    hsv_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # 根据 HSV 范围创建遮罩
    mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 150 < area < 900:  # 限制轮廓的面积
            (x, y, w, h) = cv2.boundingRect(cnt)
            center = (x + w // 2, y + h // 2)

            # 计算轮廓的圆形度
            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * np.pi * (area / (perimeter ** 2)) if perimeter > 0 else 0

            # 检测到蓝色且形状接近圆形
            if circularity > 0.8:
                # 只在检测逻辑中记录信息，不进行绘制
                current_time = time.time()
                if last_time is not None:
                    time_diff = current_time - last_time
                    print(f"时间差: {time_diff:.4f} 秒")
                    if last_position is not None:
                        print(f"上次位置: {last_position}, 当前位: {center}")
                        print(f"检测间隔: {time_diff:.4f} 秒\n")
                last_time = current_time
                last_position = center

                print(f"检测到蓝色小球: ({center[0]}, {center[1]})")
                detected = True
                break  # 只检测第一个符合条件的轮廓

    if not detected:
        print("未检测到小球")
        
    return last_time, last_position, mask

def frame_capture():
    """捕获视频帧并放入帧队列"""
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("无法从摄像头读取帧")
            break
        try:
            frame_queue.put(frame, timeout=1)
        except queue.Full:
            print("帧队列已满，丢弃帧")
            continue
    stop_event.set()

def frame_processing():
    """处理视频帧并更新最新的位置"""
    lower_blue = np.array([16, 82, 142])
    upper_blue = np.array([161, 255, 255])

    last_time = None
    last_position = None

    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        roi = frame  # 可根据需要修改感兴趣区域

        # 调用检测函数
        updated_time, updated_position, mask = detect_ball(roi, last_time, last_position, lower_blue, upper_blue)

        # 更新状态
        last_time = updated_time
        last_position = updated_position

        try:
            display_queue.put((frame, mask), timeout=1)
        except queue.Full:
            print("显示队列已满，丢弃处理结果")
            pass

        # 更新共享变量
        if updated_position is not None:
            with position_lock:
                global latest_position
                latest_position = updated_position

def data_communication():
    """处理PID控制和数据发送，基于共享变量"""
    # 定义目标点列表
    list_of_targets = [
       
         (331,145),
        #  (347,208),
        (382,271),
        (398,261),
        (413,251),
        (409,278),
        (424,304),
        (439,330),
        (454,328),
        # (422,357),
        (390,330),
        #  (358,331),
        (325,331),
        (293,332),
        (260,333),
        (228,334),
        (195,334),
        (212,335),
        (229,308),
        (246,281),
        (263,254),
        (280,227),
        (297,200),
        (314,173),
        (331,145)]
    current_target_index = 0  # 当前目标点索引

    # 设置初始目标点
    setpoint_x, setpoint_y = list_of_targets[current_target_index]
    pid_x = PID(0.01, 0.0016, 1.1, setpoint_x)
    pid_y = PID(0.01, 0.0019, 1.1, setpoint_y)

    port = "COM6"
    ser = link.connect_to_stm32(port, 384000)

    distance_threshold =47 # 定义一个距离阈值，当小球距离目标点小于此值时认为到达

    while not stop_event.is_set():
        with position_lock:
            current_position = latest_position

        if current_position is not None:
            center_x, center_y = current_position
            # 更新 PID 控制
            angle_x = pid_x.update(center_x)
            angle_y = pid_y.update(center_y)
            # 逆运动学计算
            angle__6 = re.calculate_inverse_kinematics(angle_x, angle_y)
            if angle__6 is not None:
                angle__6 = [int(angle) for angle in angle__6]
                # 发送数据
                link.send_data(ser, angle__6)

                # 检查是否到达当前目标点
                target_x, target_y = list_of_targets[current_target_index]
                distance = np.sqrt((center_x - target_x) ** 2 + (center_y - target_y) ** 2)
                if distance < distance_threshold:
                    print(f"已到达目标点: ({target_x}, {target_y})")
                    # 更新到下一个目标点
                    current_target_index += 1
                    if current_target_index >= len(list_of_targets):
                        current_target_index = 0  # 如果到达最后一个目标点，重新开始循环
                        print("所有目标点已完成，重新开始路径规划。")
                    # 更新PID控制器的目标点
                    setpoint_x, setpoint_y = list_of_targets[current_target_index]
                    pid_x.set_point(setpoint_x)
                    pid_y.set_point(setpoint_y)
                    print(f"下一个目标点: ({setpoint_x}, {setpoint_y})")
        else:
            print("未检测到小球，跳过当前帧处理。")
        
        # 为了避免过度占用CPU，设置适当的睡眠时间
        time.sleep(0.01)  # 10ms，可根据需要调整

def display_frames():
    """显示处理后的帧"""
    while not stop_event.is_set():
        try:
            frame, mask = display_queue.get(timeout=1)
        except queue.Empty:
            continue

        cv2.imshow('color', frame)
        cv2.imshow('edges', mask)

        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            stop_event.set()
            break

def main():
    """主函数，启动所有线程"""
    global cap

    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()

    # 创建显示窗口
    cv2.namedWindow('color')
    cv2.namedWindow('edges')

    # 启动捕获线程
    capture_thread = threading.Thread(target=frame_capture, daemon=True)
    capture_thread.start()

    # 启动处理线程
    processing_thread = threading.Thread(target=frame_processing, daemon=True)
    processing_thread.start()

    # 启动通信线程
    communication_thread = threading.Thread(target=data_communication, daemon=True)
    communication_thread.start()

    # 设置进程优先级（无法单独设置线程优先级）
    set_thread_priority(communication_thread, psutil.HIGH_PRIORITY_CLASS)

    # 启动显示线程（主线程）
    display_frames()

    # 等待所有线程结束
    capture_thread.join()
    processing_thread.join()
    communication_thread.join()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()