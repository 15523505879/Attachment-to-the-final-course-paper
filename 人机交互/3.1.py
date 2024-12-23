import json


def main():
    # 初始化计数器
    total_count = 0
    male_count = 0
    female_count = 0
    mask_count = 0
    no_mask_count = 0

    # 打开并读取文件
    with open('results.txt', 'r') as file:
        lines = file.readlines()

        for line in lines:
            # 去除行尾的换行符和多余的逗号
            line = line.strip().rstrip(',')

            # 尝试将 JSON 字符串转换为字典
            try:
                data = json.loads(line)
                print(f"Parsed data: {data}")  # 打印解析结果，方便调试
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e} in line: {line}")
                continue

            # 统计总人数
            total_count += 1

            # 统计性别
            if data['gender'] == '男':
                male_count += 1
            elif data['gender'] == '女':
                female_count += 1

            # 统计口罩情况
            if data['口罩'] == '带':
                mask_count += 1
            elif data['口罩'] == '不带':
                no_mask_count += 1

    # 输出结果
    print(f"总人数: {total_count}")
    print(f"男性人数: {male_count}")
    print(f"女性人数: {female_count}")
    print(f"戴口罩人数: {mask_count}")
    print(f"没戴口罩人数: {no_mask_count}")


if __name__ == '__main__':
    main()