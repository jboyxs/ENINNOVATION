import numpy as np
import cv2
import time
from lock_17.pidchanged import PID as pid
from lock_17 import link as link
from lock_17 import guide as gu
from resolve import gongchuang as re

depth_width = 640
depth_height = 480

def nothing(x):
    pass

def detect_ball(roi, last_time, last_position):
    gray_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 获取滑动条的值
    # blur_value = cv2.getTrackbarPos('GaussianBlur', 'controls')
    blur_value = 4
    # canny_min = cv2.getTrackbarPos('CannyMin', 'controls')
    canny_min = 45
    # canny_max = cv2.getTrackbarPos('CannyMax', 'controls')
    canny_max=140

    # 确保模糊值为奇数
    if blur_value % 2 == 0:
        blur_value += 1

    blurred_frame = cv2.GaussianBlur(gray_frame, (blur_value, blur_value), 2)
    edges = cv2.Canny(blurred_frame, canny_min, canny_max)
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=2)
    contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 150 < area < 900:
            (x, y, w, h) = cv2.boundingRect(cnt)
            center = (x + w // 2, y + h // 2)

            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * np.pi * (area / (perimeter ** 2)) if perimeter > 0 else 0

            if circularity > 0.8:
                color = (0, 0, 255)
                thickness = 2
                cv2.rectangle(roi, (x, y), (x + w, y + h), color, thickness)
                cv2.circle(roi, center, 5, (0, 255, 0), -1)

                current_time = time.time()

                if last_time is not None:
                    time_diff = current_time - last_time
                    print(f"时间差: {time_diff:.4f} 秒")
                    if last_position is not None:
                        print(f"上次位置: {last_position}, 当前位: {center}")
                        print(f"检测间隔: {time_diff:.4f} 秒\n")
                last_time = current_time
                last_position = center

                print(f"检测到小球: ({center[0]}, {center[1]})")

    return last_time, last_position, edges

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('color')

    # 创建窗口和滑动条
    cv2.namedWindow('controls')
    cv2.createTrackbar('GaussianBlur', 'controls', 1, 20, nothing)
    cv2.createTrackbar('CannyMin', 'controls', 50, 255, nothing)
    cv2.createTrackbar('CannyMax', 'controls', 150, 255, nothing)

    last_time = None
    last_position = None
    # pid_init
    setpoint_xo=318
    setpoint_yo=204
    setpoint_x=setpoint_xo
    setpoint_y=setpoint_yo
    pid_x = pid(0.27, 0., 400, setpoint_x)
    pid_y = pid(0.27, 0., 400, setpoint_y)
    # link_init
    port="COM6"
    ser=link.connect_to_stm32(port,384000)
while True:
    ret, color_frame = cap.read()
    if not ret:
        break

    roi = color_frame

    # 调用检测函数
    last_time, last_position, edges = detect_ball(roi, last_time, last_position)
    # 检查 last_position 是否为 None
    if last_position is not None:
        # pid
        center_x, center_y = last_position
        # 修改setpoint
        [setpoint_x,setpoint_y]=gu.gnposition((setpoint_xo,setpoint_yo),(center_x,center_y))
        # 每次更新的时候先改setpoint
        pid_x = pid(0.01, 0.001, 17, setpoint_x)
        pid_y = pid(0.01, 0.001, 17, setpoint_y)
        angle_x = pid_x.update(center_x)
        angle_y = pid_y.update(center_y)
        # resolve 反解
        angle__6 = re.calculate_inverse_kinematics(angle_x, angle_y)
        if angle__6 is not None:
            angle__6 = [int(angle) for angle in angle__6]
            # link
            link.send_data(ser,angle__6)
    else:
        print("未检测到小球，跳过当前帧处理。")
        zero_data = [0, 0, 0, 0, 0, 0]
        # 发送全零数据给单片机
        link.send_data(ser, zero_data)

    cv2.imshow('color', color_frame)
    cv2.imshow('edges', edges)

    key = cv2.waitKey(1)
    if int(key) == ord('q'):
        break