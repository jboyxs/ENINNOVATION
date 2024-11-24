import time

import time

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, integral_window=5):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.last_time = time.time()
        self.error_history = []  # 存储最近的误差和时间差
        self.integral_window = integral_window  # 积分窗口大小

    def update(self, feedback_value):
        # current_time = time.time()
        # delta_time = current_time - self.last_time
        error = self.setpoint - feedback_value

        # 更新误差历史
        self.error_history.append((error, 1))
        if len(self.error_history) > self.integral_window:
            # 移除最早的误差
            self.error_history.pop(0)

        # 计算积分项，只累加最近的误差
        self.integral = sum(e * dt for e, dt in self.error_history)

        # 计算微分项
        # derivative = (error - self.previous_error) / delta_time if delta_time > 0 else 0
        derivative = (error - self.previous_error) 
        # 计算输出
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 更新历史数据
        self.previous_error = error
        # self.last_time = current_time

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