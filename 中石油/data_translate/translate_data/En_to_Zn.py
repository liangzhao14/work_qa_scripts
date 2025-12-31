import csv
from collections import Counter


# 读取CSV文件
def read_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader][1:]  # 跳过标题行


# 按照中文内容的长度降序排列
def sort_by_chinese_length(data):
    # 使用Counter来统计每个中文翻译的长度
    translation_lengths = Counter()
    for row in data:
        if len(row) > 1:
            translation_lengths[row[1]] = len(row[1])

    # 按照长度降序排列
    sorted_translations = sorted(translation_lengths.items(), key=lambda x: x[1], reverse=True)
    return [[english, translation] for translation, _ in sorted_translations for english in
            [row[0] for row in data if row[1] == translation]]


# 写入新的CSV文件
def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='', encoding='GB18030') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['英文', '中文'])  # 写入标题行
        writer.writerows(data)


# 主函数
def main():
    input_file = r"D:\data_translate\数据集\en2zh.csv" # 请替换为你的输入文件路径
    output_file = r"D:\data_translate\数据集\output_en.csv"  # 输出CSV文件名

    data = read_csv(input_file)
    sorted_data = sort_by_chinese_length(data)
    write_to_csv(sorted_data, output_file)
    print(f"CSV文件已生成：{output_file}")


if __name__ == "__main__":
    main()
