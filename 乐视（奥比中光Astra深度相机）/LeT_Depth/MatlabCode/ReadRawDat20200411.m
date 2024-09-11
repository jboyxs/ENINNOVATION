clear all;
clc;

FrameNum   = 300;                                                           %   Ҫ�������֡��
filepath   = 'D:\LeT_20200409\DepthDemo\x64\Debug\2020_412_234_49345';     %   ��ԭʼ֡���ݵ��ļ���·��
namenumber = 0                                                            	%   ֡���ݵ����֣���0��ſ�ʼ���� 0000000000.bin

for i = 1 : 1 : FrameNum        
    filename       =  num2str(namenumber,'%010d');                        	%   ֡���ݵ����֣�ת�����ַ���
    FrameFilePath  =  [filepath, '\', filename, '.bin'];                  	%   Ҫ�������1֡���ݵĴ��·��

    fid1 = fopen(FrameFilePath,'rb');                                            %   �����֡�����ļ�

    img  = fread(fid1,[640,480],'uint16');                                 	%   ��16λ���ݵķ�ʽ����[640*480]�ķ�ʽ������
    img  = img';                                                          	%   Ҫ������ת��һ�£�����ͼ���ǵ�������

    imagesc(img, [500 6000]);                                             	%   ��ʾ��ͼ�����Ʒ�ΧΪ 500mm - 6000mm
    colorbar('location','EastOutside');                                    	%   ������ɫ��
    colormap hot                                                         	%   ����ͼ ��ʽ

    saveas(gcf, [filepath, '\', filename], 'png');                          %   �Ѵ�����ͼƬ������������ļ�����

    fclose(fid1);                                                           %   �ر����֡�����ļ�
    namenumber  = namenumber + 1
end
