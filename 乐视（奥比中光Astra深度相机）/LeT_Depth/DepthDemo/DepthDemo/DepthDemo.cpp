// DepthDemo.cpp : �������̨Ӧ�ó������ڵ㡣
//
#include "stdafx.h"             //���һ��Ҫ������ǰ�棡

#include <astra/capi/astra.h>
#include <stdio.h>
#include <key_handler.h>

#include <Windows.h>
#include<iostream>
#include <fstream>
#include <stdlib.h>

#include <atlstr.h>                 //CString��Ҫ��ͷ�ļ�

uint32_t  FileName = 0;             //FileName���ļ������ļ���ֵ��uint32_t���ͣ���Ҳ�൱�ڱ���ͼ��֡���ļ���ֵ
CString   FileNameStr;              //FileNameת���ַ�����ʽ������������Ϊ�ļ���ʹ�ã�FileNameStr�����ַ�����ʽ
CString   strFolder;                //Ҫ�������ļ������ƣ� ͼ��֡������ 1�� 1�� .bin �ļ��ķ�ʽ����������ļ�������

int16_t   FramesSamples = 300;      //�ܹ��ɼ�����֡����

void print_depth(astra_depthframe_t depthFrame)
{
    astra_image_metadata_t  metadata;               //  ���ͼ�����Ϣ�ṹ�����ݣ�����width��height��pixelFormat
    int16_t*                depthData;              //  ָ��������ݵ�ָ�룬����������� mm Ϊ��λ
    uint32_t                depthLength;            //  ������ݵĳ��ȣ�Ҳ���Ǹ�����    

    astra_depthframe_get_data_ptr(depthFrame, &depthData, &depthLength);//  ����ȴ����������ݶ�����
    astra_depthframe_get_metadata(depthFrame, &metadata);               //  �����ͼ�����Ϣ������������width��height��pixelFormat

    HANDLE                  hFile;                  //  �����xxxxxxxxxx.bin�ļ��ľ������ÿ1֡ͼ����1�� .bin �ļ�

                                                    //  _T("")��һ���꣬����������ĳ���֧��Unicode����
    FileNameStr.Format(_T("%010d"), FileName);      //  FileName���ļ������ļ���ֵ��uint32_t���ͣ���Ҳ�൱�ڱ���ͼ��֡���ļ���ֵ��
                                                    //  ���������ֵ��Ϊ.bin �ļ�����FileNameת���ַ�����ʽ������������Ϊ�ļ���ʹ�ã�FileNameStr�����ַ�����ʽ
    FileName++;                                     //  FileName������
    FileNameStr = FileNameStr + _T(".bin");         //  ���ַ����������� .bin �ַ������γ�1��������xxxxxxxxxx.bin�ļ���
                                                    
    //  ��strFolder�ļ�·�������1����ΪFileNameStr���ļ����е�VS�汾��Ҫ�� (LPCTSTR) ǿ��ת��һ�¸�ʽ���е�����Ҫ
    //  _T("\\")�е�2�� \ ������1����ת���������
    hFile = CreateFile((LPCTSTR)(strFolder + _T("\\") + FileNameStr), GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);

    DWORD                   dwWrites;                           //  ���ڱ���WriteFileʵ��д���˶��ٸ����ݣ���ʵ�ڱ�������û���ã�����WriteFileҪ�����������
    WriteFile(hFile, depthData, depthLength, &dwWrites, NULL);  //  ����1֡ͼ���depthData����д��FileNameStr�ļ�����   
    CloseHandle(hFile);                                         //  ���ļ��ر���

    int width = metadata.width;                                 //  ͼ�Ŀ��
    int height = metadata.height;                               //  ͼ�ĸ߶�

    size_t index = ((width * (height / 2)) + (width / 2));      //  ȡ��ͼ���м���Ǹ����������ݣ���ʾ����
    short middle = depthData[index];

    astra_frame_index_t frameIndex;                             //  ��ǰΪ�ڼ�֡ͼ������Ǵ������ڲ��ļ���ֵ��
    astra_depthframe_get_frameindex(depthFrame, &frameIndex);
    printf("depth frameIndex:  %d  value:  %d  Len:  %d WD:  %d HT:  %d\n", frameIndex, middle, depthLength, width, height);

    FramesSamples--;//ÿ�βɼ���1֡���ݣ�FramesSamples���Լ�1
}

void frame_ready(void* clientTag, astra_reader_t reader, astra_reader_frame_t frame)
{
    astra_depthframe_t depthFrame;
    astra_frame_get_depthframe(frame, &depthFrame);

    print_depth(depthFrame);
}

void CreatDocument()//����1��������ݵ��ļ���
{
    SYSTEMTIME  sys; 
    CString     strTemp;

    GetLocalTime(&sys);                     //����windowsϵͳ��ʱ��

    //��  YY_MMDD_HHMM_SSMS   Ϊ�ļ��е�����
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

    if(!PathFileExists(strFolder))          //  �ļ��в������򴴽�
    {
        CreateDirectory(strFolder,NULL);    //  �ڳ������е�Ŀ¼���棬��������ļ���
    }    
}

int main(int argc, char* argv[])
{
    set_key_handler();          //  ���� Ctrl+C ����ֹͣ�ɼ������˳�����

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
    } while ( (FramesSamples>0) && (shouldContinue==true) );        //  �ɼ���ָ��֡�� ���� ������Ctrl+C  ����ֹͣ�ɼ������˳�����

    astra_reader_unregister_frame_ready_callback(&callbackId);

    astra_reader_destroy(&reader);
    astra_streamset_close(&sensor);

    astra_terminate();
}