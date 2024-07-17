import numpy as np
import matplotlib.pyplot as plt

# 读取CSV文件为numpy数组
def read_csv_to_numpy(filename):
    return np.loadtxt(filename, delimiter=',')

# 主函数
def main():
    data = read_csv_to_numpy('data.csv')  # 替换为你的CSV文件路径
    plt.figure(figsize=(10, 8))
    plt.imshow(data, cmap='viridis', aspect='auto')  # 选择合适的color map
    plt.colorbar()
    plt.title('Heatmap of CSV Data')
    plt.xlabel('Column Index')
    plt.ylabel('Row Index')
    plt.show()

if __name__ == '__main__':
    main()
