import os
import re
from email.parser import Parser
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string
import xlsxwriter

# 下载停用词资源
nltk.download('stopwords', quiet=True)


def clean_text(text):
    """清理文本数据：移除标点符号、转换为小写、去除非字母字符"""
    text = re.sub(f'[{string.punctuation}]', " ", text)
    text = re.sub("[^\\u4E00-\\u9FA5|^a-z|^A-Z]", " ", text.strip())
    return ' '.join(text.lower().split())


def preprocess_text(text, stemmer, stop_words):
    """预处理文本：清除、分词、移除停用词、提取词干"""
    cleaned_text = clean_text(text)
    tokens = [stemmer.stem(word) for word in cleaned_text.split() if word not in stop_words]
    return tokens


def build_inverted_index(documents):
    """构建倒排索引"""
    inverted_index = defaultdict(list)
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()

    for doc_id, content in documents.items():
        tokens = preprocess_text(content, stemmer, stop_words)
        unique_tokens = dict.fromkeys(tokens)  # 去重

        for token in unique_tokens:
            inverted_index[token].append(doc_id)

    return {k: v for k, v in sorted(inverted_index.items())}


def parse_emails_from_directory(directory):
    """从给定目录中解析所有邮件文件并返回内容字典"""
    documents = {}
    for root, _, files in os.walk(directory):
        for file_name in files:
            with open(os.path.join(root, file_name), 'r', encoding='utf-8', errors='ignore') as file:
                email_content = Parser().parse(file)
                documents[file_name] = email_content.get_payload()
    return documents


def write_inverted_index_to_files(inverted_index, txt_file_path='results.txt', excel_file_path='results.xlsx'):
    """将倒排索引写入文本文件和Excel文件"""
    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        workbook = xlsxwriter.Workbook(excel_file_path)
        worksheet = workbook.add_worksheet()

        # 写入表头
        for doc_id in range(1, len(next(iter(inverted_index.values()), [])) + 1):
            worksheet.write(0, doc_id, doc_id)

        row = 1  # 从第一行开始写入数据
        for word, docs in inverted_index.items():
            txt_file.write(f"{word:<15}\t{len(docs):<10}\t{str(docs):<40}\n")
            worksheet.write(row, 0, word)  # 写入词项

            # 写入文档频率和对应的文档ID
            for doc_id in docs:
                try:
                    col = int(doc_id)  # 确保doc_id是整数
                    worksheet.write(row, col, 1)
                except ValueError:
                    print(f"Warning: Invalid doc_id '{doc_id}', skipping.")

            row += 1

        workbook.close()


def main():
    base_directory = r'hyatt-k'
    emails_content = parse_emails_from_directory(base_directory)
    inverted_index = build_inverted_index(emails_content)
    write_inverted_index_to_files(inverted_index)


if __name__ == '__main__':
    main()