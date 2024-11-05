import numpy as np
import cv2
import time
from lock_17 import pid71 as pid
from lock_17 import my_bluetooth as bt
from resolve import gongchuang as re

depth_width = 640
depth_height = 480

def nothing(x):
    pass

def detect_ball(roi, last_time, last_position):
    gray_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 获取滑动条的值
    blur_value = cv2.getTrackbarPos('GaussianBlur', 'controls')
    canny_min = cv2.getTrackbarPos('CannyMin', 'controls')
    canny_max = cv2.getTrackbarPos('CannyMax', 'controls')

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

    while True:
        ret, color_frame = cap.read()
        if not ret:
            break

        roi = color_frame

        # 调用检测函数
        last_time, last_position, edges = detect_ball(roi, last_time, last_position)
        # pid
        center_x, center_y = last_position
        angle_x=pid.update(center_x)
        angle_y=pid.update(center_y)
        #resolve反解
        pwm__6=re.calculate_inverse_kinematics(angle_x, angle_y)
        #bluetooth
        bt.send_bluetooth_data_multiple(pwm__6, port='COM5', baudrate=9600)


        cv2.imshow('color', color_frame)
        cv2.imshow('edges', edges)

        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()