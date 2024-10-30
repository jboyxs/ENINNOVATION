import numpy as np
import cv2
import time
from openni import openni2
from openni import _openni2 as c_api

depth_width = 640
depth_height = 480
DEPTH_THRESHOLD = 1000  # 设定一个深度阈值，单位为毫米

def mousecallback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(f"Depth at ({y}, {x}): {dpt[y, x]} mm")

if __name__ == "__main__":
    openni2.initialize()
    dev = openni2.Device.open_any()
    depth_stream = dev.create_depth_stream()
    depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX=depth_width, resolutionY=depth_height, fps=30))
    depth_stream.start()

    cap = cv2.VideoCapture(0)
    cv2.namedWindow('depth')
    cv2.setMouseCallback('depth', mousecallback)

    last_time = None
    last_position = None

    while True:
        frame = depth_stream.read_frame()
        dframe_data = np.array(frame.get_buffer_as_triplet()).reshape([depth_height, depth_width, 2])
        dpt1 = np.asarray(dframe_data[:, :, 0], dtype='float32')
        dpt2 = np.asarray(dframe_data[:, :, 1], dtype='float32')
        dpt2 = dpt2 * 255
        dpt = dpt1 + dpt2
        dpt = dpt[:, ::-1]

        dpt_normalized = cv2.normalize(dpt, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        dpt_filtered = cv2.GaussianBlur(dpt_normalized, (5, 5), 2)
        dpt_filtered = cv2.bilateralFilter(dpt_filtered, 9, 75, 75)
        edges = cv2.Canny(dpt_filtered, 50, 150)
        kernel = np.ones((5, 5), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel, iterations=2)
        contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        ret, color_frame = cap.read()

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 150 < area < 900:
                (x, y, w, h) = cv2.boundingRect(cnt)
                center = (x + w // 2, y + h // 2)
                depth_at_center = dpt[y + h // 2, x + w // 2]

                if depth_at_center < DEPTH_THRESHOLD:
                    perimeter = cv2.arcLength(cnt, True)
                    circularity = 4 * np.pi * (area / (perimeter ** 2)) if perimeter > 0 else 0

                    if circularity > 0.8:
                        color = (0, 0, 255)
                        thickness = 2
                        cv2.rectangle(dpt_filtered, (x, y), (x + w, y + h), color, thickness)
                        cv2.circle(dpt_filtered, center, 5, (0, 255, 0), -1)
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

        cv2.imshow('depth', dpt_filtered)
        cv2.imshow('color', color_frame)

        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    depth_stream.stop()
    dev.close()