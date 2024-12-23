import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets._samples_generator import make_blobs, make_circles

# 生成用于硬间隔支持向量机（Hard Margin SVM）的训练数据
# 使用make_blobs函数创建两个中心的数据点，样本数量为50，标准差为0.60，随机状态固定为0以保证结果可重复
X_hard_margin, y_hard_margin = make_blobs(
    n_samples=50, centers=2, random_state=0, cluster_std=0.60
)

# 创建并训练硬间隔支持向量机模型
# 使用线性核函数和较大的惩罚参数C=1E10来实现硬间隔
model_hard_margin = SVC(kernel='linear', C=1E10)
model_hard_margin.fit(X_hard_margin, y_hard_margin)


def plot_svc_decision_function(model, ax=None, plot_support=True):
    """
    绘制二维SVC决策函数

    参数:
    - model: 训练好的SVC模型
    - ax: Matplotlib轴对象，用于绘制图形。如果为None，则使用当前轴。
    - plot_support: 布尔值，指示是否绘制支持向量
    """
    if ax is None:
        ax = plt.gca()

    # 获取当前轴的x和y范围
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # 创建网格以评估模型
    # 在x和y方向上分别创建30个等间距的点，形成一个网格
    x_grid = np.linspace(xlim[0], xlim[1], 30)
    y_grid = np.linspace(ylim[0], ylim[1], 30)
    Y, X = np.meshgrid(y_grid, x_grid)

    # 将网格上的所有点展平成二维数组，并计算每个点的决策函数值
    xy_points = np.vstack([X.ravel(), Y.ravel()]).T
    decision_values = model.decision_function(xy_points).reshape(X.shape)

    # 绘制决策边界和间隔
    # 决策函数值为-1、0和1的地方分别是负间隔边界、超平面和支持向量之间的正间隔边界
    ax.contour(X, Y, decision_values, colors='k',
               levels=[-1, 0, 1], alpha=0.5,
               linestyles=['--', '-', '--'])

    # 绘制支持向量
    if plot_support:
        ax.scatter(model.support_vectors_[:, 0],
                   model.support_vectors_[:, 1],
                   s=300, linewidth=1, facecolors='none', edgecolors='black')

    # 设置轴范围
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)


# 绘制硬间隔支持向量机的结果
plt.figure(figsize=(8, 6))
plt.scatter(X_hard_margin[:, 0], X_hard_margin[:, 1], c=y_hard_margin, s=50, cmap='summer')
plot_svc_decision_function(model_hard_margin, plot_support=True)
plt.title("Hard Margin SVM")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()

# 生成用于软间隔支持向量机（Soft Margin SVM）的训练数据
# 使用make_blobs函数创建两个中心的数据点，样本数量为100，标准差为0.8，随机状态固定为0以保证结果可重复
X_soft_margin, y_soft_margin = make_blobs(
    n_samples=100, centers=2, random_state=0, cluster_std=0.8
)

# 创建子图以显示不同C参数下的结果
# 创建一个包含两列的子图布局，每列对应一个不同的C值
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.subplots_adjust(left=0.0625, right=0.95, wspace=0.1)

# 不同的惩罚参数C列表
C_list = [10, 0.1]

for i, C_value in enumerate(C_list):
    # 创建并训练带有不同C参数的支持向量机模型
    # 较小的C值允许更多的误分类，从而实现软间隔
    model_soft_margin = SVC(kernel="linear", C=C_value)
    model_soft_margin.fit(X_soft_margin, y_soft_margin)

    # 在子图上绘制结果
    axes[i].scatter(X_soft_margin[:, 0], X_soft_margin[:, 1], c=y_soft_margin, s=50, cmap="summer")
    plot_svc_decision_function(model_soft_margin, axes[i])
    axes[i].set_title(f'Soft Margin SVM with C = {C_value}', size=14)
    axes[i].set_xlabel("Feature 1")
    axes[i].set_ylabel("Feature 2")

plt.show()

# 生成用于核支持向量机（Kernel SVM）的训练数据
# 使用make_circles函数创建两个同心圆的数据点，噪声水平为0.1，因子为0.1
X_kernel, y_kernel = make_circles(100, factor=.1, noise=.1)

# 创建并训练带有径向基函数核的支持向量机模型
# 使用RBF核函数和较大的惩罚参数C=1E6来提高模型的拟合能力
model_kernel_svm = SVC(kernel='rbf', C=1E6)
model_kernel_svm.fit(X_kernel, y_kernel)

# 绘制核支持向量机的结果
plt.figure(figsize=(8, 6))
plt.scatter(X_kernel[:, 0], X_kernel[:, 1], c=y_kernel, s=50, cmap='autumn')
plot_svc_decision_function(model_kernel_svm)
plt.scatter(model_kernel_svm.support_vectors_[:, 0],
            model_kernel_svm.support_vectors_[:, 1],
            s=300, lw=1, facecolors='none')
plt.title("Kernel SVM with RBF Kernel")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()