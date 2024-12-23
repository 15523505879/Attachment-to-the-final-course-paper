import calendar


def get_days_in_month(year, month):
    """获取指定年份和月份的总天数"""
    _, days = calendar.monthrange(year, month)
    return days


def main():
    # 读取输入
    year = int(input("请输入年份: "))
    month = int(input("请输入月份: "))

    # 获取该月的总天数
    days = get_days_in_month(year, month)

    # 输出结果
    print(days)


if __name__ == '__main__':
    main()
