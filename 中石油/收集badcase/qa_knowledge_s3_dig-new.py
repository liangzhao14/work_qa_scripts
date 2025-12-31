# -*- coding: utf-8 -*-
import json
import threading
import time
import pandas as pd
import os
import concurrent.futures
from datetime import datetime
import re

class DigitalArtisan:
    def __init__(self):
        self.lock = threading.Lock()
        self.outputData = []

    def safe_json_parse(self, json_str):
        """增强版JSON解析，处理LaTeX公式和特殊字符"""
        if not json_str or not isinstance(json_str, str):
            return {}

        # 预处理字符串
        json_str = json_str.strip()
        json_str = json_str.replace('\ufeff', '')  # 移除BOM
        
        # 处理代码块标记
        if json_str.startswith("```json") and json_str.endswith("```"):
            json_str = json_str[7:-3].strip()
        elif json_str.startswith("```") and json_str.endswith("```"):
            json_str = json_str[3:-3].strip()

        # 处理LaTeX特殊字符
        json_str = re.sub(r'(?<!\\)\\([^"\\])', r'\\\\\1', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # 二次尝试：转义所有反斜杠
            try:
                return json.loads(json_str.replace('\\', '\\\\'))
            except:
                print(f"JSON解析失败，位置 {e.lineno}:{e.colno}")
                return {}
        except Exception as e:
            print(f"JSON解析错误: {str(e)}")
            return {}

    def extract_scores(self, input_dict):
        """处理单条记录，兼容各种异常情况"""
        try:
            # 基础字段处理
            base_data = {
                "Id": str(input_dict.get("Id", "")),
                "start_time": input_dict.get("start_time", ""),
                "question": input_dict.get("question", ""),
                "expected_answer": input_dict.get("expected_answer", ""),
                "expected_paragraph": input_dict.get("expected_paragraph", ""),
                "llm_answer": input_dict.get("llm_answer", ""),
                "answer_source": input_dict.get("answer_source", ""),
                "references": input_dict.get("references", ""),
                "recall_result": str(input_dict.get("recall_result", "{}")),
                "result_check_answer": str(input_dict.get("result_check_answer", "{}"))
            }

            # 解析JSON数据
            result_data = self.safe_json_parse(base_data["result_check_answer"])
            if not result_data:
                print(f"ID {base_data['Id']} JSON解析失败，尝试原始提取...")
                # 应急提取逻辑
                raw_text = base_data["result_check_answer"]
                result_data = {
                    "dimension_scores": {
                        dim: {"score": 0, "reason": ""} for dim in [
                            "faithfulness", "answer_relevance",
                            "retrieval_quality", "completeness", "overall"
                        ]
                    },
                    "error_analysis": {
                        "hallucinations": [],
                        "missing_points": [],
                        "retrieval_failures": []
                    },
                    "improvement_suggestions": []
                }
                if '"score":' in raw_text:
                    for dim in result_data["dimension_scores"]:
                        pattern = rf'"{dim}":.*?"score":\s*(\d)'
                        if match := re.search(pattern, raw_text):
                            result_data["dimension_scores"][dim]["score"] = int(match.group(1))

            # 提取评分数据
            scores = {
                dim: result_data.get("dimension_scores", {}).get(dim, {})
                for dim in ["faithfulness", "answer_relevance", "retrieval_quality", "completeness", "overall"]
            }
            
            # 错误分析和建议
            error_analysis = result_data.get("error_analysis", {})
            suggestions = result_data.get("improvement_suggestions", [])

            # 构建结果行
            result_row = [
                base_data["Id"],
                base_data["start_time"],
                base_data["question"],
                base_data["expected_answer"],
                base_data["expected_paragraph"],
                base_data["llm_answer"],
                base_data["answer_source"],
                base_data["references"],
                self.safe_json_parse(base_data["recall_result"]).get("recall", ""),
                self.safe_json_parse(base_data["recall_result"]).get("result_reason", ""),
                round(  # 综合得分
                    scores["faithfulness"].get("score", 0) * 0.25 +
                    scores["answer_relevance"].get("score", 0) * 0.2 +
                    scores["retrieval_quality"].get("score", 0) * 0.15 +
                    scores["completeness"].get("score", 0) * 0.3 +
                    scores["overall"].get("score", 0) * 0.1,
                    2
                ),
                *[scores[dim].get("score", 0) for dim in scores],
                *[scores[dim].get("reason", "") for dim in scores],
                *["\n".join(error_analysis.get(key, [])) for key in ["hallucinations", "missing_points", "retrieval_failures"]],
                "\n".join(map(str, suggestions)) if suggestions else ""
            ]

            with self.lock:
                self.outputData.append(result_row)

            return True

        except Exception as e:
            print(f"处理ID {base_data.get('Id', '')} 出错: {str(e)}")
            return False

    def create_excel(self, file_path):
        """线程安全地创建/更新Excel文件（带固定列顺序和Id排序）"""
        with self.lock:
            try:
                # 定义固定列顺序
                columns = [
                    'Id', 'start_time', 'question', 'expected_answer', 'expected_paragraph', 'llm_answer',
                    'answer_source', 'references', 'recall', 'result_reason', 'answer_score',
                    'faithfulness_score', 'answer_relevance_score', 'retrieval_quality_score',
                    'completeness_score', 'overall_score', 'faithfulness_reason',
                    'answer_relevance_reason', 'retrieval_quality_reason', 'completeness_reason',
                    'overall_reason', 'hallucinations', 'missing_points', 'retrieval_failures',
                    'improvement_suggestions'
                ]

                # 转换为DataFrame并排序
                df = pd.DataFrame(self.outputData, columns=columns)
                
                # 确保Id列可以正确排序（处理字符串和数字混合情况）
                df['Id'] = pd.to_numeric(df['Id'], errors='coerce').fillna(0).astype(int)
                df = df.sort_values('Id').reset_index(drop=True)
                
                # 恢复Id列的原始格式（避免数字被转为float）
                df['Id'] = df['Id'].astype(str)

                if os.path.exists(file_path):
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                        existing_df = pd.read_excel(writer, sheet_name='Sheet1')
                        # 合并时也保持排序
                        combined_df = pd.concat([existing_df, df], ignore_index=True)
                        combined_df['Id'] = pd.to_numeric(combined_df['Id'], errors='coerce').fillna(0).astype(int)
                        combined_df = combined_df.sort_values('Id').reset_index(drop=True)
                        combined_df['Id'] = combined_df['Id'].astype(str)
                        combined_df.to_excel(writer, sheet_name='Sheet1', index=False)
                else:
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Sheet1', index=False)
                
                print(f"成功写入: {file_path}")
                return True
                
            except Exception as e:
                print(f"写入Excel失败: {str(e)}")
                return False
            finally:
                self.outputData = []

    def process_single_file(self, input_path):
        """处理单个输入文件"""
        print(f"\n开始处理文件: {input_path}")
        
        try:
            # 读取输入文件
            df = pd.read_excel(input_path)
            if df.empty:
                print("警告: 空文件，跳过处理")
                return False

            # 准备输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(
                os.path.dirname(input_path),
                f"{base_name}_tj_{timestamp}.xlsx"
            )

            # 分批处理数据
            batch_size = 20
            records = df.to_dict('records')
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                print(f"处理批次 {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}")

                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(self.extract_scores, item) for item in batch]
                    for future in concurrent.futures.as_completed(futures):
                        future.result()  # 只是为了捕获异常

                # 每批处理完后保存
                if not self.create_excel(output_path):
                    print("警告: 本批次数据保存失败")

            print(f"文件处理完成: {input_path} -> {output_path}")
            return True

        except Exception as e:
            print(f"处理文件失败: {input_path}\n错误: {str(e)}")
            return False

    def batch_process_files(self, directory):
        """批量处理目录下的所有Excel文件"""
        print(f"\n开始处理目录: {directory}")
        
        if not os.path.isdir(directory):
            print("错误: 指定的路径不是目录")
            return False

        # 获取所有.xlsx文件（排除临时文件和已处理文件）
        excel_files = [
            os.path.join(directory, f) 
            for f in os.listdir(directory) 
            if (f.endswith('.xlsx') or f.endswith('.xls')) 
            and not f.startswith('~$') 
            and '_tj_' not in f
        ]

        if not excel_files:
            print("没有找到可处理的Excel文件")
            return False

        print(f"找到 {len(excel_files)} 个待处理文件:")
        for i, f in enumerate(excel_files, 1):
            print(f"{i}. {os.path.basename(f)}")

        # 处理每个文件
        success_count = 0
        for file_path in excel_files:
            if self.process_single_file(file_path):
                success_count += 1

        print(f"\n处理完成: 成功 {success_count}/{len(excel_files)} 个文件")
        return success_count > 0

if __name__ == '__main__':
    processor = DigitalArtisan()

    
    # 使用示例
    target_dir = input("请输入要处理的目录路径（留空使用当前目录）: ").strip() or os.getcwd()
    processor.batch_process_files(target_dir)
    
    print("\n程序执行完毕")
    if os.name == 'nt':  # Windows系统保持窗口
        input("按Enter键退出...")