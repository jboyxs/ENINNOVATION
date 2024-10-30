import numpy as np
import cv2
import time
import json
import os

# 全局变量，用于存储点击的点
calibration_points = []

def nothing(x):
    pass

def mouse_click(event, x, y, flags, param):
    """
    鼠标回调函数，用于记录用户点击的四个定标点
    """
    global calibration_points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(calibration_points) < 4:
            calibration_points.append((x, y))
            print(f"点{len(calibration_points)}: ({x}, {y})")
        else:
            print("已经选择了四个点，不需要更多点击。")

def get_ball_position(frame):
    """
    通过颜色检测获取小球在帧中的位置
    :param frame: 输入的图像帧
    :return: 小球的(x, y)坐标，如果未检测到则返回(None, None)
    """
    # 转换为HSV色彩空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义小球的颜色范围（以红色为例，需要根据实际情况调整）
    # 红色在HSV空间中分布在两个区域
    lower_color1 = np.array([0, 100, 100])
    upper_color1 = np.array([10, 255, 255])
    lower_color2 = np.array([160, 100, 100])
    upper_color2 = np.array([180, 255, 255])

    # 创建颜色掩码
    mask1 = cv2.inRange(hsv, lower_color1, upper_color1)
    mask2 = cv2.inRange(hsv, lower_color2, upper_color2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 进行形态学操作，去除噪声
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 找到最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        # 计算轮廓的最小外接圆
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
        if radius > 10:  # 过滤掉太小的噪声
            return int(x), int(y)

    return None, None

def calibrate_platform(cap):
    """
    通过用户在图像上点击四个顶点进行平台定标，计算裁剪区域
    :param cap: 视频捕捉对象
    :return: 裁剪区域的四个顶点，如果定标未完成则返回None
    """
    global calibration_points
    print("开始平台定标，请在图像上点击平台的四个顶点。")

    # 创建一个窗口并设置鼠标回调
    cv2.namedWindow('calibration')
    cv2.setMouseCallback('calibration', mouse_click)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧。")
            break

        # 绘制已点击的点
        for idx, point in enumerate(calibration_points):
            cv2.circle(frame, point, 5, (0, 255, 0), -1)
            cv2.putText(frame, f"{idx+1}", (point[0] + 10, point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 如果已经选择了四个点，提示用户按下 's' 键保存定标或 'c' 键重新选择
        if len(calibration_points) == 4:
            cv2.putText(frame, "Press 's' to save calibration or 'c' to reset.", 
                        (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow('calibration', frame)
        key = cv2.waitKey(1) & 0xFF

        if len(calibration_points) == 4:
            if key == ord('s') or key == ord('S'):
                # 保存定标点
                with open('calibration_points.json', 'w') as f:
                    json.dump(calibration_points, f)
                print("定标完成，定标点已保存。")
                break  # 退出定标循环

            elif key == ord('c') or key == ord('C'):
                calibration_points = []
                print("重新选择四个点。")

        if key == ord('q') or key == ord('Q'):
            print("定标已取消。")
            break

    cv2.destroyWindow('calibration')

    if len(calibration_points) == 4:
        return calibration_points  # 返回定标点
    else:
        return None

def apply_calibration(frame, matrix):
    """
    应用透视变换到图像
    :param frame: 输入的图像帧
    :param matrix: 透视变换矩阵
    :return: 变换后的图像
    """
    target_width, target_height = 800, 600  # 定标时使用的目标尺寸
    calibrated_frame = cv2.warpPerspective(frame, matrix, (target_width, target_height))
    return calibrated_frame

def load_calibration():
    """
    加载已保存的透视变换矩阵
    :return: 透视变换矩阵，如果文件不存在则返回None
    """
    if os.path.exists('calibration_matrix.json'):
        with open('calibration_matrix.json', 'r') as f:
            matrix = np.array(json.load(f), dtype=np.float32)
        print("加载现有的定标矩阵。")
        return matrix
    else:
        print("未找到定标矩阵，需要进行定标。")
        return None

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头。")
        return

    cv2.namedWindow('color')
    cv2.setMouseCallback('color', mouse_click)

    # 创建控制窗口和滑动条
    cv2.namedWindow('controls')
    cv2.createTrackbar('GaussianBlur', 'controls', 1, 20, nothing)
    cv2.createTrackbar('CannyMin', 'controls', 50, 255, nothing)
    cv2.createTrackbar('CannyMax', 'controls', 150, 255, nothing)
    cv2.createTrackbar('BilateralD', 'controls', 1, 20, nothing)
    cv2.createTrackbar('SigmaColor', 'controls', 1, 100, nothing)
    cv2.createTrackbar('SigmaSpace', 'controls', 1, 100, nothing)

    # 尝试加载定标矩阵
    calibration_matrix = load_calibration()
    if calibration_matrix is None:
        # 平台定标
        calibration_matrix = calibrate_platform(cap)
        if calibration_matrix is None:
            print("定标未完成，程序退出。")
            cap.release()
            cv2.destroyAllWindows()
            return

    # 初始化 last_time 和 last_position
    last_time = None
    last_position = None

    # 继续进行小球识别和控制逻辑
    while True:
        ret, color_frame = cap.read()
        if not ret:
            print("无法读取摄像头帧。")
            break

        # 应用透视变换
        calibrated_frame = apply_calibration(color_frame, calibration_matrix)

        # 获取小球的当前坐标
        current_x, current_y = get_ball_position(calibrated_frame)

        if current_x is not None and current_y is not None:
            # 在图像上标记小球的位置
            cv2.circle(calibrated_frame, (current_x, current_y), 10, (255, 0, 0), 2)
            print(f"小球位置: ({current_x}, {current_y})")
        else:
            print("未检测到小球")

        # 其余的图像处理和显示逻辑
        gray_frame = cv2.cvtColor(calibrated_frame, cv2.COLOR_BGR2GRAY)

        # 获取滑动条的值
        blur_value = cv2.getTrackbarPos('GaussianBlur', 'controls')
        canny_min = cv2.getTrackbarPos('CannyMin', 'controls')
        canny_max = cv2.getTrackbarPos('CannyMax', 'controls')
        bilateral_d = cv2.getTrackbarPos('BilateralD', 'controls')
        sigma_color = cv2.getTrackbarPos('SigmaColor', 'controls')
        sigma_space = cv2.getTrackbarPos('SigmaSpace', 'controls')

        # 确保模糊值为奇数
        if blur_value % 2 == 0:
            blur_value += 1

        # 应用双边滤波
        bilateral_frame = cv2.bilateralFilter(gray_frame, bilateral_d, sigma_color, sigma_space)

        # 应用高斯模糊
        blurred_frame = cv2.GaussianBlur(bilateral_frame, (blur_value, blur_value), 2)
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
                    cv2.rectangle(calibrated_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.circle(calibrated_frame, center, 5, (0, 255, 0), -1)

                    current_time = time.time()

                    if last_time is not None:
                        time_diff = current_time - last_time
                        print(f"Time since last detection: {time_diff:.4f} seconds")
                        if last_position is not None:
                            print(f"Previous Ball Position: {last_position}, Current Ball Position: {center}")
                            print(f"Time between detections: {time_diff:.4f} seconds\n")
                    last_time = current_time
                    last_position = center

                    print(f"Ball detected at: ({center[0]}, {center[1]})")

        cv2.imshow('calibrated', calibrated_frame)
        cv2.imshow('edges', edges)

        key = cv2.waitKey(1)
        if key == ord('q') or key == ord('Q'):
            print("程序已退出。")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()