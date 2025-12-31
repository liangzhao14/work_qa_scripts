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
    def __init__(self, localhost, file_path, cookie):
        self.localhost = localhost
        self.session = requests.Session()
        # self.login("18888888869","123456")
        self.session.cookies.update(cookie)
        start_time = int(time.time() * 1000)
        self.outputData = []
        self.file_path = file_path
        # self.columns = ['thread_id', 'start_time', 'question', 'L1_prompt', 'L1_LLManswer', 'L2_prompt', 'L2_LLManswer'
        #     , 'L3_prompt', 'L3_LLManswer', 'L4_prompt','L4_LLManswer', 'result','L5_LLManswer']
        self.columns = ['thread_id', 'start_time', 'question', 'result' ]

    def login(self,mobile,code):
        url = f"{self.localhost}/api/user/login4WebByLoginMobile"
        headers = {"content-type": "application/json","Stress-Test":"true"}
        body = {"mobile": mobile, "code": code, "scene": "login"}
        response = self.session.post(url=url, json=body, headers=headers, verify=False)
        # print(response.text)





    def ask_llm(self, question,conversationId, type):
        thread_id = threading.get_ident()
        url = f"{self.localhost}/api/chat/conversation/streamChat"
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream","Cache-Control": "no-cache","Stress-Test":"true"}
        body = {"content": question, "assistantId": None, "conversationId": conversationId, "type": type}
        result = ""
        assistant = "基模回答"
        assistantId = ""
        start_time = datetime.datetime.now()

        try:
            first_response_time = None
            end_time = start_time
            response = self.session.post(url=url, json=body, headers=headers, stream=True, verify=False, timeout=600)
            response.raise_for_status()  # 抛出异常如果响应状态码不是200
            response.encoding = 'utf-8'
            # r = response.text
            result_temp_10 = []
            result_temp_11 = []
            result_temp=[]

            # print(my_list)
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # print(line)
                    if "data" in line :
                        data_string = line.split("data:", 1)[1]
                        data_dict = json.loads(data_string)
                        # print(data_dict)
                        if data_dict["type"] == 1 and data_dict["status"] == 0:
                            if data_dict["target"] == "add":
                                end_time = datetime.datetime.now()
                                print(end_time - start_time)
                                request_id = data_dict["requestId"]
                                conversationId = data_dict["conversationId"]
                                # break
                            elif data_dict["target"] == "add":
                                if first_response_time is None:
                                    first_response_time = datetime.datetime.now()
                                result += data_dict["messages"][0]["text"]
                            else:
                                result += data_dict["messages"][0]["text"]
                                # response.close()
                        elif data_dict["type"] == 6 and data_dict["status"] == 0:
                            assistantId = data_dict['answer'].get("assistantId")
                            if assistantId == 1:
                                assistant = "炼化知识专家"
                            elif assistantId == 2:
                                assistant = "油气知识专家"
                            elif assistantId == 4:
                                assistant = "油藏知识专家"
                            elif assistantId == 5:
                                assistant = "新能源知识专家"
                            else:
                                assistant = "联网检索"
                                assistantId = ""
                        elif data_dict["type"] == 10 and data_dict["status"] == 1:
                            # print("----------")
                            temp1 = data_dict["messages"][0]["text"]
                            result_temp_10.append(temp1)
                            # print(temp1)

                            # print(temp.split(',')[1])

                            # print("----------")
                        elif data_dict["type"] == 11 and data_dict["status"] == 1:
                            print("******")
                            # temp = data_dict["messages"][0]["text"]
                            # result_temp_11.append(temp)
                            # print(temp)

                        elif data_dict["type"] == 1 and data_dict["status"] == 1:
                            if data_dict["target"] == "update" or data_dict["target"] == "add":
                                #     print(data_dict)
                                result_temp.append(data_dict["messages"][0]["text"])
                                # print(data_dict["messages"][0]["text"])

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
            # rewrite = self.select_sql(request_id=request_id, assistantId=assistantId)
            result = ''
            for word in result_temp:
                result += word
            rewrite=''
            # print('*********')
            # print(result_temp_11[0])
            # print('*********')
            N_10=len(result_temp_10)
            result_10=[0] * 6
            N_11= len(result_temp_11)
            result_11 = [0] * 6
            for i in range(5):
                    result_10[i] =rewrite
                    result_11[i] =rewrite
            result_10[:N_10] = result_temp_10[:N_10]
            result_11[:N_11] = result_temp_10[:N_11]

                # print(result_10[i])

            # for j in range(5):
            #     if j == 0:
            #         j = rewrite
            #     print(j)


            # item = [thread_id, start_time.strftime("%H:%M:%S"), question, result_temp_10[0], result_temp_11[0],result_temp_10[1], result_temp_11[1], result_temp_10[2], result_temp_11[2],result_temp_10[3], result_temp_11[3],result_temp_10[4], result_temp_11[4]]
            # item = [thread_id, start_time.strftime("%H:%M:%S"), question, result_10[0], result_11[0],result_10[1],result_11[1], result_10[2], result_11[2], result_10[3], result_11[3], result, rewrite]
            item = [thread_id, start_time.strftime("%H:%M:%S"), question, result]
                    # result_11[1], result_10[2], result_11[2], result_10[3], result_11[3], result, rewrite]
            # print(item)
            self.outputData.append(item)
            # return conversationId

    # def ask_llm_twice(self,first_question,second_question):
    #     conversationId = self.ask_llm(question=first_question, conversationId="", type=3)
    #     self.ask_llm(question=second_question,conversationId=conversationId, type=3)



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
    cookie = {
        "i_c_u_a_t": "dc9ab4860d5e46eca7a4bf75ec04f006"
    }
    a = AskLLM(localhost="https://expert.kunlungpt.cn/", file_path='D:/test1114.xlsx',cookie=cookie)
    # df = pandas.read_excel(r'D:\work\ZSY\1128\basic\HYDJ\questions.xlsx')
    # questions = df.iloc[:, 0].tolist()
    # print(questions)
    a.ask_llm(question="你认识繁体字吗？把下面这几个繁体字的词换成简体字，“書籍、蘋果、夢想、勇氣”。", conversationId="", type=3)
    # a.select_sql(request_id='a22b79c6-9f77-41a2-871f-53df3c081bb8',assistantId='')
    # a.ask_llm_twice(first_question="JAVA工程师的工作职责",second_question="它是软件开发工程师吗？")
    a.create_excel()