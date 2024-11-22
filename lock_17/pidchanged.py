import time

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, integral_window=5, min_output=-1, max_output=1):
        """
        初始化 PID 控制器

        :param Kp: 比例系数
        :param Ki: 积分系数
        :param Kd: 微分系数
        :param setpoint: 设定点
        :param integral_window: 积分窗口大小，只对最近的误差进行积分
        :param min_output: 输出的最小限制值
        :param max_output: 输出的最大限制值
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.last_time = time.time()
        self.error_history = []  # 存储最近的误差和时间差
        self.integral_window = integral_window  # 积分窗口大小
        self.min_output = min_output  # 输出最小值限制
        self.max_output = max_output  # 输出最大值限制

    def update(self, feedback_value):
        """
        更新 PID 控制器并计算输出

        :param feedback_value: 当前反馈值
        :return: PID 控制器输出
        """
        current_time = time.time()
        delta_time = current_time - self.last_time
        error = self.setpoint - feedback_value

        # 更新误差历史
        self.error_history.append((error, delta_time))
        if len(self.error_history) > self.integral_window:
            # 移除最早的误差
            self.error_history.pop(0)

        # 计算积分项，只累加最近的误差
        self.integral = sum(e * dt for e, dt in self.error_history)

        # 计算微分项
        derivative = (error - self.previous_error) / delta_time if delta_time > 0 else 0

        # 计算输出
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 应用输出限制
        if self.min_output is not None:
            output = max(self.min_output, output)
        if self.max_output is not None:
            output = min(self.max_output, output)

        # 更新历史数据
        self.previous_error = error
        self.last_time = current_time

        return output