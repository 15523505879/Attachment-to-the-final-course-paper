import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score

# 定义超参数
EPOCH = 3  # 训练的总轮数
BATCH_SIZE = 50  # 每批数据的数量
LR = 0.01  # 学习率
DOWNLOAD_MNIST = True  # 是否下载MNIST数据集

# 数据预处理转换
transform = transforms.Compose([
    transforms.ToTensor(),  # 将图像数据转换为张量，并将像素值从[0, 255]缩放到[0, 1]
])

# 加载训练数据集
train_data = torchvision.datasets.MNIST(
    root='./mnist',  # 数据保存路径
    train=True,  # 表示这是训练集
    transform=transform,  # 应用上述定义的数据转换
    download=DOWNLOAD_MNIST  # 如果本地没有数据集，则下载
)

# 输出训练数据的一些信息
print(f"训练数据形状: {train_data.data.size()}")
print(f"训练标签形状: {train_data.targets.size()}")
print(f"第一个训练样本的像素值: {train_data.data[0]}")

# 显示一个训练样本的图片
plt.imshow(train_data.data[0].numpy(), cmap='gray')
plt.title(f'Label: {train_data.targets[0].item()}')  # 使用.item()获取单个数值
plt.show()

# 创建DataLoader用于迭代加载训练数据
train_loader = DataLoader(dataset=train_data, batch_size=BATCH_SIZE, shuffle=True)

# 加载测试数据集
test_data = torchvision.datasets.MNIST(
    root='./mnist',
    train=False,
    transform=transform
)

# 准备测试数据（只取前3000个样本）
test_x = test_data.data[:3000].unsqueeze(1).float() / 255  # 归一化到[0, 1]范围，并且增加通道维度
test_y = test_data.targets[:3000]

# 定义卷积神经网络模型
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()

        # 第一层卷积层 + ReLU激活函数 + 最大池化层
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=5, stride=1, padding=2),  # 输入通道数为1，输出通道数为16
            nn.ReLU(),  # 激活函数
            nn.MaxPool2d(kernel_size=2)  # 池化窗口大小为2x2
        )

        # 第二层卷积层 + ReLU激活函数 + 最大池化层
        self.layer2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )

        # 全连接层，输入是32*7*7维，输出是10类别的预测结果
        self.fc = nn.Linear(32 * 7 * 7, 10)

    def forward(self, x):
        # 前向传播过程，通过两个卷积层后展平输入全连接层
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.view(out.size(0), -1)  # 展平多维张量成二维张量
        out = self.fc(out)
        return out


cnn = CNN()
print(cnn)  # 打印网络结构

# 定义优化器和损失函数
optimizer = optim.Adam(cnn.parameters(), lr=LR)  # Adam优化器
loss_fn = nn.CrossEntropyLoss()  # 交叉熵损失函数，适用于分类问题

# 开始训练
for epoch in range(EPOCH):  # 遍历所有epoch
    for step, (batch_x, batch_y) in enumerate(train_loader):  # 遍历每个batch的数据
        # 前向传播计算预测值，并计算损失
        outputs = cnn(batch_x)  # 获取预测输出
        loss = loss_fn(outputs, batch_y)  # 计算损失

        # 反向传播更新权重
        optimizer.zero_grad()  # 清空上一步的残余更新参数值
        loss.backward()  # 误差反向传播, 计算参数更新值
        optimizer.step()  # 更新所有参数

        # 每隔50步打印一次当前的训练状态
        if step % 50 == 0:
            with torch.no_grad():  # 禁用梯度计算以加速评估过程
                # 在测试集上评估模型性能
                test_outputs = cnn(test_x)
                predicted = torch.max(test_outputs, 1)[1]  # 获取最大概率对应的类别索引作为预测结果

                # 计算准确率
                correct = (predicted == test_y).sum().item()
                total = test_y.size(0)
                accuracy = correct / total

                print(
                    f'Epoch [{epoch + 1}/{EPOCH}], Step [{step + 1}], Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}')

# 测试模型在测试集上的表现
with torch.no_grad():
    test_output = cnn(test_x)  # 对全部测试样本进行预测
    y_pred = torch.max(test_output, 1)[1].data.squeeze()

    # 计算整体准确率、精确率和召回率
    overall_accuracy = (y_pred == test_y).sum().item() / len(test_y)
    precision = precision_score(test_y.numpy(), y_pred.numpy(), average='weighted')
    recall = recall_score(test_y.numpy(), y_pred.numpy(), average='weighted')

    print('预测结果:', y_pred.tolist())
    print('真实结果:', test_y.tolist())

    print(f'测试集准确率: {overall_accuracy:.4f}')
    print(f'测试集精确率: {precision:.4f}')
    print(f'测试集召回率: {recall:.4f}')



