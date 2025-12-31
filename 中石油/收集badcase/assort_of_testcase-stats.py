# -*- coding: utf-8 -*-
import os
import json
import time
from openai import OpenAI
import pandas as pd
import concurrent.futures

class AssortTestcase:
    def __init__(self,file_path):
        start_time = int(time.time())
        self.outputData = []
        self.columns = ["Id", "question", "sort", "category"]
        self.file_path = file_path
        self.sort_mapping = {
            1: "事实提取",
            2: "概念解释",
            3: "因果关系",
            4: "假设情景",
            5: "比较分析",
            6: "逻辑推理"
        }

    def chat_to_professional_model(self,role,prompt,temperature,top_p):
        try:
            client = OpenAI(api_key="sk-PhVffqMthHNiJS7L00Aa4cAc999a40B593431a2120AdA504",
                        base_url="http://124.71.167.110:8083/v1")
            use_model = "deepseek-r1-volcengine"
            response = client.chat.completions.create(
                model=use_model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                top_p=top_p,
                stream=False,
                timeout=600
            )
            LLManswer = response.choices[0].message.content
            if response.choices[0].message.model_extra['reasoning_content']:
                think = response.choices[0].message.model_extra['reasoning_content']
            else:
                think = None
            return LLManswer,think

        except Exception as e:
            print(f"chat_to_professional_model fail: {e}")
            raise Exception("chat_to_professional_model fail")

#    def chat_to_professional_model(self,role, prompt, temperature, top_p):
#        client = OpenAI(api_key="mEwS9dwMxOtKzP32zN9dBpkdyNo2tgxL",
#                        base_url="http://10.54.102.5:80/xlm-gateway-zpvhcl/sfm-api-gateway/gateway/compatible-mode/v1")
#        use_model = "qwen2---5-72b-dqydcbdv"
#        response = client.chat.completions.create(
#            model=use_model,
#            messages=[
#                {"role": "system", "content": role},
#                {"role": "user", "content": prompt},
#            ],
#            stream=False,
#            temperature=temperature,
#            top_p=top_p
#        )
#        LLManswer = response.choices[0].message.content
#        return LLManswer

    def assort(self,question):
        role = """### 角色设定
                    你是一名**问题类型仲裁官**，专精于对学术/技术问题进行机械式分类。你的核心能力：
                    1. **绝对规则遵循者**：严格绑定用户提供的6类定义，禁止任何主观扩展
                    2. **边界扫描仪**：能敏锐识别问题中的关键特征词（如“比较”“为什么”“如果”“计算”）
                    3. **决策机器**：当存在多类别特征时，自动触发优先级仲裁机制：
                       - 出现「推理/计算」关键词 → 强制锁定逻辑推理(6)
                       - 含假设条件词（如果/假设）→ 优先假设情景(4)
                       - 因果疑问词（为什么/如何导致）→ 优先因果关系(3)
                       - 比较类动词（对比/区别/优劣）→ 强制比较分析(5)
                    4. **零解释执行者**：永远只输出JSON格式结果
                    """

        prompt = rf"""
                    **任务：** 请严格依据以下分类体系，对输入的问题进行单一类别判定。
                    
                    **输出要求：**
                    *   **仅输出一个最匹配的类别编号（1-6）。**
                    *   **输出格式：`{{"category": 数字}}`** (例如：`{{"category": 3}}`)
                    *   请**严格遵循**分类定义，避免主观臆断。如果一个问题可勉强划入多个类别，选择**最核心、最显著**的特征对应的类别。
                    *   如果问题完全不符合任何类别，输出 `{{"category": 0}}` (但这种情况应尽量避免，请尽力匹配)。
                    
                    **工作流程：**
                    1. 接收问题文本
                    2. 扫描关键词 → 匹配特征矩阵 
                        1.  **事实提取：** 问题要求直接提取数据、定义、事实信息（如“XX是什么？”、“XX的具体数值是多少？”）。答案通常直接存在于已知信息源中，无需解释或推理。
                        2.  **概念解释：** 问题要求解释术语、原理、理论或概念的含义、背景或机制（如“请解释XX的含义”、“XX的工作原理是什么？”）。侧重于理解性说明。
                        3.  **因果关系：** 问题明确询问原因、结果或机制，包含“为什么”、“如何导致”、“XX的原因/影响是什么？”等关键词。核心是探究事物间的因果链条。
                        4.  **假设情景：** 问题基于一个虚构或改变的条件进行发问，通常以“如果...会怎样？”、“假设...那么...？”开头。答案需要基于逻辑或知识推测在特定条件下的结果。
                        5.  **比较分析：** 问题要求对比两个或多个事物（数据、概念、方案、方法等）的异同、优劣或关系（如“比较A和B的区别”、“X与Y相比哪个更好？为什么？”）。核心是识别和评估差异与联系。
                        6.  **逻辑推理：** 问题无法通过直接查找或简单解释解决，**必须**经过多步逻辑推理、计算、推断或综合信息才能得出答案（如“根据上述信息，下一步应该怎么做？”、“计算XX的值”、“推理出XX的结论”）。答案依赖于推理过程。
                    3. 无冲突特征 → 按基础定义归类
                    4. 特征冲突 → 触发优先级仲裁
                    5. 输出 {{"category":数字}}
                    
                    **禁忌：** 
                    禁止添加任何说明文字
                    禁止输出非JSON格式
                    禁止创建新类别（未知问题返回0）
                    
                    **问题：** `{question["question"]}`
                    
                    **分类结果：**
                """
        llm_answer = self.chat_to_professional_model(role,prompt,0.2,0.75)
        print(llm_answer)

        category_text = llm_answer[0].strip()
        if category_text.startswith("```json"):
            category_text = category_text[len("```json") : -len("```")].strip()
        else:
            category_text = category_text.strip()
        category = json.loads(category_text).get("category", "")

        item = [question["Id"] ,question["question"], llm_answer, category]
        self.outputData.append(item)
        return  llm_answer

    def generate_stats(self, df):
        """生成sort值的统计数据"""
        if 'sort' not in df.columns:
            return pd.DataFrame()
        
        # 统计各sort值的数量
        stats = df['sort'].value_counts().reset_index()
        stats.columns = ['sort_value', 'count']
        
        # 计算占比
        total = stats['count'].sum()
        stats['percentage'] = (stats['count'] / total * 100).round(2).astype(str) + '%'
        
        # 添加类型说明
        stats['type_name'] = stats['sort_value'].map(self.sort_mapping)
        
        # 重新排列列顺序
        stats = stats[['sort_value', 'type_name', 'count', 'percentage']]
        stats = stats.sort_values('sort_value')
        
        return stats

    def create_excel(self):
        print("output excel...")
        df_output = pd.DataFrame(self.outputData, columns=self.columns)

        # 生成统计数据
        stats_df = self.generate_stats(df_output)

        # 检查文件是否存在
        if os.path.exists(self.file_path):
            # 如果文件存在,则以追加模式打开
            writer = pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay')
            # 读取原有数据
            existing_data = pd.read_excel(self.file_path, sheet_name='Sheet1')
            # 合并新旧数据
            combined_data = pd.concat([existing_data, pd.DataFrame(self.outputData, columns=self.columns)],
                                      ignore_index=True)
            # 将合并后的数据写入Excel
            combined_data.to_excel(writer, sheet_name='Sheet1', index=False, header=True)
            stats_df.to_excel(writer, sheet_name='Sheet2', index=False, header=True)
        else:
            # 如果文件不存在,则创建一个新的
            writer = pd.ExcelWriter(self.file_path, engine='openpyxl')
            # 创建DataFrame并写入Excel
            df = pd.DataFrame(data=self.outputData, columns=self.columns)
            df.to_excel(writer, sheet_name='Sheet1', index=False, header=True)
            stats_df.to_excel(writer, sheet_name='Sheet2', index=False, header=True)
        writer.close()
        print("Excel已输出.")

class Thread:
    def __init__(self):
        df = pd.read_excel(r'testcase.xlsx')
        #self.questions = df.iloc[:, 0].tolist()
        self.questions = df.to_dict(orient='records')
        start_time = int(time.time() * 1000)
        self.file_path = rf"result_{start_time}.xlsx"

    def run(self,max_workers):
        questions = self.questions
        for m in range(0, len(questions), 20):
            batch = questions[m:m + 20]
            # 创建线程池
            print("创建线程池")
            thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            check_llm = AssortTestcase(self.file_path)
            futures = [
                thread_pool.submit(check_llm.assort, question=batch[i])
                for i in
                range(len(batch))]
            try:
                results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=None)]


            except concurrent.futures.TimeoutError:
                print("Timeout error occurred, stopping program...")
            except Exception as e:
                print(f"An exception occurred: {e}")
            finally:
                # 关闭线程池
                thread_pool.shutdown(wait=True)
                print("关闭线程池")
                check_llm.create_excel()

        # 开始排序
        sheet_to_sort = "Sheet1"
        sort_column = "Id"

        # 读取 Excel 文件，拿到所有 sheet 名称
        xls = pd.ExcelFile(self.file_path)
        all_sheets = xls.sheet_names

        # 读取所有 sheet 到字典
        sheet_dfs = {sheet: xls.parse(sheet) for sheet in all_sheets}

        # 对指定 sheet 排序
        if sheet_to_sort in sheet_dfs:
            # 确保排序列是数字类型（可选）
            sheet_dfs[sheet_to_sort][sort_column] = pd.to_numeric(sheet_dfs[sheet_to_sort][sort_column], errors='coerce')
            sheet_dfs[sheet_to_sort] = sheet_dfs[sheet_to_sort].sort_values(by=sort_column).reset_index(drop=True)
        else:
            print(f"警告: 找不到指定的 sheet {sheet_to_sort}")

        # 用 ExcelWriter 写回所有 sheet（覆盖保存）
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='w') as writer:
            for sheet_name, df in sheet_dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"{sheet_to_sort} 已按 {sort_column} 排序并保存到: {self.file_path}")


if __name__ == '__main__':
    a = Thread()
    a.run(5)