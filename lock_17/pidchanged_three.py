import time

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, integral_window=5):
        """
        初始化 PID 控制器。

        :param Kp: 比例系数
        :param Ki: 积分系数
        :param Kd: 微分系数
        :param setpoint: 目标值
        :param integral_window: 积分窗口大小（用于积分防饱和）
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0.0
        self.last_time = time.time()
        self.error_history = []  # 存储最近的误差和时间差
        self.integral_window = integral_window  # 积分窗口大小
        self.integral = 0.0  # 积分项

    def update(self, feedback_value):
        """
        更新 PID 控制器并计算输出值。

        :param feedback_value: 当前反馈值
        :return: 控制器输出
        """
        current_time = time.time()
        delta_time = current_time - self.last_time
        if delta_time <= 0.0:
            delta_time = 1e-16  # 防止除以零

        error = self.setpoint - feedback_value

        # 更新误差历史
        self.error_history.append((error, delta_time))
        if len(self.error_history) > self.integral_window:
            # 移除最早的误差
            removed_error, removed_dt = self.error_history.pop(0)
            self.integral -= removed_error * removed_dt

        # 计算积分项，只累加最近的误差
        self.integral += error * delta_time

        # 计算微分项
        derivative = (error - self.previous_error) / delta_time

        # 计算输出
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 输出限制
        if output > 5:
            output = 4.5
        elif output < -3:
            output = -3

        # 更新历史数据
        self.previous_error = error
        self.last_time = current_time

        print(f"Output: {output:.4f} (Error: {error:.4f}, Integral: {self.integral:.4f}, Derivative: {derivative:.4f})")

        return output

    def set_point(self, setpoint):
        """
        动态设置新的目标点并重置 PID 控制器的状态。

        :param setpoint: 新的目标点值
        """
        self.setpoint = setpoint
        self.clear()

    def clear(self):
        """
        重置 PID 控制器的状态
        """
        self.previous_error = 0.0
        self.error_history = []
        self.integral = 0.0
        self.last_time = time.time()