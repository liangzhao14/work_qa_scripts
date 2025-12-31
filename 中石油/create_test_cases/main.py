import pandas as pd
from openpyxl import Workbook

# 按平台分类的测试用例数据
platforms = {
    "托管子平台": [...],  # 填入上表对应数据
    "数据子平台": [...],
    "标注子平台": [...],
    "训练子平台": [...],
    "推理子平台": [...],
    "运营子平台": [...]
}

with pd.ExcelWriter("AI平台测试用例集.xlsx") as writer:
    for platform, cases in platforms.items():
        df = pd.DataFrame(cases, columns=["一级分类","二级分类","三级分类","功能模块功能点",
                                          "用例标题","前置条件","执行步骤","预期结果",
                                          "用例分级","用例类型","用例适用阶段"])
        df.to_excel(writer, sheet_name=platform, index=False)