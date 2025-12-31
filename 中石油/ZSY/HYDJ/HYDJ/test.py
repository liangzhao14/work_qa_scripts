import time
from time import sleep
import requests
import json
import datetime
import concurrent.futures
import threading
from requests.exceptions import HTTPError
import os
import pandas as pd
import pymysql
import urllib3

# 关闭所有 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AskLLM():
    def __init__(self, localhost, file_path):
        self.localhost = localhost
        self.session = requests.Session()
        self.session.verify = False  # 忽略证书验证
        self.session.headers.update({"Stress-Test": "true"})  # 添加全局请求头
        self.login_with_cookie()  # 使用 cookie 登录
        self.file_path = file_path
        self.columns = ['thread_id', 'start_time', 'question', 'result']
        self.outputData = []  # 初始化 outputData 属性

        # 其他方法...

    def login_with_cookie(self):
        # 从文件加载 cookie
        try:
            with open('cookie.txt', 'r') as f:
                cookie = f.read().strip()
            self.session.cookies.set('session_cookie', cookie)  # 设置 cookie
        except FileNotFoundError:
            print("Cookie 文件未找到，请确保文件存在并放置在正确路径。")

    def select_sql(self, request_id, assistantId):
        db_config = {
            'host': '11.54.88.199',  # 数据库服务器的IP地址
            'port': 23306,  # 数据库端口号
            'user': 'kllm_expert_knowledge',  # 数据库用户名
            'password': 'Cnpc%2024!@#',  # 数据库密码
            'database': 'kllm_expert_knowledge',  # 要连接的数据库名称
            'charset': 'utf8mb4',  # 字符集
        }

        # 连接到数据库
        connection = pymysql.connect(**db_config)

        try:
            with connection.cursor() as cursor:
                # 编写你的查询语句
                sql = f"SELECT content FROM artisan_chat_history WHERE " \
                      f"request_id = '{request_id}' AND role = 'rewrite' LIMIT 1"
                # 执行查询
                print(sql)
                cursor.execute(sql)
                # 获取查询结果
                result = cursor.fetchall()
                result = result[0][0] if result else ""
                print(result)
        finally:
            # 关闭数据库连接
            connection.close()
        return result

    def ask_llm(self, question, conversationId, type):
        thread_id = threading.get_ident()
        url = f"{self.localhost}/api/chat/conversation/streamChat"
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }
        body = {
            "content": question,
            "assistantId": None,
            "conversationId": conversationId,
            "type": type
        }
        result = ""
        start_time = datetime.datetime.now()

        try:
            first_response_time = None
            end_time = start_time
            response = self.session.post(url=url, json=body, headers=headers, stream=True, verify=False, timeout=600)
            response.raise_for_status()  # 抛出异常如果响应状态码不是200
            response.encoding = 'utf-8'
            result_temp_10 = []
            result_temp_11 = []
            result_temp = []

            for line in response.iter_lines(decode_unicode=True):
                if line and "data" in line:
                    data_string = line.split("data:", 1)[1]
                    data_dict = json.loads(data_string)

                    if data_dict["type"] == 1 and data_dict["status"] == 0:
                        if data_dict["target"] == "add":
                            end_time = datetime.datetime.now()
                            request_id = data_dict["requestId"]
                            conversationId = data_dict["conversationId"]
                        elif data_dict["target"] == "add":
                            if first_response_time is None:
                                first_response_time = datetime.datetime.now()
                            result += data_dict["messages"][0]["text"]
                    elif data_dict["type"] == 6 and data_dict["status"] == 0:
                        assistantId = data_dict['answer'].get("assistantId")
                    elif data_dict["type"] == 10 and data_dict["status"] == 1:
                        temp1 = data_dict["messages"][0]["text"]
                        result_temp_10.append(temp1)
                    elif data_dict["type"] == 11 and data_dict["status"] == 1:
                        # temp = data_dict["messages"][0]["text"]
                        # result_temp_11.append(temp)
                        pass
                    elif data_dict["type"] == 1 and data_dict["status"] == 1:
                        if data_dict["target"] == "update" or data_dict["target"] == "add":
                            result_temp.append(data_dict["messages"][0]["text"])

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

            if first_response_time is not None:
                first_response = "{:.3f}".format((first_response_time - start_time).total_seconds())
                output_time = (end_time - first_response_time).total_seconds()
                second_output = len(result) / output_time if output_time > 0 else len(result)

            result = ''.join(result_temp)
            print(f'Thread {thread_id}: Total time: {total_time}s')
            print(f'start_time: {start_time.strftime("%H:%M:%S")}')
            print(f'LLManswer: {result}')
            print(f'first_response_time: {first_response}')
            print(f'second_output: {second_output}')

            # 构建输出数据
            item = [thread_id, start_time.strftime("%H:%M:%S"), question, result]
            self.outputData.append(item)

    def create_excel(self):
        print("开始输出excel...")
        if os.path.exists(self.file_path):
            writer = pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay')
            existing_data = pd.read_excel(self.file_path, sheet_name='Sheet1')
            combined_data = pd.concat([existing_data, pd.DataFrame(self.outputData, columns=self.columns)],
                                      ignore_index=True)
        else:
            writer = pd.ExcelWriter(self.file_path, engine='openpyxl')
            df = pd.DataFrame(data=self.outputData, columns=self.columns)
            df.to_excel(writer, sheet_name='Sheet1', index=False, header=True)

        writer.close()
        print("Excel已输出.")


if __name__ == '__main__':
    a = AskLLM(localhost="https://expert.kunlungpt.cn/", file_path='D:/test1114.xlsx')
    a.ask_llm(question="你认识繁体字吗？把下面这几个繁体字的词换成简体字，“書籍、蘋果、夢想、勇氣”。", conversationId="",
              type=3)
    a.create_excel()