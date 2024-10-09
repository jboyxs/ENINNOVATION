from openni import openni2
from openni import _openni2 as c_api
import numpy as np
import cv2

depth_width = 640
depth_height = 480

def mousecallback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(y, x, dpt[y, x])

if __name__ == "__main__":
    openni2.initialize()

    dev = openni2.Device.open_any()
    print(dev.get_device_info())
     # 创建一个深度数据流对象
    depth_stream = dev.create_depth_stream()
    print(depth_stream.get_video_mode())
    # 设置深度数据流的视频模式
    depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX = depth_width, resolutionY = depth_height, fps = 30))
    depth_stream.start()
    

    # 打开视频捕获设备，参数1表示使用第二个摄像头（如果有多个摄像头的话）
    cap = cv2.VideoCapture(1)
    # 创建一个名为 'depth' 的窗口，用于显示视频
    cv2.namedWindow('depth')
    # 设置鼠标回调函数，当在 'depth' 窗口中发生鼠标事件时，调用 mousecallback 函数进行处理
    cv2.setMouseCallback('depth', mousecallback)


    while True :
        # 从深度数据流中读取一帧数据
        frame = depth_stream.read_frame()

        # 从深度帧中获取原始数据，并将其转换为一个形状为 (depth_height, depth_width, 2) 的三维数组
        dframe_data = np.array(frame.get_buffer_as_triplet()).reshape([depth_height, depth_width, 2])
        # 提取深度数据的第一个通道，并将其转换为 float32 类型的数组
        dpt1 = np.asarray(dframe_data[:, :, 0],dtype='float32')
        # 提取深度数据的第二个通道，并将其转换为 float32 类型的数组
        dpt2 = np.asarray(dframe_data[:, :, 1],dtype='float32')

        
        dpt2 = dpt2*255
        dpt = dpt1 + dpt2
        dpt = dpt[:,::-1]
        cv2.imshow('depth', dpt)

        ret, frame = cap.read()
        cv2.imshow('color', frame)

        key = cv2.waitKey(1)
        if int(key) == ord('q'):
            break

cap.release()

cv2.destroyAllWindows()

depth_stream.stop()
dev.close()

