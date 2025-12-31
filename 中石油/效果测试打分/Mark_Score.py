import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
import json
import openpyxl


class ModelEvaluation:
    def __init__(self):
        # 初始化大模型API相关参数
        self.model_api_url = None  # 填写大模型的API接口地址
        self.api_key = None  # 填写API密钥，如果需要的话

        # 初始化相似度计算模型
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_excel_data(self, file_path):
        """加载Excel数据"""
        try:
            df = pd.read_excel(file_path)
            if len(df.columns) != 3:
                raise ValueError("Excel文件必须包含三列：问题、参考答案和模型回复")
            return df
        except Exception as e:
            print(f"加载Excel文件时出错: {e}")
            return None

    def calculate_similarity(self, reference_answer, model_response):
        """计算文本相似度"""
        try:
            if self.model_api_url:
                # 调用大模型API计算相似度
                payload = {
                    "text1": reference_answer,
                    "text2": model_response
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
                }
                response = requests.post(self.model_api_url, headers=headers, data=json.dumps(payload))

                if response.status_code == 200:
                    result = response.json()
                    # 假设API返回的相似度分数是一个0到1之间的值
                    similarity_score = result.get("similarity_score", 0.0)
                    return similarity_score
                else:
                    print(f"调用大模型API失败，使用备选相似度计算方法")
                    return self.fallback_similarity_method(reference_answer, model_response)
            else:
                # 如果没有设置API地址，使用备选相似度计算方法
                return self.fallback_similarity_method(reference_answer, model_response)
        except Exception as e:
            print(f"计算相似度时出错: {e}")
            return 0.0

    def fallback_similarity_method(self, text1, text2):
        """当无法调用大模型API时使用的备选相似度计算方法"""
        # 使用Sentence-BERT计算余弦相似度
        embeddings1 = self.similarity_model.encode([text1])
        embeddings2 = self.similarity_model.encode([text2])
        similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
        return similarity

    def grade_response(self, similarity_score):
        """根据相似度分数给出评分"""
        if similarity_score < 0.1:
            return 1  # 只要回答出来就行
        elif similarity_score < 0.3:
            return 2  # 稍微相关
        elif similarity_score < 0.6:
            return 3  # 近似相关
        elif similarity_score < 0.8:
            return 4  # 80%相关
        else:
            return 5  # 满分

    def evaluate_data(self, df):
        """评估数据集"""
        evaluated_data = []
        for _, row in df.iterrows():
            question = row[0]
            reference = row[1]
            model_response = row[2]

            similarity = self.calculate_similarity(reference, model_response)
            score = self.grade_response(similarity)

            evaluated_data.append({
                "问题": question,
                "参考答案": reference,
                "模型回复": model_response,
                "相似度": round(similarity, 4),
                "评分": score
            })

        return pd.DataFrame(evaluated_data)

    def save_results(self, evaluated_df, output_path):
        """保存评估结果到Excel文件"""
        try:
            evaluated_df.to_excel(output_path, index=False)
            print(f"评估结果已保存到 {output_path}")
        except Exception as e:
            print(f"保存评估结果时出错: {e}")

    def run_evaluation(self, input_file, output_file):
        # 调用大模型API的示例函数
        # 实际使用时需要替换为具体API的调用方式
        def call_model_api(text):
            if not self.model_api_url:
                print("请设置大模型API接口地址")
                return None

            payload = {"text": text}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.model_api_url, headers=headers, json=payload)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"调用大模型API失败，状态码: {response.status_code}")
                return None

        # 加载数据
        df = self.load_excel_data(input_file)
        if df is None:
            return

        # 打分
        evaluated_df = self.evaluate_data(df)

        # 保存结果
        self.save_results(evaluated_df, output_file)


# 示例用法
if __name__ == "__main__":
    evaluator = ModelEvaluation()
    evaluator.model_api_url = "http://your-model-api-url.com/v1/models/text-similarity:predict"  # 填写大模型API接口地址
    evaluator.api_key = "your_api_key"  # 如果需要 API 密钥，填写在此

    input_excel = "input_data.xlsx"  # 输入Excel文件路径
    output_excel = "evaluated_data.xlsx"  # 输出Excel文件路径

    evaluator.run_evaluation(input_excel, output_excel)