import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

file_path = r"D:\data_translate\数据集\en2zh.csv"# 替换为你的文件路径
encoding = detect_encoding(file_path)
print(f"文件编码是: {encoding}")
