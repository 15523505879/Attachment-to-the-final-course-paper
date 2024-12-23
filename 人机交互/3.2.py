def read_file(file_path):
    """读取文件内容，返回一个包含所有行的列表"""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]


def is_palindrome(s):
    """判断字符串 s 是否是回文"""
    queue = []
    stack = []

    # 将字符串中的字符依次加入队列和栈
    for char in s:
        queue.append(char)
        stack.append(char)

    # 比较队列和栈中的字符
    while queue:
        if queue.pop(0) != stack.pop():
            return False
    return True


def main():
    # 读取文件内容
    lines = read_file('questions_hwpd.txt')

    # 判断每一行是否是回文
    for line in lines:
        if is_palindrome(line):
            print(f"'{line}' 是回文")
        else:
            print(f"'{line}' 不是回文")


if __name__ == '__main__':
    main()