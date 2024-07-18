import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import csv
def generate_matrix_m(A):
    A = np.array(A)
    rows, cols = A.shape
    M = np.zeros((rows, cols))

    # 计算每一行的和和每一列的和
    row_sums = np.sum(A, axis=1)
    col_sums = np.sum(A, axis=0)

    for i in range(rows):
        for j in range(cols):
            M[i, j] = row_sums[i] + col_sums[j] - A[i, j]

    return M
def generate_random_matrix(n=32):
    """
    随机生成一个 n x n 的矩阵，元素为 0 或 1。
    """
    return np.random.randint(256, size=(n, n))
def generate_matrix(n):
    matrix = []
    for i in range(n):
        row = [1] * (n - i) + [0] * i
        matrix.append(row)
    return np.array(matrix)
# 示例输入矩阵A

def visualize_matrices(matrix_list, n=32):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for ax, matrix, idx in zip(axes, matrix_list, range(1, 4)):
        ax.imshow(matrix, cmap='gray', interpolation='nearest')
        ax.set_title(f'Matrix {idx}')
        ax.axis('off')
    plt.tight_layout()
    plt.show()
        
def construct_B(n = 32):
    size = n * n
    B = np.zeros((size, size), dtype=float)
    
    for i in range(n):
        for j in range(n):
            row_idx = i * n + j
            # 行和部分
            for k in range(n):
                B[row_idx, i * n + k] += 0.2            # 列和部分
            for k in range(n):
                B[row_idx, k * n + j] += 0.2
            # 减去 A[i,j]
            B[row_idx, row_idx] += 0.6
    inverse_B = np.linalg.inv(B)
    return B, inverse_B

def load_from_csv(filename):
    """
    从 CSV 文件中提取数据并返回为二维数组。
    
    参数:
    filename (str): 要读取的 CSV 文件名
    
    返回:
    list of lists: 二维数组
    """
    array = []
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            array.append([-float(element) for element in row])
    return np.array(array)

n = 32

M = load_from_csv('compeye_data/compeye_20240717_234219Fig.csv')
B,Bi = construct_B()
m = M.flatten()
ra = B @ m

rA = ra.reshape(n, n)

print("\n生成的矩阵 M:")
print(M)
print("近似的矩阵 A:")
print(rA)
visualize_matrices([B, M, rA])
