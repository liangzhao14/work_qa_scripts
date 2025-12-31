import pandas as pd
import requests
import urllib3
import json
from tqdm import tqdm
import concurrent.futures
import time
import os

# 关闭所有 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WWZ():
    def __init__(self,localhost,file_path):
        self.localhost = localhost
        self.session = requests.Session()
        self.login("chenjian", "cj1008611")
        start_time = int(time.time() * 1000)
        self.outputData = []
        self.file_path = file_path
        self.columns = ["问题", "客户答案", "正确url", "新闻标题", "大模型答案", "召回url", "召回1", "召回2", "召回3", "召回4", "召回5",
                        "是否召回"]

    def login(self,loginName,loginPassword):
        url = f"{self.localhost}/api/user/backdoorLogin"
        headers = {"content-type": "application/json", "system-code": "0"}
        body = {"loginName": loginName, "loginPassword": loginPassword}
        response = self.session.post(url=url, json=body, headers=headers, verify=False)
        # print(response.text)
        data = response.json()
        self.orgId = data['data']['orgId']


    def get_recall(self, question,answer,testurl,title):
        result = ""
        paragraphs = []
        urls = []

        url = f"{self.localhost}/api/gas/chat/conversation/chat"
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream","Cache-Control": "no-cache",
                    "system-code":"0","current-org-id":f"{self.orgId}"}
        body = {"content": question, "conversationId": ""}
        response = self.session.post(url=url, json=body, headers=headers, stream=True, verify=False, timeout=600)
        response.encoding = 'utf-8'
        for line in response.iter_lines(decode_unicode=True):
            if line != "":
                line = line.split("data:")[1]
                data_dict = json.loads(line)
                if data_dict["type"] == 1 and data_dict["status"] == 1 and data_dict["target"] != "end":
                    result += data_dict["messages"][0]["text"]
                elif data_dict["type"] == 8 and data_dict["status"] == 1:
                    paragraph_list = data_dict["messages"][0]["adaptiveCards"][0]["body"]["source"]
                    # print(paragraph_list)
                    for each in paragraph_list:
                        paragraph = f"docName:{each['title']}"
                        paragraphs.append(paragraph)
                        urls.append(each['url'])

        item = [question, answer, testurl, title, result,str(urls),paragraphs[0],paragraphs[1],paragraphs[2],paragraphs[3],
                paragraphs[4],str(1 if testurl in urls else 0)]
        print(item)
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
    df = pd.read_excel('D:\\WWZ\\测试集.xlsx')
    localhost = r'https://test-assistant.ai.cnpc'
    file_path = 'D:\\WWZ\\裸模测试输出.xlsx'
    col_dict = df.to_dict(orient='records')
    # print(col_dict)
    for m in range(0, len(col_dict), 20):
        batch = col_dict[m:m + 20]
        # 创建线程池
        print("创建线程池")
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=20)
        WWZ1 = WWZ(localhost=localhost,file_path=file_path)
        futures = [thread_pool.submit(WWZ1.get_recall, question=batch[i]['问题'],answer=batch[i]['问题答案'],testurl=batch[i]['url'],
                                      title=batch[i]['标题']) for i in range(len(batch))]
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
            WWZ1.create_excel()