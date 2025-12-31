# coding: utf-8
import _thread as thread
import base64
import hashlib
import hmac
import json
import os
import ssl
import time
import uuid

import requests
import websocket
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
import pandas as pd
import concurrent.futures

# 数据初始化
# 接口首次响应时间列表
first_response_time_list = []

# 接口分片间隔时间列表
fragment_time_list = []

# 每个接口耗时列表
Interface_execution_time_list = []

# 接口出错统计
interface_error_num = 0

# 请求次数
request_num = 0

# 表头列表
columns_list = []

# 获取到qa对的新list
data_result_list = []


class FlamesChatClientV2(object):

    # 初始化
    def __init__(self, APP_ID, APP_SECRET, BASE_URL, BODY_ID, data):
        self.app_id = APP_ID
        self.app_secret = APP_SECRET
        self.body_id = BODY_ID
        self.host = urlparse(BASE_URL).hostname
        self.base_url = BASE_URL
        # chat会话接口地址
        self.chat_endpoint = "/openapi/flames/api/v2/chat"
        # 文件上传接口地址
        self.upload_endpoint = "/openapi/flames/file/v2/upload"
        self.data = data
        self.matchs = ''
        self.recall_list = []  # 召回片段

    # 生成url,拼接API网关核心鉴权签名信息
    def create_url(self, method, path, wsProtocol):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(self.host, date, method, path)

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.app_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'hmac api_key="{self.app_id}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host,
            "bodyId": self.body_id
        }
        base_url = self.base_url.replace("https", "wss").replace("http", "ws") if wsProtocol else self.base_url
        # 拼接鉴权参数，生成url
        url = base_url + path + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url

    def upload(self, file_path):
        request_url = self.create_url("POST", self.upload_endpoint, False)
        print("### upload ### request_url:", request_url)
        _, file_name = os.path.split(file_path)
        file = open(file_path, 'rb')
        file_base64_str = base64.b64encode(file.read()).decode('utf-8')
        body = {
            "payload": {
                "fileName": file_name,
                "file": file_base64_str
            }
        }
        response = requests.post(request_url, json=body, headers={'content-type': "application/json"},
                                 verify=False)
        print('response:', response.text)
        data = json.loads(response.text)
        code = data["header"]["code"]
        if code != 0:
            print(f'请求错误: {code}, {data}')
            return
        else:
            file_id = data["payload"]["id"]
        return file_id

    # 建立连接, 生成内容
    def generate(self):
        matchs = ''  # 重置 matchs

        params = {
            "header": {
                "traceId": TRACE_ID,
                "bodyId": self.body_id,
                "appId": self.app_id,
                "mode": 0
            },
            "payload": {
                "sessionId": "",
                "text": [
                    {
                        "content": self.data[question],
                        "content_type": "text",
                        "role": "user"
                    }
                ]
            }
        }

        request_url = self.create_url("GET", self.chat_endpoint, True)
        print("### generate ### request_url:", request_url)
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            request_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        ws.app_id = self.app_id
        ws.body_id = self.body_id
        ws.params = params
        ws.run_forever(
            sslopt={
                "cert_reqs": ssl.CERT_NONE
            }
        )

    # 收到websocket错误的处理
    def on_error(self, ws, error):
        print("### on_error:", error)

    # 收到websocket关闭的处理
    def on_close(self, ws, close_status_code, close_msg):
        print("### on_close ### code:", close_status_code, " msg:", close_msg)

    # 收到websocket连接建立的处理
    def on_open(self, ws):
        print("### on_open ###")
        request_params = json.dumps(ws.params)
        print("### request:", ws.params)
        ws.send(request_params)

    # 收到websocket消息的处理
    def on_message(self, ws, message):
        # print("### on_message:", message)
        data = json.loads(message)
        code = data['header']['code']

        if code == 0:
            choices = data["payload"]["choices"]
            status = choices["status"]
            # status = data['header']['status']
            # 大模型回复片段拼接
            try:
                self.matchs += choices["text"][0]["content"]
            except:
                pass
            # 消息实时拼接打印
            # print(fragment, end='')

            # 获取召回片段，检查 choices['text'][0] 是否存在并在 reference 中提取 sources
            if ('text' in choices and len(choices['text']) > 0 and 'content_type' in choices['text'][0] and
                    choices['text'][0]['content_type'] == 'reference'):
                sources = choices['text'][0]['reference']['sources']
                # 遍历 sources 列表，提取 parts 中的 content 值并添加到 recall_list 中
                for source in sources:
                    if 'parts' in source and isinstance(source['parts'], list):
                        for part in source['parts']:
                            if 'content' in part:
                                self.recall_list.append(part['content'])
                print(f'### 召回片段个数: {len(self.recall_list)}', )

            # 接口响应结束后内容操作
            if status == 2:
                format_matchs = self.matchs.replace('<ret>', '\n').replace('<end>', '').replace('<', '')
                # self.data.append([format_matchs] + self.recall_list)
                # self.data.extend(self.recall_list)
                data_result_list.append(self.data + [format_matchs] + self.recall_list)
                print('模型回复: ', format_matchs)
                print("#### 关闭会话\n")
                ws.close()
        else:
            # print(f'请求错误: {code}, {data}')
            global interface_error_num
            # 异常接口处理
            # if code == 20018 & code == 20019:
            #     error_message = data["payload"]["choices"]["text"][0]["progress"]["skill"]["skillOutput"]
            # else:
            error_message = f'请求错误: {code}, {data}'
            format_matchs = error_message
            self.data.append(format_matchs)
            data_result_list.append(self.data)
            print(format_matchs)
            interface_error_num += 1
            ws.close()


class TestFile(object):

    def __init__(self, num, path, limit):
        self.num = num
        self.path = path
        self.limit = limit

    def readfile(self):
        global columns_list
        # 读取Excel文件
        df = pd.read_excel(self.path, sheet_name=sheet_name)
        # print('行数:',df.shape[0])
        # 计数器初始化
        counter = 0
        columns_list = df.columns.tolist()
        content_list = df.values.tolist()
        if limit == 0:
            self.limit = df.shape[0]
        else:
            pass
        # client = FlamesChatClient(APP_ID, APP_SECRET, BASE_URL, ASSISTANT_CODE)
        with concurrent.futures.ThreadPoolExecutor(self.num) as executor:
            futures = []

            while counter < self.limit:
                for row in content_list:
                    if counter >= self.limit:
                        break
                    # print(row)
                    client = FlamesChatClientV2(APP_ID, APP_SECRET, BASE_URL, BODY_ID, row)
                    future = executor.submit(client.generate)
                    futures.append(future)

                    # 计数器
                    counter += 1
        time.sleep(2)

    def writefile(self, header, content, resName):
        """
        参数：
        header (list): 表头
        content (list): 内容
        resName (str): 结果文件名
        """
        # if len(header) != len(content[0]):
        #     raise ValueError("header和content的长度不匹配")

        try:
            # 确保每行数据长度与 header 一致
            padded_content = [row + ['无召回片段'] * (len(header) - len(row)) for row in content]
            # 将结果集序号列进行升序排序
            padded_content.sort(key=lambda x: x[0])
            df = pd.DataFrame(padded_content, columns=header)
            df.to_excel(resName, index=False)
            # df.to_csv(resName, index=False)
            print(f"数据已成功写入{resName}")
        except Exception as e:
            print(f"写入文件失败： {e}")


# 入口函数
if __name__ == "__main__":

    TRACE_ID = str(uuid.uuid1()).replace("-", "")
    # 开发平台访问地址
    BASE_URL = "ws://10.18.43.131:30009/"
    # 应用管理 -> 应用详情 -> AppID(复制)
    APP_ID = "853CCE5C316D4991B918"
    # 应用管理 -> 应用详情 -> App Secret Key(复制)
    APP_SECRET = "B8D3E5B14A014D768679D20856C9EFB2"
    # 应用管理 -> 应用详情 -> 关联数据列表 -> 编码(复制)
    BODY_ID = "xzrbgent2d1lb5xkrrhch7ehpkuneluk"


    question = 0  #读取的列，从0开始计算
    sheet_name = "Sheet1"  #读取的工作表名称
    limit = 0  #跑批数量
    num = 1  #并发数
    start_time = int(time.time() * 1000)
    # path = './testfile/装备设计助手 new.xlsx'
    path = 'input/装备设计助手（4x250）/宝石机械_设计助手_167.xlsx'
    response_document_path = fr'output/装备设计助手/宝石机械/chat_{num}路_{start_time}.xlsx'

    # ##指定循环次数调试
    # 循环计数器
    i = 0
    # 循环次数
    j = 1
    while i < j:
        file = TestFile(num, path, limit)
        file.readfile()
        i += 1

        # 数据处理，导入新文件中
        # 增加列名
        addcolumns = ['模型回复', '召回片段1', '召回片段2', '召回片段3', '召回片段4', '召回片段5', '召回片段6',
                      '召回片段7', '召回片段8', '召回片段9', '召回片段10']
        # addcolumns = ['模型回复','召回片段', '响应时间']
        columns_list.extend(addcolumns)
        # print(columns_list, data_result_list)
        # 将获取到的内容插入新的excel
        file.writefile(columns_list, data_result_list, response_document_path)
    # 生成内容
    # client.generate(content="给我写一篇500字的童话故事,主题随机")
