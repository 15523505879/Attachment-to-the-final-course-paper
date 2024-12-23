# 获取用户输入的年份范围下界和上界
start_year = int(input("请输入年份下界:"))
end_year = int(input("请输入年份上界:"))

# 遍历年份范围内的每一年，判断是否为闰年并输出
for year in range(start_year, end_year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        print(year)