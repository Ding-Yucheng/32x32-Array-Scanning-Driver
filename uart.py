import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# 配置串口参数，需与ESP32端串口设置一致，将'COM3'替换为实际的串口号
ser = serial.Serial('COM3', 115200)
time.sleep(2)  # 等待串口初始化，可根据实际情况调整等待时间

# 用于存储接收到的数据
received_data = np.zeros((32, 32))


def update(frame):
    """
    用于更新绘图数据的函数，被FuncAnimation定期调用
    """
    global received_data
    print(received_data)
    try:
        if ser.in_waiting:  # 检查串口是否有数据可读
            raw_data = ser.readline().decode('utf-8').strip()  # 读取一行数据并解码、去除空白字符
            if raw_data.startswith('str') and raw_data.endswith('end'):
                data_list = raw_data[3:-3].split('.')  # 去除开头和结尾标识后按点分割数据
                if len(data_list) == 32 * 32:  # 确保接收到的数据量正确
                    data_array = np.array(list(map(int, data_list))).reshape(32, 32)
                    received_data = data_array
                    ax.clear()  # 清除之前的绘图
                    im = ax.imshow(received_data, cmap='hot', interpolation='nearest')  # 绘制热力图，可调整颜色映射等参数
                    plt.colorbar(im)  # 添加颜色条便于查看数值对应的颜色
    except Exception as e:
        print(f"读取或绘制数据出现错误: {e}")


# 创建绘图对象和坐标轴
fig, ax = plt.subplots()

# 设置绘图相关属性，如标题、坐标轴标签等
ax.set_title("实时热力图")
ax.set_xlabel("X轴")
ax.set_ylabel("Y轴")

# 创建动画，每1000毫秒（1秒）调用一次update函数来更新绘图
ani = animation.FuncAnimation(fig, update, interval=1000)

# 显示绘图窗口
plt.show()
