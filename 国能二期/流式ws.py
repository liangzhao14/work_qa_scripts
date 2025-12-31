# coding: utf-8
# Install this package at first: python -m pip install websocket-client
import _thread as thread
import base64
import hashlib
import hmac
import json
import random
import ssl
import string
import websocket
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
import time

# 1231
class FlamesChatClient(object):
    # 初始化
    def __init__(self, app_id, app_secret, base_url):
        self.app_id = app_id
        self.app_secret = app_secret
        # self.chat_endpoint = chat_endpoint
        self.host = urlparse(base_url).hostname
        self.path = urlparse(base_url).path
        self.base_url = base_url

    # 生成url,拼接大模型接口鉴权签名信息
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(
            self.app_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding="utf-8")

        authorization_origin = f'hmac api_key="{self.app_id}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
            encoding="utf-8"
        )

        # 将请求的鉴权参数组合为字典
        v = {"authorization": authorization, "date": date, "host": self.host}
        # 拼接鉴权参数，生成url
        url = self.base_url + "?" + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print(url)
        return url

    # 建立连接, 生成内容
    def generate(self, content):
        request_url = self.create_url()
        print("### generate ### request_url:", request_url)
        print("### generate ### content:", content)
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            request_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        ws.app_id = self.app_id
        ws.trace_id = (
            "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        )
        ws.content = content
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# 收到websocket错误的处理
def on_error(ws, error):
    print("### on_error:", error)


# 收到websocket关闭的处理
def on_close(ws, close_status_code, close_msg):
    print("### on_close ### code:", close_status_code, " msg:", close_msg)


# 收到websocket连接建立的处理
def on_open(ws):
    print("### on_open ###")
    thread.start_new_thread(run, (ws,))


# 发送数据
def run(ws, *args):
    data = json.dumps(
        gen_params(
            trace_id=ws.trace_id,
            app_id=ws.app_id,
            content=ws.content,
        )
    )
    print("### run ### data:", data)
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    print("### on_message:", message)
    data = json.loads(message)
    code = data[0]["header"]["code"]
    if code != 0:
        print(f"请求错误: {code}, {data}")
        ws.close()
    else:
        choices = data[0]["payload"]["choices"]
        status = choices["status"]
        if status == 2:
            print("### 关闭会话")
            ws.close()


# 生成请求参数，不同助手不同
def gen_params(trace_id, app_id, content):
    """
    通过"应用管理->应用详情->关联数据列表->协议"详情获取请求参数
    """
    data = {
        "header": {"traceId": trace_id},
        "parameter": {"chat": {"top_k": "4"}},
        "payload": {
            "message": {"text": [{"content": content, "role": "user", "content_type": "text"}]}
        },
    }
    return data


# 入口函数
# if __name__ == "__main__":
#
#     for i in range(1):
#         # time.sleep(5)
#         APP_ID = "20250528AN115121DUF5"
#         # 应用管理 -> 应用详情 -> App Secret Key(复制)
#         APP_SECRET = "8AA42EF6AFCD470184D633D176A2FBA2"
#
#         BASE_URL = "ws://172.30.209.223:30014/openapi/rvppa0r2"
#
#         client = FlamesChatClient(APP_ID, APP_SECRET, BASE_URL)
#         # 生成内容
#         client.generate(content="你是谁？")
import concurrent.futures


def run_client():
    APP_ID = "20250626AN1205163yJP"
    APP_SECRET = "1E41FD4ABC3240ABBEA931327730A785"
    BASE_URL = "ws://172.31.169.228:30014/openapi/3vu3k3cv"

    client = FlamesChatClient(APP_ID, APP_SECRET, BASE_URL)
    client.generate(content="你是谁？")


if __name__ == "__main__":
    num_calls = 1 # 并发次数
    max_workers = 2  # 最大并发线程数

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_client) for _ in range(num_calls)]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("发生异常:", str(e))