import xlwt
import random


def generate_chicken_rabbit_problem():
    """生成一个鸡兔同笼问题"""
    # 随机生成鸡和兔的数量
    chickens = random.randint(1, 50)
    rabbits = random.randint(1, 50)

    # 计算头数和足数
    heads = chickens + rabbits
    legs = 2 * chickens + 4 * rabbits

    return heads, legs


def main():
    # 创建工作簿
    wb = xlwt.Workbook()

    # 创建sheet对象
    ws = wb.add_sheet('鸡兔同笼题目')

    # 写入表头
    ws.write(0, 0, '序号')
    ws.write(0, 1, '头数')
    ws.write(0, 2, '足数')

    # 生成100道题目并写入Excel
    for i in range(1, 101):
        heads, legs = generate_chicken_rabbit_problem()
        ws.write(i, 0, i)
        ws.write(i, 1, heads)
        ws.write(i, 2, legs)

    # 保存文件
    wb.save('鸡兔同笼题目.xlsx')


if __name__ == '__main__':
    main()