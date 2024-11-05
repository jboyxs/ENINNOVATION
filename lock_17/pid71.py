import time

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp = Kp  # 比例系数
        self.Ki = Ki  # 积分系数
        self.Kd = Kd  # 微分系数
        self.setpoint = setpoint  # 目标值
        self.previous_error = 0
        self.integral = 0
        self.last_time = time.time()

    def update(self, feedback_value):
        current_time = time.time()
        delta_time = current_time - self.last_time
        error = self.setpoint - feedback_value
        self.integral += error * delta_time
        derivative = (error - self.previous_error) / delta_time if delta_time > 0 else 0

        # 计算控制输出
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 更新历史数据
        self.previous_error = error
        self.last_time = current_time

        return output

