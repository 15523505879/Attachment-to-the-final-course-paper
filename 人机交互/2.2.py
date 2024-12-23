import random

# 定义年份范围
start_year = 1500
end_year = 2254

# 生成 100 个随机年份
random_years = [random.randint(start_year, end_year) for _ in range(100)]

# 将生成的年份保存到文件中
with open('years.txt', 'w') as file:
    for year in random_years:
        file.write(f'{year}\n')

print("100 个随机年份已成功保存到 years.txt 文件中。")