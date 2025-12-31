import time
import requests
import json
import datetime
import concurrent.futures
import threading
from requests.exceptions import HTTPError
import os
import pandas as pd
import pymysql

class AskLLM():
    def __init__(self,localhost,file_path):
        self.localhost = localhost
        self.session = requests.Session()
        self.login("chenjian","cj1008611")
        start_time = int(time.time() * 1000)
        self.outputData = []
        self.file_path = file_path
        self.columns = ['thread_id', 'start_time', 'question', 'rewrite', 'LLManswer', 'first_response_time', 'second_output', 'total_time',
                        'paragraph1', 'paragraph2', 'paragraph3', 'paragraph4', 'paragraph5']

    def login(self,loginName,loginPassword):
        url = f"{self.localhost}/api/user/backdoorLogin"
        headers = {"content-type": "application/json","system-code":"0","Stress-Test":"true"}
        body = {"loginName": loginName, "loginPassword": loginPassword}
        response = self.session.post(url=url, json=body, headers=headers, verify=False)
        # print(response.text)
        data = response.json()
        self.orgId = data['data']['orgId']
        # print(self.orgId)

    def select_sql(self,request_id):
        db_config = {
            'host': '11.54.88.199',  # 数据库服务器的IP地址
            'port': 23306,  # 数据库端口号
            'user': 'kllm_gas_chat',  # 数据库用户名
            'password': 'Cnpc%2024!@#',  # 数据库密码
            'database': 'kllm_gas_chat',  # 要连接的数据库名称
            'charset': 'utf8mb4',  # 字符集
            # 'cursorclass': pymysql.cursors.DictCursor  # 返回结果作为字典
        }

        # 连接到数据库
        connection = pymysql.connect(**db_config)

        try:
            with connection.cursor() as cursor:
                # 编写你的查询语句
                sql = f"SELECT content FROM artisan_chat_history where request_id = '{request_id}' and role = 'rewrite' limit 1"  # 替换为你的实际查询语句
                # print(sql)

                # 执行查询
                cursor.execute(sql)

                # 获取查询结果
                result = cursor.fetchall()
                result = result[0][0] if result else ""

                # 打印查询结果
                # result = (result[0][0]).replace("'",'"')
                # result = json.loads(result)
                # print(result['question'])
                # print(result[0][0])
                # print(result[0][1])
        finally:
            # 关闭数据库连接
            connection.close()

        return result

    def ask_llm(self, question, conversationId):
        thread_id = threading.get_ident()
        url = f"{self.localhost}/api/gas/chat/conversation/chat"
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream","Cache-Control": "no-cache",
                   "system-code":"0","current-org-id":f"{self.orgId}","Stress-Test":"true"}
        body = {"content": question, "conversationId": conversationId}
        paragraph = [""] * 5
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
                            request_id = data_dict["requestId"]
                            break
                        elif data_dict["target"] == "add":
                            if first_response_time is None:
                                first_response_time = datetime.datetime.now()
                            result += data_dict["messages"][0]["text"]
                        else:
                            result += data_dict["messages"][0]["text"]
                            # response.close()
                    elif data_dict["type"] == 8 and data_dict["status"] == 1:
                        paragraph_list = data_dict["messages"][0]["adaptiveCards"][0]["body"]["source"]
                        print(paragraph_list)
                        for i in range(len(paragraph_list)):
                            item = paragraph_list[i]
                            paragraph[i] = f"title:{item['title']}\n" \
                                           f"url:{item['url']}"
                        # print(f"{paragraph} test")

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

            print(request_id)
            result = result.replace("\n", "")
            print(f'Thread {thread_id}: Total time: {total_time}s\n'
                  f'start_time:{start_time.strftime("%H:%M:%S")}\n'
                  f'LLManswer:{result}\n'
                  # f'response:{r}\n'
                  f'first_response_time:{first_response}\n'
                  f'second_output:{second_output}\n')
            rewrite = self.select_sql(request_id=request_id)
            item = [thread_id, start_time, question, rewrite, result, first_response, second_output, total_time,
                    paragraph[0], paragraph[1], paragraph[2], paragraph[3], paragraph[4]]
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
    file_path = fr'D:/ZSY/1128/output/HYDJ/'
    a = AskLLM(localhost="https://test-assistant.ai.cnpc", file_path=fr'D:/ZSY/1128/output/test1114.xlsx')
    # a.select_sql(request_id='9ffd5fba-9330-4057-b4a6-5de064b97e9d')
    a.ask_llm(question="李克强的去世是否出乎意料？", conversationId="")
    # a.create_excel()