from openni import openni2
from openni import _openni2 as c_api
import numpy as np
import cv2
import time

depth_width = 640
depth_height = 480

# 设置深度阈值，以筛选小球
DEPTH_THRESHOLD = 300  # 设定一个深度阈值，单位为毫米

def mousecallback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(f"Depth at ({y}, {x}): {dpt[y, x]} mm")

if __name__ == "__main__":
    openni2.initialize()

    dev = openni2.Device.open_any()
    print(dev.get_device_info())
    
    # 创建一个深度数据流对象
    depth_stream = dev.create_depth_stream()
    print(depth_stream.get_video_mode())

    # 设置深度数据流的视频模式
    depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX=depth_width, resolutionY=depth_height, fps=30))
    depth_stream.start()

    # 打开视频捕获设备，使用第二个摄像头（如有多个）
    cap = cv2.VideoCapture(0)
    
    # 创建窗口
    cv2.namedWindow('depth')
    cv2.setMouseCallback('depth', mousecallback)

    last_time = None  # 记录上一次检测到小球的时间
    last_position = None  # 记录上一次检测到小球的坐标

    while True:
        # 从深度数据流中读取一帧数据
        frame = depth_stream.read_frame()

        # 从深度帧中获取原始数据，并将其转换为一个形状为 (depth_height, depth_width, 2) 的三维数组
        dframe_data = np.array(frame.get_buffer_as_triplet()).reshape([depth_height, depth_width, 2])
        dpt1 = np.asarray(dframe_data[:, :, 0], dtype='float32')
        dpt2 = np.asarray(dframe_data[:, :, 1], dtype='float32')

        dpt2 = dpt2 * 255
        dpt = dpt1 + dpt2
        dpt = dpt[:, ::-1]

        # 将深度图转换为8位灰度图（标准化处理以便于边缘检测）
        dpt_normalized = cv2.normalize(dpt, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # 滤波部分已被注释
        # 1. 高斯滤波 (Gaussian Blur)
        # dpt_filtered = cv2.GaussianBlur(dpt_normalized, (3, 3), 1)  # 内核尺寸为 3x3，标准差为 1

        # 2. 双边滤波 (Bilateral Filter)
        # dpt_filtered = cv2.bilateralFilter(dpt_normalized, 5, 50, 50)  # 内核为5，空间距离为50，颜色距离为50

        # 因为滤波部分被注释掉，直接使用归一化后的深度图
        dpt_filtered = dpt_normalized

        # Canny边缘检测
        edges = cv2.Canny(dpt_filtered, 30, 100)  # 低阈值为30，高阈值为100

        # 使用形态学操作来填充边缘
        kernel = np.ones((3, 3), np.uint8)  # 内核为 3x3
        edges_dilated = cv2.dilate(edges, kernel, iterations=1)

        # 找到轮廓
        contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 在深度图和彩色图上绘制检测到的小球
        ret, color_frame = cap.read()

        for cnt in contours:
            # 计算轮廓的面积并过滤小面积和大面积的轮廓
            area = cv2.contourArea(cnt)
            if 150 < area < 900:  # 优化面积阈值，适应具体情况
                # 计算小球的边界框和中心点
                (x, y, w, h) = cv2.boundingRect(cnt)
                center = (x + w // 2, y + h // 2)

                # 计算轮廓中心的深度值
                depth_at_center = dpt[y + h // 2, x + w // 2]  # 获取中心点的深度值

                # 筛选出符合深度阈值的小球
                if depth_at_center < DEPTH_THRESHOLD:
                    # 计算圆度，使用更高的圆度阈值，确保物体为圆形
                    perimeter = cv2.arcLength(cnt, True)
                    circularity = 4 * np.pi * (area / (perimeter ** 2)) if perimeter > 0 else 0

                    if circularity > 0.8:  # 调整圆度阈值
                        # 在深度图上绘制更明显的边框
                        color = (0, 0, 255)  # 红色边框
                        thickness = 2  # 边框厚度
                        cv2.rectangle(dpt_filtered, (x, y), (x + w, y + h), color, thickness)
                        cv2.circle(dpt_filtered, center, 5, (0, 255, 0), -1)  # 绘制中心点

                        # 在彩色图上绘制边框
                        cv2.rectangle(color_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.circle(color_frame, center, 5, (0, 0, 255), -1)  # 绘制中心点

                        # 获取当前时间
                        current_time = time.time()

                        # 如果上次检测到小球的时间不为空，则计算时间差并输出
                        if last_time is not None:
                            time_diff = current_time - last_time
                            print(f"Time since last detection: {time_diff:.4f} seconds")
                        
                            # 打印两个位置之间的时间差和坐标
                            if last_position is not None:
                                print(f"Previous Ball Position: {last_position}, Current Ball Position: {center}")
                                print(f"Time between detections: {time_diff:.4f} seconds\n")
                        
                        # 更新上一次检测到小球的时间和位置
                        last_time = current_time
                        last_position = center

                        # 打印小球的中心坐标和深度
                        print(f"Ball detected at: ({center[0]}, {center[1]}) with depth: {depth_at_center} mm")

        # 显示结果
        cv2.imshow('depth', dpt_filtered)  # 显示滤波后的深度图和明显的边框
        cv2.imshow('color', color_frame)

        # 按 'q' 键退出
        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    depth_stream.stop()
    dev.close()
