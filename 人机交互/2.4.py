import random


def generate_question():
    # 随机选择鸡和兔的数量
    x = random.randint(1, 50)  # 鸡的数量
    y = random.randint(1, 50)  # 兔的数量

    # 计算头数和脚数
    heads = x + y
    feet = 2 * x + 4 * y

    return heads, feet


def write_questions_to_file(filename, num_questions=100):
    with open(filename, 'w') as file:
        for i in range(num_questions):
            heads, feet = generate_question()
            file.write(f"Question{i + 1}:Heads:{heads},Feet:{feet}\n")


# 调用函数生成并保存100个问题
write_questions_to_file('questions.txt')