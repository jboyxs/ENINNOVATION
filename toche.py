import cv2
import numpy as np

def adjust_hsv():
    """创建图形化界面调节 HSV 范围"""
    # 创建窗口和滑动条
    cv2.namedWindow("HSV Adjuster")
    cv2.resizeWindow("HSV Adjuster", 400, 300)
    
    # 初始化滑动条值
    cv2.createTrackbar("Lower H", "HSV Adjuster", 50, 180, lambda x: None)  # H 范围：0-180
    cv2.createTrackbar("Lower S", "HSV Adjuster", 120, 255, lambda x: None) # S 范围：0-255
    cv2.createTrackbar("Lower V", "HSV Adjuster", 190, 255, lambda x: None) # V 范围：0-255

    cv2.createTrackbar("Upper H", "HSV Adjuster", 100, 180, lambda x: None)
    cv2.createTrackbar("Upper S", "HSV Adjuster", 200, 255, lambda x: None)
    cv2.createTrackbar("Upper V", "HSV Adjuster", 255, 255, lambda x: None)

def main():
    """主程序：打开摄像头并应用 HSV 调整器"""
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    # 初始化 HSV 调节器
    adjust_hsv()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧")
            break

        # 获取滑动条值
        lower_h = cv2.getTrackbarPos("Lower H", "HSV Adjuster")
        lower_s = cv2.getTrackbarPos("Lower S", "HSV Adjuster")
        lower_v = cv2.getTrackbarPos("Lower V", "HSV Adjuster")
        upper_h = cv2.getTrackbarPos("Upper H", "HSV Adjuster")
        upper_s = cv2.getTrackbarPos("Upper S", "HSV Adjuster")
        upper_v = cv2.getTrackbarPos("Upper V", "HSV Adjuster")

        # 形成 HSV 范围
        lower_blue = np.array([lower_h, lower_s, lower_v])
        upper_blue = np.array([upper_h, upper_s, upper_v])

        # 转换为 HSV 并应用遮罩
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # 显示原始图像和结果
        cv2.imshow("Original Frame", frame)
        cv2.imshow("Masked Frame", result)

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
