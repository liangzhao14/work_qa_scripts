import time
import requests
import pymysql
import json
import datetime
import threading
from requests.exceptions import HTTPError
import os
import pandas as pd
from rouge_chinese import Rouge
import jieba

class CreateSummary():
    def __init__(self,localhost,file_path):
        self.localhost = localhost
        self.session = requests.Session()
        self.login("18605564701","123456")
        start_time = int(time.time() * 1000)
        self.outputData = []
        self.file_path = file_path
        self.columns = ['thread_id', 'businessId', 'title', 'content', 'summary', 'rouge_scores']

    def login(self,mobile,code):
        url = f"{self.localhost}/api/user/login4WebByLoginMobile"
        headers = {"content-type": "application/json"}
        body = {"mobile": mobile, "code": code, "scene": "login"}
        response = self.session.post(url=url, json=body, headers=headers, verify=False)
        # print(response.text)

    def select_sql(self,businessId):
        db_config = {
            'host': '11.54.88.199',  # 数据库服务器的IP地址
            'port': 23306,  # 数据库端口号
            'user': 'kllm_expert_news',  # 数据库用户名
            'password': 'Cnpc%2024!@#',  # 数据库密码
            'database': 'kllm_expert_news',  # 要连接的数据库名称
            'charset': 'utf8mb4',  # 字符集
            # 'cursorclass': pymysql.cursors.DictCursor  # 返回结果作为字典
        }

        # 连接到数据库
        connection = pymysql.connect(**db_config)

        try:
            with connection.cursor() as cursor:
                # 编写你的查询语句
                sql = f"SELECT title,content FROM kllm_hot_news where id = {businessId} limit 1"  # 替换为你的实际查询语句

                # 执行查询
                cursor.execute(sql)

                # 获取查询结果
                result = cursor.fetchall()

                # 打印查询结果
                # print(result[0][0])
                # print(result[0][1])
        finally:
            # 关闭数据库连接
            connection.close()
        return {'title': result[0][0], 'content': result[0][1]}

    def ask_llm(self, content, assistantId, businessId, conversationId, type):
        thread_id = threading.get_ident()
        url = f"{self.localhost}/api/chat/conversation/chat"
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream", "Cache-Control": "no-cache"}
        body = {"content": content, "assistantId": assistantId, "conversationId": conversationId, "type": type,"businessId": businessId}
        result = ""
        start_time = datetime.datetime.now()

        try:
            first_response_time = None
            end_time = start_time
            response = self.session.post(url=url, json=body, headers=headers, stream=True, verify=False, timeout=600)
            response.raise_for_status()  # 抛出异常如果响应状态码不是200
            response.encoding = 'utf-8'
            r = response.text

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    data_string = line.split("data:", 1)[1]
                    data_dict = json.loads(data_string)
                    if data_dict["type"] == 1 and data_dict["status"] == 1:
                        if data_dict["target"] == "end":
                            end_time = datetime.datetime.now()
                            break
                        elif data_dict["target"] == "add":
                            if first_response_time is None:
                                first_response_time = datetime.datetime.now()
                            result += data_dict["messages"][0]["text"]
                        else:
                            result += data_dict["messages"][0]["text"]
                            # response.close()

        except HTTPError as http_err:
            if http_err.response.status_code == 504:
                result = "504 Gateway Timeout: The server did not respond in time."
            else:
                result = f"HTTP Error {http_err.response.status_code}: {http_err.response.reason_phrase}"

        finally:
            total_time = "{:.3f}".format((end_time - start_time).total_seconds())
            first_response = "N/A"
            second_output = "N/A"
            response.close()

            if "end_time" in locals() and first_response_time is not None:
                first_response = "{:.3f}".format((first_response_time - start_time).total_seconds())
                output_time = "{:.3f}".format((end_time - first_response_time).total_seconds())
                if float(output_time) > 0:
                    second_output = "{:.3f}".format(len(result) / float(output_time))
                else:
                    second_output = len(result)

            result = result.replace("\n", "")
            # print(f'Thread {thread_id}: Total time: {total_time}s\n'
            #       f'start_time:{start_time.strftime("%H:%M:%S")}\n'
            #       f'LLManswer:{result}\n'
            #       # f'response:{r}\n'
            #       f'first_response_time:{first_response}\n'
            #       f'second_output:{second_output}\n')
            return result

    def check_rouge(self,businessId,title):
        thread_id = threading.get_ident()
        news = self.select_sql(businessId=businessId)
        title = f"新闻分析：【{news['title']}】"
        content = news['content']
        summary = self.ask_llm(content=title, assistantId=None, businessId=businessId, conversationId="", type=5)
        hypothesis = ' '.join(jieba.cut(summary))
        reference = ' '.join(jieba.cut(content))
        rouge = Rouge()
        scores = rouge.get_scores(hypothesis, reference)
        rouge_scores = "{:.2f}".format(scores[0]['rouge-2']['f'] * 100)
        print(summary)
        item = [thread_id, businessId, title, content, summary, rouge_scores]
        self.outputData.append(item)


    def create_excel(self):
        print("开始输出excel...")
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
        else:
            # 如果文件不存在,则创建一个新的
            writer = pd.ExcelWriter(self.file_path, engine='openpyxl')
            # 创建DataFrame并写入Excel
            df = pd.DataFrame(data=self.outputData, columns=self.columns)
            df.to_excel(writer, sheet_name='Sheet1', index=False, header=True)
        writer.close()
        print("Excel已输出.")


if __name__ == '__main__':
    a = CreateSummary(localhost="https://test-expert.ai.cnpc", file_path=fr'D:/ZSY/1128/output/HYDJ/')
    a.check_rouge(621,"")
    # a.create_excel()

