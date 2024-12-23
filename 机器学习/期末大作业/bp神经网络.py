import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import warnings

# 忽略特定的UserWarning
warnings.filterwarnings("ignore", category=UserWarning, message=r"Glyph.*missing from font$s$ DejaVu Sans.")

# 设置Matplotlib的默认字体为SimHei
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 定义激活函数及其导数
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return np.where(x > 0, 1, 0)

# 参数设置
b = 1  # 激发函数f(x)中的系数
error_thr = 0.02  # 最大容许误差
M = 1000  # 增加最大训练轮数

input_node = 57
output_node = 2
hidden_node = 60  # 增加隐藏层节点数

eta = 0.001  # 减小初始学习率
batch_size = 32  # 小批量大小
momentum = 0.9  # 动量项
l2_lambda = 0.001  # 调整L2正则化参数

# Xavier初始化权重和偏置
wij = np.random.randn(input_node, hidden_node) * np.sqrt(2 / input_node)
wjk = np.random.randn(hidden_node, output_node) * np.sqrt(2 / hidden_node)
bH = np.zeros(hidden_node)
bY = np.zeros(output_node)

# 初始化动量项
wij_momentum = np.zeros_like(wij)
wjk_momentum = np.zeros_like(wjk)
bH_momentum = np.zeros_like(bH)
bY_momentum = np.zeros_like(bY)

# 获取当前工作目录
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")

# 构建数据文件的完整路径
data_file_path = os.path.join(current_dir, 'spambase.data')
print(f"Data file path: {data_file_path}")

# 检查文件是否存在
if not os.path.exists(data_file_path):
    print("Error: Data file not found.")
else:
    # 加载数据并跳过第一行
    data_all = np.genfromtxt(data_file_path, delimiter=',', skip_header=1)
    data_all_samples = data_all[:, :57]  # 样本特征
    data_all_label = data_all[:, 57:]  # 样本标签

    # 数据归一化处理
    scaler = StandardScaler()
    data_all_samples = scaler.fit_transform(data_all_samples)

    # 打乱数据并划分训练集、验证集和测试集
    X_train_val, X_test, y_train_val, y_test = train_test_split(data_all_samples, data_all_label, test_size=0.2, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, random_state=42)

    # 将训练集标签扩展为2维输出
    y_train_one_hot = np.zeros((y_train.shape[0], output_node))
    for i, label in enumerate(y_train.flatten()):
        if label == 0:
            y_train_one_hot[i] = [1, 0]  # 非垃圾邮件
        else:
            y_train_one_hot[i] = [0, 1]  # 垃圾邮件

    # 将验证集标签扩展为2维输出
    y_val_one_hot = np.zeros((y_val.shape[0], output_node))
    for i, label in enumerate(y_val.flatten()):
        if label == 0:
            y_val_one_hot[i] = [1, 0]  # 非垃圾邮件
        else:
            y_val_one_hot[i] = [0, 1]  # 垃圾邮件

    error_accu_round = []  # 存储每轮训练结束后的累计误差
    val_error_accu_round = []  # 存储每轮验证结束后的累计误差

    best_val_loss = float('inf')
    patience = 10  # 早停耐心
    no_improvement_count = 0

    # 训练神经网络
    for round_num in range(M):
        error_accu = 0  # 单轮训练内的误差
        for batch_start in range(0, len(X_train), batch_size):
            batch_end = min(batch_start + batch_size, len(X_train))
            batch_input = X_train[batch_start:batch_end].T
            batch_target = y_train_one_hot[batch_start:batch_end]

            wij_grad_sum = np.zeros_like(wij)
            wjk_grad_sum = np.zeros_like(wjk)
            bH_grad_sum = np.zeros_like(bH)
            bY_grad_sum = np.zeros_like(bY)

            for index in range(batch_input.shape[1]):
                # 前向传播
                hI = np.dot(wij.T, batch_input[:, index]) - bH
                hO = relu(hI)
                yI = np.dot(wjk.T, hO) - bY
                yO = sigmoid(yI).flatten()  # 确保 yO 是一维数组

                # 计算误差
                error_accu += 0.5 * np.sum((batch_target[index] - yO) ** 2)

                # 反向传播计算梯度
                delta_O = (batch_target[index] - yO) * sigmoid_derivative(yO)
                wjk_grad_sum += np.outer(hO, delta_O)
                bY_grad_sum += delta_O

                delta_H = np.dot(wjk, delta_O) * relu_derivative(hI)
                wij_grad_sum += np.outer(batch_input[:, index], delta_H)
                bH_grad_sum += delta_H

            # 平均梯度
            wij_grad_avg = wij_grad_sum / batch_input.shape[1]
            wjk_grad_avg = wjk_grad_sum / batch_input.shape[1]
            bH_grad_avg = bH_grad_sum / batch_input.shape[1]
            bY_grad_avg = bY_grad_sum / batch_input.shape[1]

            # 更新权重和偏置，加入动量和L2正则化
            wij_momentum = momentum * wij_momentum + eta * (wij_grad_avg - l2_lambda * wij)
            wjk_momentum = momentum * wjk_momentum + eta * (wjk_grad_avg - l2_lambda * wjk)
            bH_momentum = momentum * bH_momentum + eta * bH_grad_avg
            bY_momentum = momentum * bY_momentum + eta * bY_grad_avg

            wij += wij_momentum
            wjk += wjk_momentum
            bH += bH_momentum
            bY += bY_momentum

        # 存储本轮的累计误差
        error_accu /= len(X_train)
        error_accu_round.append(error_accu)

        # 验证集上的误差计算
        val_error_accu = 0
        for index in range(len(X_val)):
            # 前向传播
            hI = np.dot(wij.T, X_val[index].T) - bH
            hO = relu(hI)
            yI = np.dot(wjk.T, hO) - bY
            yO = sigmoid(yI).flatten()  # 确保 yO 是一维数组

            # 计算误差
            val_error_accu += 0.5 * np.sum((y_val_one_hot[index] - yO) ** 2)

        val_error_accu /= len(X_val)
        val_error_accu_round.append(val_error_accu)

        # 如果验证集误差小于要求时结束训练
        if val_error_accu < error_thr:
            break

        # 早停法
        if val_error_accu < best_val_loss:
            best_val_loss = val_error_accu
            no_improvement_count = 0
        else:
            no_improvement_count += 1
            if no_improvement_count >= patience:
                print(f"Early stopping at epoch {round_num} due to no improvement on validation set.")
                break

        # 学习率调度
        if round_num % 100 == 0:
            eta *= 0.9  # 每100个epoch将学习率乘以0.9

    # 测试神经网络
    count_0 = 0
    count_1 = 0
    y_true = []
    y_pred = []

    for index_test in range(len(X_test)):
        # 前向传播
        hI = np.dot(wij.T, X_test[index_test].T) - bH
        hO = relu(hI)
        yI = np.dot(wjk.T, hO) - bY
        yO = sigmoid(yI).flatten()  # 确保 yO 是一维数组

        if yO[0] > yO[1]:
            predicted_class = 0
        else:
            predicted_class = 1

        y_true.append(int(y_test[index_test]))
        y_pred.append(predicted_class)

        if predicted_class == 0 and y_test[index_test] == 0:
            count_0 += 1
        elif predicted_class == 1 and y_test[index_test] == 1:
            count_1 += 1

    # 计算精确率、召回率和F1分数
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print(f'非垃圾邮件正确识别率: {count_0 / (len(X_test) - np.sum(y_test)):.3f}')
    print(f'垃圾邮件正确识别率: {count_1 / np.sum(y_test):.3f}')
    print(f'精确率: {precision:.3f}')
    print(f'召回率: {recall:.3f}')
    print(f'F1分数: {f1:.3f}')

    # 绘制训练过程中的误差变化曲线
    plt.figure(figsize=(12, 6))
    plt.plot(error_accu_round, label='训练误差')
    plt.plot(val_error_accu_round, label='验证误差')
    plt.xlabel('训练轮数')
    plt.ylabel('累计误差')
    plt.title('训练过程中累计误差的变化')
    plt.legend()
    plt.show()