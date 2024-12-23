import re


def solve(heads, feet):
    # 计算鸡和兔的数量
    for rabbits in range(heads + 1):
        chickens = heads - rabbits
        if (2 * chickens + 4 * rabbits) == feet:
            return chickens, rabbits
    return None, None  # 如果没有解，则返回None


def main():
    # 打开问题文件和答案文件
    with open('questions.txt', 'r') as file, open('answers.txt', 'w') as answer_file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            # 使用正则表达式解析每行数据
            match = re.match(r'Question(\d+):Heads:(\d+),Feet:(\d+)', line.strip())
            if match:
                question_number = int(match.group(1))
                heads = int(match.group(2))
                feet = int(match.group(3))

                # 调用解题函数
                chickens, rabbits = solve(heads, feet)

                # 写入答案
                if chickens is not None and rabbits is not None:
                    answer_file.write(f"Answer{question_number}: Chickens:{chickens},Rabbits:{rabbits}\n")
                else:
                    answer_file.write(f"Answer{question_number}: No solution\n")
            else:
                print(f"Invalid format in line {i + 1}: {line.strip()}")


if __name__ == '__main__':
    main()