import pandas as pd
import requests
import urllib3
import json
from tqdm import tqdm

class Test():
    def __init__(self, localhost):
        self.localhost = localhost
        self.session = requests.Session()
        self.login()
    
    def login(self):
        user = ["chenjian", "cj1008611"]
        url = f"{self.localhost}/api/user/backdoorLogin"
        headers = {"content-type": "application/json","system-code":"0"}
        body = {"loginName": user[0], "loginPassword": user[1]}
        response = self.session.post(url=url, json=body, headers=headers, verify=False)
        data = response.json()
        orgId = data['data']['orgId']
        return orgId


    def get_recall(self, question):
        result = ""
        paragraphs = []
        urls = []

        url = f"{self.localhost}/api/gas/chat/conversation/chat"
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream","Cache-Control": "no-cache",
                    "system-code":"0","current-org-id":f"{self.login()}"}
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
        return question, result, paragraphs, urls