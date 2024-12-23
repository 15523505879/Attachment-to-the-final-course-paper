def is_leap_year(year):
    # 判断年份是否为闰年
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


# 主程序
if __name__ == "__main__":
    # 获取用户输入
    year = int(input("请输入一个年份:"))

    # 判断是否为闰年并输出结果
    if is_leap_year(year):
        print(f"{year}是闰年")
    else:
        print(f"{year}不是闰年")