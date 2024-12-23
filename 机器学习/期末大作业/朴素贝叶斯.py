import os
import re
import string
import math
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
import nltk
import logging

# 配置日志记录器以抑制所有日志信息
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

# 禁用特定库的日志信息
for handler in logger.handlers:
    logger.removeHandler(handler)

# 下载停用词列表
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# 定义数据目录路径，不要使用引号
DATA_DIR = r"C:\Users\liu'quan'lin\Desktop\pycharm2023\机器学习\期末大作业\email"
target_names = ['ham', 'spam']

def get_data(DATA_DIR):
    """
    从指定目录加载电子邮件数据

    参数:
        DATA_DIR (str): 包含电子邮件数据集的目录路径

    返回:
        tuple: 包含两个列表的元组，一个用于存储邮件内容，另一个用于存储对应的标签
    """
    # 定义子文件夹名
    subfolders = {'ham': 'easy-ham', 'spam': 'spam'}
    data = []
    target = []

    # 遍历每个子文件夹
    for label, subfolder in subfolders.items():
        folder_path = os.path.join(DATA_DIR, subfolder)

        # 检查目录是否存在
        if not os.path.exists(folder_path):
            print(f"错误: 目录 {folder_path} 不存在.")
            return [], []

        files = os.listdir(folder_path)
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, encoding="latin-1") as f:
                    data.append(f.read())
                    target.append(1 if label == 'spam' else 0)
            except FileNotFoundError:
                print(f"错误: 文件 {file_path} 未找到.")
            except PermissionError:
                print(f"错误: 访问文件 {file_path} 权限被拒绝.")
            except Exception as e:
                print(f"读取文件 {file_path} 时出错: {e}")

    return data, target

# 打印当前工作目录，方便调试
print(f"当前工作目录: {os.getcwd()}")

# 获取数据
X, y = get_data(DATA_DIR)

if not X or not y:
    print("没有加载到数据，退出程序...")
    exit()

# 分割数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

class SpamDetectorBase(object):
    """实现朴素贝叶斯分类器的基本类"""

    def clean(self, s):
        """去除输入字符串中的标点符号"""
        translator = str.maketrans("", "", string.punctuation)
        return s.translate(translator)

    def tokenize(self, text):
        """清理并分割文本为单词"""
        text = self.clean(text).lower()
        tokens = re.split("\W+", text)
        stop_words = set(stopwords.words('english'))
        return [word for word in tokens if word and word not in stop_words]

    def get_word_counts(self, words):
        """统计每个单词出现的次数"""
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0.0) + 1.0
        return word_counts

class SpamDetectorTrainer(SpamDetectorBase):
    """训练朴素贝叶斯模型的类"""

    def fit(self, X, Y):
        """
        在提供的数据集上训练朴素贝叶斯模型

        参数:
            X (list): 邮件文本列表
            Y (list): 对应的标签（1表示垃圾邮件，0表示正常邮件）
        """
        self.num_messages = {'spam': 0, 'ham': 0}
        self.log_class_priors = {'spam': 0.0, 'ham': 0.0}
        self.word_counts = {'spam': {}, 'ham': {}}
        self.vocab = set()

        # 统计垃圾邮件和正常邮件的数量
        self.num_messages['spam'] = sum(1 for label in Y if label == 1)
        self.num_messages['ham'] = sum(1 for label in Y if label == 0)

        # 确保两个类别都有样本，避免除以零
        if self.num_messages['spam'] == 0 or self.num_messages['ham'] == 0:
            print("错误: 其中一个类别为空，无法继续训练.")
            return

        # 计算先验概率
        total_messages = self.num_messages['spam'] + self.num_messages['ham']
        self.log_class_priors['spam'] = math.log(self.num_messages['spam'] / total_messages)
        self.log_class_priors['ham'] = math.log(self.num_messages['ham'] / total_messages)

        # 收集每个类别的词频
        for x, y in zip(X, Y):
            c = 'spam' if y == 1 else 'ham'
            word_counts = self.get_word_counts(self.tokenize(x))
            for word, count in word_counts.items():
                self.vocab.add(word)
                if word not in self.word_counts[c]:
                    self.word_counts[c][word] = 0.0
                self.word_counts[c][word] += count

        print(f"训练完成，词汇表大小: {len(self.vocab)}")
        print(f"垃圾邮件数量: {self.num_messages['spam']}")
        print(f"正常邮件数量: {self.num_messages['ham']}")

class SpamDetectorPredictor(SpamDetectorTrainer):
    """使用训练好的朴素贝叶斯模型进行预测的类"""

    def predict(self, X):
        """
        预测每封邮件是垃圾邮件还是正常邮件

        参数:
            X (list): 要分类的邮件文本列表

        返回:
            list: 预测结果（1表示垃圾邮件，0表示正常邮件）
        """
        results = []
        for x in X:
            word_counts = self.get_word_counts(self.tokenize(x))
            spam_score = self.log_class_priors['spam']
            ham_score = self.log_class_priors['ham']

            for word, _ in word_counts.items():
                if word not in self.vocab:
                    continue

                # 应用拉普拉斯平滑
                spam_count = self.word_counts['spam'].get(word, 0) + 1
                ham_count = self.word_counts['ham'].get(word, 0) + 1
                total_spam_words = sum(self.word_counts['spam'].values()) + len(self.vocab)
                total_ham_words = sum(self.word_counts['ham'].values()) + len(self.vocab)

                log_w_given_spam = math.log(spam_count / total_spam_words)
                log_w_given_ham = math.log(ham_count / total_ham_words)

                spam_score += log_w_given_spam
                ham_score += log_w_given_ham

            # 根据得分确定预测类别
            if spam_score > ham_score:
                results.append(1)
            else:
                results.append(0)

        return results

# 初始化并训练垃圾邮件检测器
MNB = SpamDetectorPredictor()
MNB.fit(X_train, y_train)

# 在测试集上做预测
predictions = MNB.predict(X_test)
true_labels = y_test

# 计算准确率
accuracy = sum(1 for p, t in zip(predictions, true_labels) if p == t) / len(true_labels)
print(f"准确率: {accuracy * 100:.2f}%")

# 计算精确率、召回率和F1分数
precision = precision_score(true_labels, predictions, zero_division=0)
recall = recall_score(true_labels, predictions, zero_division=0)
f1 = f1_score(true_labels, predictions, zero_division=0)

print(f'精确率: {precision:.3f}')
print(f'召回率: {recall:.3f}')
print(f'F1分数: {f1:.3f}')