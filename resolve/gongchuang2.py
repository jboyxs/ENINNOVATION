from ctypes import *
import time

def calculate_inverse_kinematics(PITCH, ROLL):
    # 加载 DLL 文件
    pRSS6RBT_Inverse = CDLL(r"d:\en\project\resolve\RSS6RBT_InverseDLL.dll")
    
    pInversResult = (c_double * 6)()
    I = 0
    J = 0

    # 固定 XP、YP、YAW 的值
    XP = 0.0
    YP = 0.0
    YAW = 0.0

    # 定义 ZP 的不同值
    ZP_values = [168, 173, 178, 183, 188, 193, 198, 203, 208, 213]

    # 初始化最小距离和最近的 ZP 值
    min_distance = float('inf')
    closest_ZP = None
    closest_pInversResult = None

    # 遍历 ZP 的不同值
    for ZP in ZP_values:
        T0 = time.time()
        # 只循环一次，因为输入是手动的
        I += 1
        ret = pRSS6RBT_Inverse.InK6RSS(
            c_double(XP), c_double(YP), c_double(ZP),
            c_double(YAW), c_double(PITCH), c_double(ROLL),
            pointer(pInversResult)
        )
        if (I % 100000) == 0:
            print(f"第 {I} 次, 经过了: {time.time() - T0} s")
        if any(angle == -360 for angle in pInversResult) or ret == 0:
            J += 1
        else:
            # 计算当前 ZP 值与 183 的距离
            distance = abs(ZP - 183)
            # 如果当前距离更小，更新最小距离和最近的 ZP 值
            if distance < min_distance:
                min_distance = distance
                closest_ZP = ZP
                closest_pInversResult = [int(round(x)) for x in pInversResult]

    # 输出与最接近 183 的 ZP 值对应的数据
    if closest_ZP is not None and closest_pInversResult is not None:
        # 以下三行已删除：不再写入文件
        # File.write(f"{XP}    {YP}    {closest_ZP}    {YAW}    {PITCH}    {ROLL}    ")
        # File.write("    ".join(str(x) for x in closest_pInversResult))
        # File.write("\n")
        return closest_pInversResult
    else:
        return None