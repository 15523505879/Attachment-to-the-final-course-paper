def is_leap_year(year):
    """
    判断给定年份是否为闰年
    """
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False


def read_years_from_file(file_path):
    """
    从文件中读取年份数字
    """
    with open(file_path, 'r') as file:
        years = [int(line.strip()) for line in file]
    return years


def write_results_to_file(file_path, results):
    """
    将结果保存到文件中
    """
    with open(file_path, 'w') as file:
        for year, is_leap in results:
            result_str = f"{year} 是闰年" if is_leap else f"{year} 不是闰年"
            file.write(result_str + '\n')


def main():
    # 读取年份数字
    years = read_years_from_file('years.txt')

    # 判断每个年份是否为闰年
    results = [(year, is_leap_year(year)) for year in years]

    # 将结果保存到文件中
    write_results_to_file('results.txt', results)

    print("结果已成功保存到 results.txt 文件中。")


if __name__ == "__main__":
    main()