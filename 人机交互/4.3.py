import datetime


def day_of_year(year, month, day):
    """计算输入日期是当年的第几天"""
    # 创建输入日期的 datetime 对象
    input_date = datetime.date(year, month, day)

    # 创建该年 1 月 1 日的 datetime 对象
    start_of_year = datetime.date(year, 1, 1)

    # 计算输入日期与 1 月 1 日之间的天数差
    delta = input_date - start_of_year

    # 返回天数差 + 1（因为 1 月 1 日是第 1 天）
    return delta.days + 1


def main():
    # 读取输入
    year, month, day = map(int, input("请输入年、月、日（中间用空格分隔）: ").split())

    # 计算该日是当年的第几天
    day_number = day_of_year(year, month, day)

    # 输出结果
    print(day_number)


if __name__ == '__main__':
    main()