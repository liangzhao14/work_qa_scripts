import time
import requests
import json
import datetime
import concurrent.futures
import threading
from requests.exceptions import HTTPError
import os
import pandas as pd

class AskLLM():
    def __init__(self,localhost,file_path):
        self.localhost = localhost
        self.session = requests.Session()
        self.login("liuli","LL#liuli0661")
        start_time = int(time.time() * 1000)
        self.outputData = []
        self.file_path = file_path
        self.columns = ['thread_id', 'start_time', 'question', 'LLManswer', 'first_response_time', 'second_output', 'total_time',
                        'paragraph1', 'paragraph2', 'paragraph3', 'paragraph4', 'paragraph5', 'paragraph6', 'paragraph7',
                        'paragraph8', 'paragraph9', 'paragraph10']

    def login(self,loginName,loginPassword):
        url = f"{self.localhost}/api/user/backdoorLogin"
        headers = {"content-type": "application/json","system-code":"0","Stress-Test":"true"}
        body = {"loginName": loginName, "loginPassword": loginPassword}
        response = self.session.post(url=url, json=body, headers=headers, verify=False)
        # print(response.text)
        data = response.json()
        self.orgId = data['data']['orgId']
        print(self.orgId)

    def ask_llm(self, question, assistantId, conversationId):
        thread_id = threading.get_ident()
        url = f"{self.localhost}/api/chat/conversation/chat"
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream","Cache-Control": "no-cache",
                   "system-code":"0","current-org-id":f"{self.orgId}","Stress-Test":"true"}
        body = {"content": question, "assistantId": assistantId, "conversationId": conversationId,"type":1}
        paragraph = [""] * 10
        result = ""
        start_time = datetime.datetime.now()

        try:
            first_response_time = None
            end_time = start_time
            response = self.session.post(url=url, json=body, headers=headers, stream=True, verify=False, timeout=600)
            response.raise_for_status()  # 抛出异常如果响应状态码不是200
            response.encoding = 'utf-8'
            # r = response.text

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    data_string = line.split("data:", 1)[1]
                    data_dict = json.loads(data_string)
                    # print(data_dict)
                    if data_dict["type"] == 6 and data_dict["status"] == 0:
                        if data_dict["target"] == "add":
                            end_time = datetime.datetime.now()
                            print("**********************")
                            print(end_time - start_time)
                            print("**********************")
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
                        n = 0
                        for i in range(len(paragraph_list)):
                            item = paragraph_list[i]
                            for j in range(len(item['paragraph'])):
                                paragraph[n] = f"docName:{item['title']}\n" \
                                               f"title:{item['paragraph'][j]['title']}\n" \
                                               f"content:{item['paragraph'][j]['content']}"
                                n += 1
                        print(paragraph)

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
            print(f'Thread {thread_id}: Total time: {total_time}s\n'
                  f'start_time:{start_time.strftime("%H:%M:%S")}\n'
                  f'LLManswer:{result}\n'
                  # f'response:{r}\n'
                  f'first_response_time:{first_response}\n'
                  f'second_output:{second_output}\n')
            item = [thread_id, start_time, question, result, first_response, second_output, total_time, paragraph[0],
                    paragraph[1], paragraph[2], paragraph[3], paragraph[4], paragraph[5], paragraph[6], paragraph[7],
                    paragraph[8], paragraph[9]]
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
    file_path = fr'D:/ZSY/test1121-2.xlsx'
    a = AskLLM(localhost="https://dev-assistant.ai.cnpc", file_path=file_path)
    a.ask_llm(question="企业负责人公务用车报废标准是什么？", assistantId=1, conversationId="")
    # a.create_excel()