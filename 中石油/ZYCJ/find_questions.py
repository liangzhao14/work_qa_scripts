import pandas as pd

# 读取两份Excel文件
file1 = 'file1.xlsx'  # 第一份Excel文件路径
file2 = 'file2.xlsx'  # 第二份Excel文件路径

# 读取Excel文件中的数据，假设问题列的列名为'question'
df1 = pd.read_excel(file1, usecols=['question'])  # 读取第一份Excel的'question'列
df2 = pd.read_excel(file2, usecols=['question'])  # 读取第二份Excel的'question'列

# 将问题列转换为集合，方便进行差集操作
set1 = set(df1['question'].dropna())  # 第一份Excel的问题集合，去除空值
set2 = set(df2['question'].dropna())  # 第二份Excel的问题集合，去除空值

# 找出第二份Excel中缺少对应第一份Excel的问题
missing_problems = set1 - set2  # 差集操作，找出set1中有而set2中没有的元素

# 将结果转换为DataFrame
result_df = pd.DataFrame(list(missing_problems), columns=['question'])

# 将结果输出到新的Excel文件
output_file = 'missing_problems.xlsx'  # 输出文件路径
result_df.to_excel(output_file, index=False)  # 保存到Excel文件，不保存索引

print(f"结果已保存到 {output_file}")