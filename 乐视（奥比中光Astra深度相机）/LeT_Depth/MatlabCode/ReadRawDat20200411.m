clear all;
clc;

FrameNum   = 300;                                                           %   要处理的总帧数
filepath   = 'D:\LeT_20200409\DepthDemo\x64\Debug\2020_412_234_49345';     %   存原始帧数据的文件夹路径
namenumber = 0                                                            	%   帧数据的名字，从0编号开始，即 0000000000.bin

for i = 1 : 1 : FrameNum        
    filename       =  num2str(namenumber,'%010d');                        	%   帧数据的名字，转成了字符串
    FrameFilePath  =  [filepath, '\', filename, '.bin'];                  	%   要处理的这1帧数据的存放路径

    fid1 = fopen(FrameFilePath,'rb');                                            %   打开这个帧数据文件

    img  = fread(fid1,[640,480],'uint16');                                 	%   以16位数据的方式，以[640*480]的方式，读出
    img  = img';                                                          	%   要把数据转置一下，否则图像是倒过来的

    imagesc(img, [500 6000]);                                             	%   显示的图，限制范围为 500mm - 6000mm
    colorbar('location','EastOutside');                                    	%   开启颜色条
    colormap hot                                                         	%   热力图 形式

    saveas(gcf, [filepath, '\', filename], 'png');                          %   把处理后的图片，存放在数据文件夹中

    fclose(fid1);                                                           %   关闭这个帧数据文件
    namenumber  = namenumber + 1
end
