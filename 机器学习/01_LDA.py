import numpy as np
import matplotlib.pyplot as plt

# 设置matplotlib的字体为SimHei，以便正确显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']
# 设置matplotlib正确显示负号
plt.rcParams['axes.unicode_minus'] = False

# 定义数据集，每一行代表一个样本，前两列是特征值，最后一列是类别标签（1表示正例，0表示反例）
data = np.array([
    [0.666, 0.091, 1],
    [0.243, 0.267, 1],
    [0.244, 0.056, 1],
    [0.342, 0.098, 1],
    [0.638, 0.16, 1],
    [0.656, 0.197, 1],
    [0.359, 0.369, 1],
    [0.592, 0.041, 1],
    [0.718, 0.102, 1],
    [0.697, 0.46, 0],
    [0.774, 0.376, 0],
    [0.633, 0.263, 0],
    [0.607, 0.317, 0],
    [0.555, 0.214, 0],
    [0.402, 0.236, 0],
    [0.481, 0.149, 0],
    [0.436, 0.21, 0],
    [0.557, 0.216, 0]
])

# 分离特征和标签
# 特征向量X包含所有样本的前两列数据
X = data[:, :2]
# 标签向量y包含所有样本的最后一列数据
y = data[:, 2]

# 计算正例和反例的均值向量
# 正例均值向量
mu_0 = np.mean(X[y == 0], axis=0)
# 反例均值向量
mu_1 = np.mean(X[y == 1], axis=0)

# 计算类内散度矩阵S_w
# S_w是所有类别的样本与其各自类平均值之间的差异的总和
S_w = np.zeros((2, 2))
for i in range(len(X)):
    if y[i] == 0:  # 如果标签为0（反例）
        S_w += np.outer(X[i] - mu_0, X[i] - mu_0)
    else:  # 如果标签为1（正例）
        S_w += np.outer(X[i] - mu_1, X[i] - mu_1)

# 计算最优投影方向w_prime
# 最优投影方向是类内散度矩阵S_w的逆与两个类别均值向量差的点积
w_prime = np.linalg.inv(S_w).dot(mu_0 - mu_1)

# 计算LDA分割线（决策边界），决策边界垂直于投影向量w_prime，且通过两个类别均值的中点
mid_point = (mu_0 + mu_1) / 2  # 中点是两个类别均值的平均值
slope = w_prime[1] / w_prime[0]  # 斜率是投影向量的第二个元素除以第一个元素

# 计算垂直于投影向量的斜率
# 垂直斜率是原斜率的倒数的相反数
slope_perpendicular = -1 / slope

# 计算截距
# 截距是中点的y坐标减去垂直斜率乘以中点的x坐标
intercept_perpendicular = mid_point[1] - slope_perpendicular * mid_point[0]

# 绘制数据点
plt.figure(figsize=(10, 6))  # 设置图形大小
plt.scatter(X[y == 1][:, 0], X[y == 1][:, 1], color='blue', label='正例')  # 绘制正例
plt.scatter(X[y == 0][:, 0], X[y == 0][:, 1], color='red', label='反例')  # 绘制反例

# 绘制LDA分割线
x_values = np.linspace(0, 1, 100)  # 创建一系列x值
y_values = slope_perpendicular * x_values + intercept_perpendicular  # 计算相应的y值
plt.plot(x_values, y_values, color='green', label='LDA 分割线')  # 绘制分割线

# 添加其他图形设置
plt.xlabel('属性1')  # 设置x轴标签
plt.ylabel('属性2')  # 设置y轴标签
plt.legend()  # 显示图例
plt.title('数据集和LDA分割线')  # 设置标题
plt.show()  # 展示图形

# 输出投影向量
print(f'投影向量为：{w_prime}')
# 输出LDA分割线的方程
print(f'LDA分割线的方程为：y = {slope_perpendicular}x + {intercept_perpendicular}')