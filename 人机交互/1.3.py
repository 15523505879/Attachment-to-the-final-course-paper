# Python程序，解决鸡兔同笼问题

# 获取用户输入的头和脚的数量
heads = int(input("输入头的数量:"))
feet = int(input("输入脚的数量:"))


# 计算鸡和兔的数量
def solve_chicken_rabbit(heads, feet):
    rabbit_count = (feet - 2 * heads) / 2
    chicken_count = heads - rabbit_count
    return int(chicken_count), int(rabbit_count)


# 输出鸡和兔的数量
chickens, rabbits = solve_chicken_rabbit(heads, feet)
print(f"鸡:{chickens}只  兔:{rabbits}只")
