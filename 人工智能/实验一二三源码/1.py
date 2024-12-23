# 特征数组
characteristics = [
    "毛发", "奶", "羽毛", "会飞", "吃肉", "犬齿", "有爪", "眼盯前方", "有蹄",
    "反刍动物", "哺乳动物", "鸟", "善飞", "信天翁", "食肉动物", "黄褐色", "暗斑点",
    "黑色条纹", "长腿", "长脖子", "有蹄类动物", "虎", "金钱豹", "长颈鹿", "斑马",
    "不会飞", "黑白二色", "会游泳", "鸵鸟", "企鹅", "下蛋"
]

# 规则库定义，包含规则编号和描述
rules = {
    "r1": lambda d: ("哺乳动物", "r1") if "毛发" in d or "奶" in d else None,
    "r2": lambda d: ("鸟", "r2") if "羽毛" in d else ("鸟", "r4") if "会飞" in d and "下蛋" in d else None,
    "r3": lambda d: ("食肉动物", "r5") if "吃肉" in d else (
        "食肉动物", "r6") if "犬齿" in d and "有爪" in d and "眼盯前方" in d else None,
    "r4": lambda d: ("有蹄类动物", "r7") if "哺乳动物" in d and "有蹄" in d else (
        "有蹄类动物", "r8") if "哺乳动物" in d and "反刍动物" in d else None,
    "r5": lambda d: (
        "金钱豹", "r9") if "哺乳动物" in d and "食肉动物" in d and "黄褐色" in d and "暗斑点" in d else None,
    "r6": lambda d: (
        "虎", "r10") if "哺乳动物" in d and "食肉动物" in d and "黄褐色" in d and "黑色条纹" in d else None,
    "r7": lambda d: ("虎", "r9") if "食肉动物" in d and "黄褐色" in d and "黑色条纹" in d else None,  # 调整规则以允许直接推断虎
    "r8": lambda d: ("斑马", "r12") if "有蹄类动物" in d and "黑色条纹" in d else None,
    "r9": lambda d: ("鸵鸟", "r13") if "鸟" in d and "长脖子" in d and "长腿" in d and "不会飞" in d else None,
    "r10": lambda d: ("企鹅", "r14") if "鸟" in d and "会游泳" in d and "不会飞" in d and "黑白二色" in d else None,
    "r11": lambda d: ("信天翁", "r15") if "鸟" in d and "善飞" in d else None,
    "r12": lambda d: ("长脖子", "r16") if "鸟" in d and "不会飞" and "长腿" in d else None,  # 推断长脖子
    "r13": lambda d: ("长腿", "r17") if "鸟" in d and "长脖子" in d and "不会飞" in d else None,  # 新增规则：推断长腿
    "r14": lambda d: ("黑白二色", "r18") if "鸟" in d and "会游泳" in d and "不会飞" in d else None,
    "r15": lambda d: ("哺乳动物", "r19") if "食肉动物" in d and "黄褐色" in d and "暗斑点" in d else None,
}


def extract_features(text):
    features = [char for char in characteristics if char in text]
    # 移除矛盾的特征
    if "会飞" in features and "不会飞" in features:
        features.remove("会飞")  # 优先保留“不会飞”
    return features


def apply_rules(features):
    all_conclusions = []
    new_conclusions = True

    while new_conclusions:
        new_conclusions = False
        for rule_id, rule_func in rules.items():
            conclusion = rule_func(features)
            if conclusion and conclusion[0] not in features:
                feature, rule_name = conclusion
                print(f"根据规则 {rule_name} 推断出该动物是：{feature}")
                features.append(feature)  # 添加新推导出的结论作为特征
                all_conclusions.append((feature, rule_name))
                new_conclusions = True

    # 确保最终结论是最具体的（例如：鸵鸟）
    specific_conclusions = ["虎", "金钱豹", "斑马", "长颈鹿", "鸵鸟", "企鹅", "信天翁"]
    final_conclusion = next((c for c, _ in all_conclusions if c in specific_conclusions), None)

    return [(c, r) for c, r in all_conclusions if c == final_conclusion] if final_conclusion else []


def main():
    print("请输入描述语句：")
    S = input()
    describe = extract_features(S)

    print("\n提取或者总结的特征：")
    print(describe)

    print("\n推理过程：")
    conclusions = apply_rules(describe)
    for c, rule_name in conclusions:
        print(f"根据规则 {rule_name} 推断出该动物是：{c}")

    print("\n结论：")
    if conclusions:
        print("该动物是：" + ", ".join(c for c, _ in conclusions))
    else:
        print("无法判断是什么动物！")


if __name__ == "__main__":
    main()
