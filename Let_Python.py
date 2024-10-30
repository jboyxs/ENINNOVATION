import numpy as np
import cv2
import time

depth_width = 640
depth_height = 480

def nothing(x):
    pass

def mousecallback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(f"Coordinates: ({x}, {y})")

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('color')
    cv2.setMouseCallback('color', mousecallback)

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

        gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)

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
                    cv2.rectangle(color_frame, (x, y), (x + w, y + h), color, thickness)
                    cv2.circle(color_frame, center, 5, (0, 255, 0), -1)

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

        cv2.imshow('color', color_frame)
        cv2.imshow('edges', edges)

        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()