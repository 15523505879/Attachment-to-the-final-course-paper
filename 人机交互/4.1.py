import datetime


def main():
    # 获取当前日期和时间
    now = datetime.datetime.now()

    # 显示当前日期和时间
    print("当前日期和时间：", now)

    # 显示当前日期
    today = datetime.date.today()
    print("当前日期：", today)

    # 显示当前时间
    current_time = now.time()
    print("当前时间：", current_time)


if __name__ == '__main__':
    main()