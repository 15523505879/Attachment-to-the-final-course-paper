import re


class InvertedIndex:
    def __init__(self, file_path):
        self.hashtable = {}
        self._build_index(file_path)

    def _build_index(self, file_path):
        with open(file_path) as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split('\t')
                if len(parts) != 3:
                    continue
                word, freq_str, doc_ids_str = parts
                word = word.strip()
                doc_ids = [int(doc_id.strip("[]' ")) for doc_id in doc_ids_str.strip().split(", ") if doc_id.strip()]
                self.hashtable[word] = doc_ids

    def get_list(self, word):
        return self.hashtable.get(word, [])


def intersect(list1, list2):
    """计算两个列表的交集"""
    set1 = set(list1)
    set2 = set(list2)
    return list(set1.intersection(set2))


def main():
    # 构建倒排索引
    inverted_index = InvertedIndex('results.txt')

    while True:
        print("请输入第一个单词（或输入 'exit' 退出）：", end='')
        word1 = input().strip().lower()
        if word1 == 'exit':
            break

        print("请输入第二个单词：", end='')
        word2 = input().strip().lower()

        # 获取两个单词的倒排记录表
        list1 = inverted_index.get_list(word1)
        list2 = inverted_index.get_list(word2)

        # 计算交集
        common_docs = intersect(list1, list2)

        if common_docs:
            print(f"单词 '{word1}' 和 '{word2}' 在以下文档中共现: {common_docs}")
        else:
            print(f"单词 '{word1}' 和 '{word2}' 没有在任何相同文档中共现.")


if __name__ == "__main__":
    main()