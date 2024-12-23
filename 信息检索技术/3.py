import ast
from tkinter import messagebox
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

inverted_index = {}

def load_inverted_index(filename):
    pattern = re.compile(r'^"(\w+)"\s+(\d+)\s+\[(.*?)\]$', re.UNICODE)

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, start=1):
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith('#'):
                    continue

                match = pattern.match(stripped_line)
                if match:
                    term, doc_count_str, doc_list_str = match.groups()
                    # Ensure the document list is properly parsed as a list of integers
                    try:
                        doc_list = [int(doc_id.strip().strip("'").strip('"')) for doc_id in doc_list_str.split(',')]
                        inverted_index[term] = [int(doc_count_str), doc_list]
                        print(f"成功加载项 (Line {line_num}): {term}, 文档数量: {doc_count_str}, 文档列表: {doc_list}")
                    except ValueError as e:
                        print(f"解析错误 (Line {line_num}): {e}, 内容: {stripped_line}")
                else:
                    # Try to handle lines that might have extra spaces or tabs
                    parts = stripped_line.split(maxsplit=2)
                    if len(parts) == 3:
                        term = parts[0].strip('"')
                        doc_count_str = parts[1]
                        doc_list_str = parts[2]
                        try:
                            doc_list = [int(doc_id.strip().strip("'").strip('"')) for doc_id in doc_list_str.strip('[]').split(',')]
                            inverted_index[term] = [int(doc_count_str), doc_list]
                            print(f"成功加载项 (Line {line_num}): {term}, 文档数量: {doc_count_str}, 文档列表: {doc_list}")
                        except ValueError as e:
                            print(f"解析错误 (Line {line_num}): {e}, 内容: {stripped_line}")
                    else:
                        print(f"跳过格式不正确的行 (Line {line_num}): {repr(stripped_line)}")

        print("倒排索引加载完成，部分数据如下：")
        for term, (count, docs) in list(inverted_index.items())[:5]:
            print(f"Term: {term}, Doc Count: {count}, Docs: {docs}")

    except Exception as e:
        print("加载倒排索引时出错:", str(e))

    return inverted_index


def perform_and_search(query_terms):
    result_sets = [set(inverted_index.get(term, [0, []])[1]) for term in query_terms]
    return set.intersection(*result_sets) if result_sets else set()


def perform_or_search(query_terms):
    result_sets = [set(inverted_index.get(term, [0, []])[1]) for term in query_terms]
    return set.union(*result_sets) if result_sets else set()


def perform_not_search(query_terms):
    if len(query_terms) != 2:
        messagebox.showinfo("错误", "NOT 操作需要两个词项。")
        return set()

    term1, term2 = query_terms
    doc_set1 = set(inverted_index.get(term1, [0, []])[1])
    doc_set2 = set(inverted_index.get(term2, [0, []])[1])
    return doc_set1 - doc_set2


def perform_search(query):
    query = query.lower().replace(" and ", " AND ").replace(" or ", " OR ").replace(" not ", " NOT ")
    query_terms = query.split()

    def get_doc_set(term):
        return set(inverted_index.get(term, [0, []])[1])

    results = None
    i = 0
    while i < len(query_terms):
        term = query_terms[i]

        if term.upper() == "AND":
            if results is None:
                results = get_doc_set(query_terms[i - 1])
            results &= get_doc_set(query_terms[i + 1])
            i += 2
        elif term.upper() == "OR":
            if results is None:
                results = get_doc_set(query_terms[i - 1])
            results |= get_doc_set(query_terms[i + 1])
            i += 2
        elif term.upper() == "NOT":
            if results is None:
                results = get_doc_set(query_terms[i - 1])
            results -= get_doc_set(query_terms[i + 1])
            i += 2
        else:
            if results is None:
                results = get_doc_set(term)
            i += 1

    return results if results is not None else set()


def retrieve_documents(query, tfidf_matrix, documents):
    query_vector = tfidf_vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    doc_scores = list(zip(documents, similarities))
    doc_scores.sort(key=lambda x: x[1], reverse=True)
    return doc_scores


def evaluate_search(expected_results):
    overall_tp, overall_fp, overall_fn = 0, 0, 0

    for query, expected in expected_results.items():
        retrieved_docs = perform_search(query)
        tp = len(retrieved_docs & set(expected))
        fp = len(retrieved_docs) - tp
        fn = len(expected) - tp

        p = tp / (tp + fp) if tp + fp > 0 else 0
        r = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * (p * r) / (p + r) if p + r > 0 else 0

        print(f"查询: '{query}'\n检索结果: {retrieved_docs}\n预期结果: {set(expected)}")
        print(f"精度（P）: {p:.2f}\n召回率（R）: {r:.2f}\nF1分数（F1）: {f1:.2f}\n")

        overall_tp += tp
        overall_fp += fp
        overall_fn += fn

    overall_p = overall_tp / (overall_tp + overall_fp) if overall_tp + overall_fp > 0 else 0
    overall_r = overall_tp / (overall_tp + overall_fn) if overall_tp + overall_fn > 0 else 0
    overall_f1 = 2 * (overall_p * overall_r) / (overall_p + overall_r) if overall_p + overall_r > 0 else 0

    print("整体评估:")
    print(f"整体精度（P）: {overall_p:.2f}")
    print(f"整体召回率（R）: {overall_r:.2f}")
    print(f"整体F1分数（F1）: {overall_f1:.2f}")


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text


if __name__ == "__main__":
    folder_path = r'hyatt-k\contacts'
    corpus = []
    documents = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                document_content = file.read()
                processed_content = preprocess_text(document_content)
                corpus.append(processed_content)
                documents.append(filename)

    if not corpus:
        print("未从指定路径加载到任何文档，请检查路径或文件是否存在。")
    else:
        for i, doc in enumerate(corpus[:5], start=1):
            print(f"Document {i} content (first 100 chars):\n{doc[:100]}\n")

        tfidf_vectorizer = TfidfVectorizer(stop_words=None, token_pattern=r'(?u)\b\w+\b', min_df=1, max_df=1.0)
        try:
            tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
            terms = tfidf_vectorizer.get_feature_names_out()

            for doc_id, doc in enumerate(corpus):
                print(f"Document: {documents[doc_id]}")
                for term_id, term in enumerate(terms):
                    tfidf_weight = tfidf_matrix[doc_id, term_id]
                    print(f"Term: {term}, TF-IDF Weight: {tfidf_weight}")
        except ValueError as e:
            print("构建TF-IDF矩阵时出错:", str(e))

    inverted_index_filename = r'results.txt'

    if os.path.exists(inverted_index_filename):
        print(f"文件 {inverted_index_filename} 存在，继续加载...")

        with open(inverted_index_filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            print("文件中的前几行：")
            for i, line in enumerate(lines[:5], start=1):  # 打印前五行作为示例
                print(f"Line {i}: {repr(line.strip())}")  # 使用 repr 显示所有字符
        inverted_index = load_inverted_index(inverted_index_filename)

        test_terms = ['zzz', 'zvae']
        for term in test_terms:
            if term in inverted_index:
                print(f"Term: {term}, Docs: {inverted_index[term][1]}")
            else:
                print(f"Term: {term} not found in inverted index.")

        expected_results = {
            "zzz AND zvae": {449},
            "zzz OR zvae": {416, 449, 613, 648, 333, 623, 434, 532, 476, 478},
            "zzz NOT zvae": {555},
        }

        evaluate_search(expected_results)
    else:
        print(f"文件 {inverted_index_filename} 不存在，请检查路径。")



