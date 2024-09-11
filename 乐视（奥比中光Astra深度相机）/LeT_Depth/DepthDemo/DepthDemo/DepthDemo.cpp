// DepthDemo.cpp : 定义控制台应用程序的入口点。
//
#include "stdafx.h"             //这个一定要放在最前面！

#include <astra/capi/astra.h>
#include <stdio.h>
#include <key_handler.h>

#include <Windows.h>
#include<iostream>
#include <fstream>
#include <stdlib.h>

#include <atlstr.h>                 //CString需要的头文件

uint32_t  FileName = 0;             //FileName是文件个数的计数值（uint32_t类型），也相当于保存图像帧数的计数值
CString   FileNameStr;              //FileName转成字符串格式，这样才能作为文件名使用，FileNameStr就是字符串格式
CString   strFolder;                //要创建的文件夹名称， 图像帧数据以 1祯 1个 .bin 文件的方式，存在这个文件夹里面

int16_t   FramesSamples = 300;      //总共采集多少帧数据

void print_depth(astra_depthframe_t depthFrame)
{
    astra_image_metadata_t  metadata;               //  深度图像的信息结构体数据，包含width，height，pixelFormat
    int16_t*                depthData;              //  指向深度数据的指针，深度数据是以 mm 为单位
    uint32_t                depthLength;            //  深度数据的长度（也就是个数）    

    astra_depthframe_get_data_ptr(depthFrame, &depthData, &depthLength);//  把深度传感器的数据读出来
    astra_depthframe_get_metadata(depthFrame, &metadata);               //  把深度图像的信息读出来，包含width，height，pixelFormat

    HANDLE                  hFile;                  //  这个是xxxxxxxxxx.bin文件的句柄，把每1帧图像存成1个 .bin 文件

                                                    //  _T("")是一个宏，作用是让你的程序支持Unicode编码
    FileNameStr.Format(_T("%010d"), FileName);      //  FileName是文件个数的计数值（uint32_t类型），也相当于保存图像帧数的计数值，
                                                    //  以这个计数值作为.bin 文件名，FileName转成字符串格式，这样才能作为文件名使用，FileNameStr就是字符串格式
    FileName++;                                     //  FileName自增加
    FileNameStr = FileNameStr + _T(".bin");         //  在字符串的最后添加 .bin 字符串，形成1个完整的xxxxxxxxxx.bin文件名
                                                    
    //  在strFolder文件路径里，创建1个名为FileNameStr的文件。有的VS版本需要加 (LPCTSTR) 强制转换一下格式，有的则不需要
    //  _T("\\")中的2个 \ ，其中1个起转义符的作用
    hFile = CreateFile((LPCTSTR)(strFolder + _T("\\") + FileNameStr), GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);

    DWORD                   dwWrites;                           //  用于保存WriteFile实际写入了多少个数据，其实在本例子中没有用，但是WriteFile要求有这个参数
    WriteFile(hFile, depthData, depthLength, &dwWrites, NULL);  //  把这1帧图像的depthData数据写到FileNameStr文件里面   
    CloseHandle(hFile);                                         //  把文件关闭了

    int width = metadata.width;                                 //  图的宽度
    int height = metadata.height;                               //  图的高度

    size_t index = ((width * (height / 2)) + (width / 2));      //  取出图像中间的那个点的深度数据，显示出来
    short middle = depthData[index];

    astra_frame_index_t frameIndex;                             //  当前为第几帧图像（这个是传感器内部的计数值）
    astra_depthframe_get_frameindex(depthFrame, &frameIndex);
    printf("depth frameIndex:  %d  value:  %d  Len:  %d WD:  %d HT:  %d\n", frameIndex, middle, depthLength, width, height);

    FramesSamples--;//每次采集完1帧数据，FramesSamples就自减1
}

void frame_ready(void* clientTag, astra_reader_t reader, astra_reader_frame_t frame)
{
    astra_depthframe_t depthFrame;
    astra_frame_get_depthframe(frame, &depthFrame);

    print_depth(depthFrame);
}

void CreatDocument()//创建1个存放数据的文件夹
{
    SYSTEMTIME  sys; 
    CString     strTemp;

    GetLocalTime(&sys);                     //读到windows系统的时间

    //以  YY_MMDD_HHMM_SSMS   为文件夹的名字
    strTemp.Format(_T("%d"), sys.wYear);
    strFolder += strTemp;
    strTemp.Format(_T("_%d"), sys.wMonth);
    strFolder += strTemp;
    strTemp.Format(_T("%d"), sys.wDay);
    strFolder += strTemp;
    strTemp.Format(_T("_%d"), sys.wHour);
    strFolder += strTemp;
    strTemp.Format(_T("%d"), sys.wMinute);
    strFolder += strTemp;
    strTemp.Format(_T("_%d"), sys.wSecond);
    strFolder += strTemp;
    strTemp.Format(_T("%d"), sys.wMilliseconds);
    strFolder += strTemp;

    if(!PathFileExists(strFolder))          //  文件夹不存在则创建
    {
        CreateDirectory(strFolder,NULL);    //  在程序运行的目录里面，创建这个文件夹
    }    
}

int main(int argc, char* argv[])
{
    set_key_handler();          //  按下 Ctrl+C 将会停止采集，并退出程序

    CreatDocument();
    astra_initialize();

    astra_streamsetconnection_t sensor;

    astra_streamset_open("device/default", &sensor);

    astra_reader_t reader;
    astra_reader_create(sensor, &reader);

    astra_depthstream_t depthStream;
    astra_reader_get_depthstream(reader, &depthStream);
    astra_stream_start(depthStream);

    astra_reader_callback_id_t callbackId;
    astra_reader_register_frame_ready_callback(reader, &frame_ready, NULL, &callbackId);

    do
    {
        astra_update();
    } while ( (FramesSamples>0) && (shouldContinue==true) );        //  采集完指定帧数 或者 按下了Ctrl+C  将会停止采集，并退出程序

    astra_reader_unregister_frame_ready_callback(&callbackId);

    astra_reader_destroy(&reader);
    astra_streamset_close(&sensor);

    astra_terminate();
}