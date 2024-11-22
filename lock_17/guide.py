# 输入：当前坐标和目标坐标
# 流程：通过当前坐标和目标坐标，计算出下一个目标（靠近当前坐标），判断稳定当前坐标后，再计算下一个坐标靠进此时的当前坐标
# 输出：下一步的坐标
def gnposition(current_pos, target_pos, step_size=50.0, threshold=0.0001):
    """
    计算下一步的坐标

    :param current_pos: 当前坐标，元组 (x, y)
    :param target_pos: 目标坐标，元组 (x, y)
    :param step_size: 步长
    :param threshold: 稳定阈值
    :return: 下一步的坐标，元组 (x, y)
    """
    import math

    # 计算位移向量
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    distance = math.hypot(dx, dy)

    # 如果距离小于阈值，认为已到达目标
    if distance < threshold:
        return target_pos

    # 计算移动方向
    direction_x = dx / distance
    direction_y = dy / distance

    # 计算下一步位置
    next_x = current_pos[0] + direction_x * step_size
    next_y = current_pos[1] + direction_y * step_size

    return (next_x, next_y)
