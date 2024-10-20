from openni import openni2
from openni import _openni2 as c_api
import numpy as np
import cv2
import time
import matplotlib.pyplot as plt

depth_width = 640
depth_height = 480

# 设置深度阈值，以筛选小球
DEPTH_THRESHOLD = 1000  # 深度阈值，单位为毫米

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
    depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX=depth_width, resolutionY=depth_height, fps=60))
    depth_stream.start()

    # 打开视频捕获设备，使用第一个摄像头
    cap = cv2.VideoCapture(0)
    
    # 创建窗口
    cv2.namedWindow('depth')
    cv2.setMouseCallback('depth', mousecallback)

    last_time = None  # 记录上一次检测到小球的时间
    last_position = None  # 记录上一次检测到小球的坐标

    frame_times = []  # 存储每帧的时间戳
    frame_rates = []  # 存储每帧的帧率

    # 追踪器初始化
    tracker = None
    ball_bbox = None  # 记录小球的边界框
    tracking = False  # 是否在追踪状态

    while True:
        start_time = time.time()  # 记录帧开始时间

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

        # 1. 应用高斯滤波 (Gaussian Blur)
        dpt_filtered = cv2.GaussianBlur(dpt_normalized, (3, 3), 1)

        # 2. 应用双边滤波 (Bilateral Filter)
        dpt_filtered = cv2.bilateralFilter(dpt_filtered, 5,50, 50)

        # Canny边缘检测
        edges = cv2.Canny(dpt_filtered, 50, 150)

        # 使用形态学操作来填充边缘
        kernel = np.ones((7, 7), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel, iterations=2)

        # 找到轮廓
        contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 从摄像头读取彩色图像
        ret, color_frame = cap.read()

        if tracking and tracker is not None:
            # 如果追踪状态处于激活，则更新追踪器位置
            success, ball_bbox = tracker.update(color_frame)
            if success:
                # 追踪成功，绘制追踪的边界框
                p1 = (int(ball_bbox[0]), int(ball_bbox[1]))
                p2 = (int(ball_bbox[0] + ball_bbox[2]), int(ball_bbox[1] + ball_bbox[3]))
                cv2.rectangle(color_frame, p1, p2, (255, 0, 0), 2, 1)
                cv2.circle(color_frame, (p1[0] + ball_bbox[2] // 2, p1[1] + ball_bbox[3] // 2), 5, (0, 0, 255), -1)
            else:
                # 追踪失败，重置追踪器
                tracking = False
                tracker = None

        if not tracking:
            # 如果没有激活追踪器，进行小球检测
            for cnt in contours:
                # 计算轮廓的面积并过滤小面积和大面积的轮廓
                area = cv2.contourArea(cnt)
                if 150 < area < 900:
                    # 计算小球的边界框和中心点
                    (x, y, w, h) = cv2.boundingRect(cnt)
                    center = (x + w // 2, y + h // 2)

                    # 计算轮廓中心的深度值
                    depth_at_center = dpt[y + h // 2, x + w // 2]

                    # 筛选出符合深度阈值的小球
                    if depth_at_center < DEPTH_THRESHOLD:
                        perimeter = cv2.arcLength(cnt, True)
                        circularity = 4 * np.pi * (area / (perimeter ** 2)) if perimeter > 0 else 0

                        if circularity > 0.8:
                            # 初始化追踪器
                            ball_bbox = (x, y, w, h)
                            tracker = cv2.TrackerKCF_create()  # 创建KCF追踪器
                            tracker.init(color_frame, ball_bbox)
                            tracking = True

                            # 绘制检测到的小球
                            cv2.rectangle(color_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.circle(color_frame, center, 5, (0, 0, 255), -1)

                            current_time = time.time()

                            if last_time is not None:
                                time_diff = current_time - last_time
                                print(f"Time since last detection: {time_diff:.4f} seconds")
                                if last_position is not None:
                                    print(f"Previous Ball Position: {last_position}, Current Ball Position: {center}")
                                    print(f"Time between detections: {time_diff:.4f} seconds\n")
                            last_time = current_time
                            last_position = center

                            print(f"Ball detected at: ({center[0]}, {center[1]}) with depth: {depth_at_center} mm")

        # 显示结果
        cv2.imshow('depth', dpt_filtered)
        cv2.imshow('color', color_frame)

        # 记录处理完这一帧的时间
        end_time = time.time()
        frame_time = end_time - start_time  # 计算每帧处理的时间
        frame_rate = 1.0 / frame_time  # 计算帧率
        frame_times.append(end_time)  # 记录时间戳
        frame_rates.append(frame_rate)  # 记录帧率

        print(f"Current frame rate: {frame_rate:.2f} FPS")

        # 按 'q' 键退出
        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            break

    # 绘制帧率随时间变化的图
    plt.figure(figsize=(10, 5))
    plt.plot(frame_times, frame_rates, label="Frame Rate (FPS)", color='b')
    plt.xlabel('Time (s)')
    plt.ylabel('Frame Rate (FPS)')
    plt.title('Frame Rate Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

    cap.release()
    cv2.destroyAllWindows()
    depth_stream.stop()
    dev.close()
