# -*- coding: utf-8 -*-
# 本程序由UESTC的BigMoyan完成，并供所有人免费参考学习，但任何对本程序的使用必须包含这条声明

# 导入必要的库
import math
import numpy as np
import scipy.io as sio

# 读入数据
#############################################################################################
# 打印提示信息
print("输入样本文件名（需放在程序目录下）")
# 设置默认文件名
filename = 'mnist_train.mat'  # 使用 raw_input() 可以让用户自由输入文件名
# 加载数据
sample = sio.loadmat(filename)
sample = sample["mnist_train"]
# 归一化特征向量
sample /= 256.0

# 同上，读取标签文件
print("输入标签文件名（需放在程序目录下）")
filename = 'mnist_train_labels.mat'  # 使用 raw_input() 可以让用户自由输入文件名
label = sio.loadmat(filename)
label = label["mnist_train_labels"]

#############################################################################################

# 神经网络配置
#############################################################################################
# 获取样本总数
samp_num = len(sample)
# 获取输入层节点数
inp_num = len(sample[0])
# 设置输出节点数
out_num = 10
# 设置隐层节点数,可以调整隐层节点数量
hid_num = 90
# 初始化输入层权矩阵
w1 = 0.2 * np.random.random((inp_num, hid_num)) - 0.1
# 初始化隐层权矩阵
w2 = 0.2 * np.random.random((hid_num, out_num)) - 0.1
# 初始化隐层偏置向量
hid_offset = np.zeros(hid_num)
# 初始化输出层偏置向量
out_offset = np.zeros(out_num)
# 设置输入层权值学习率
inp_lrate = 0.3
# 设置隐层学权值习率
hid_lrate = 0.3
# 设置学习误差门限
err_th = 0.01


#############################################################################################

# 定义必要函数
#############################################################################################
# Sigmoid激活函数
def get_act(x):
    act_vec = []
    for i in x:
        act_vec.append(1 / (1 + math.exp(-i)))
    act_vec = np.array(act_vec)
    return act_vec


# 误差计算函数
def get_err(e):
    return 0.5 * np.dot(e, e)


#############################################################################################

# 训练——可使用err_th与get_err() 配合，提前结束训练过程
#############################################################################################
# 对每个样本进行训练
for count in range(samp_num):
    print(count)
    # 将当前样本的真实标签转换为one-hot编码
    t_label = np.zeros(out_num)
    t_label[label[count]] = 1

    # 前向传播过程
    # 计算隐层值
    hid_value = np.dot(sample[count], w1) + hid_offset
    # 计算隐层激活值
    hid_act = get_act(hid_value)
    # 计算输出层值
    out_value = np.dot(hid_act, w2) + out_offset
    # 计算输出层激活值
    out_act = get_act(out_value)

    # 后向传播过程
    # 计算输出值与真值间的误差
    e = t_label - out_act
    # 计算输出层delta
    out_delta = e * out_act * (1 - out_act)
    # 计算隐层delta
    hid_delta = hid_act * (1 - hid_act) * np.dot(w2, out_delta)
    # 更新隐层到输出层权向量
    for i in range(out_num):
        w2[:, i] += hid_lrate * out_delta[i] * hid_act
    # 更新输入层到隐层的权向量
    for i in range(hid_num):
        w1[:, i] += inp_lrate * hid_delta[i] * sample[count]
    # 更新输出层偏置
    out_offset += hid_lrate * out_delta
    # 更新隐层偏置
    hid_offset += inp_lrate * hid_delta

#############################################################################################

# 测试网络
#############################################################################################
# 读取测试数据文件
filename = 'mnist_test.mat'
test = sio.loadmat(filename)
test_s = test["mnist_test"]
test_s /= 256.0

# 读取测试标签文件
filename = 'mnist_test_labels.mat'
testlabel = sio.loadmat(filename)
test_l = testlabel["mnist_test_labels"]
right = np.zeros(10)  # 正确分类的数字计数器
numbers = np.zeros(10)  # 总共的数字计数器

# 统计测试数据中各个数字的数目
for i in test_l:
    numbers[i] += 1

# 对每个测试样本进行预测
for count in range(len(test_s)):
    # 计算隐层值
    hid_value = np.dot(test_s[count], w1) + hid_offset
    # 计算隐层激活值
    hid_act = get_act(hid_value)
    # 计算输出层值
    out_value = np.dot(hid_act, w2) + out_offset
    # 计算输出层激活值
    out_act = get_act(out_value)
    # 如果预测正确，则增加正确分类的计数
    if np.argmax(out_act) == test_l[count]:
        right[test_l[count]] += 1

# 输出统计结果
print(right)
print(numbers)
result = right / numbers
sum_correct = right.sum()
print(result)
print(sum_correct / len(test_s))

#############################################################################################

# 输出神经网络参数
#############################################################################################
# 创建一个文件来保存神经网络参数
with open("MyNetWork", 'w') as Network:
    Network.write(str(inp_num) + '\n')
    Network.write(str(hid_num) + '\n')
    Network.write(str(out_num) + '\n')
    # 写入输入层到隐层的权重
    for i in w1:
        Network.write(' '.join(map(str, i)) + '\n')
    Network.write('\n')
    # 写入隐层到输出层的权重
    for i in w2:
        Network.write(' '.join(map(str, i)) + '\n')