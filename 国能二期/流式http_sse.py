import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime
from time import mktime
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
import urllib3


class http_client(object):
    def __init__(self, authorization, base_url):
        self.authorization = authorization
        self.host = urlparse(base_url).hostname
        self.base_url = base_url
        self.path = urlparse(base_url).path
        self.content_type = "application/json"
        self.request_method = "POST"
        self.digest = ""

    def run(self, content):
        data = json.dumps(content)
        self.digest = self.sign_body(data)
        print("请求入参：", data)
        headers = self.auth_headers()
        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning)  # 关闭警告

        try:
            response = requests.request(
                self.request_method,
                self.base_url,
                data=data,
                headers=headers,
                stream=True,
                verify=False
            )
        except Exception as e:
            print("请求异常：", e)
            return None

        if response.status_code != 200:
            print("响应错误：", response.status_code, response.text)
            return None

        print("SSE流响应开始：")
        # for line in response.iter_lines(decode_unicode=True):
        #     if line:
        #         print(line)  # 原始输出，不做解析
        for line in response.iter_lines():
            if line:
                try:
                    print(line.decode("utf-8"))
                except UnicodeDecodeError:
                    print(line)

    def sign_body(self, body):
        sha256 = hashlib.sha256()
        sha256.update(body.encode("utf-8"))
        digest = sha256.digest()
        return base64.b64encode(digest).decode("utf-8")

    def auth_headers(self):

        return {
            "Authorization": "Bearer " + self.authorization,
            # "Authorization": authorization,
            # "Date": date,
            # "Host": self.host,
            # "Digest": f"SHA-256={self.digest}",
            "Content-Type": self.content_type,
            "Accept": "text/event-stream"
        }


def request_params():
    return {
        "model": "qwen2.5-72b",
        "stream": True,
        "messages": [
            {
                "role": "user",
                "content": "你好"
            }
        ]
    }


if __name__ == "__main__":
    BASE_URL = "https://cloud-skgs-ilink.chnenergy.com.cn/openapi/36io57cj"
    Authorization = "20251230AN185418Baks_E1EDF544E0B74215B61B2D9B7B476E1E"
    client = http_client(Authorization, BASE_URL)
    client.run(request_params())
    # for i in range(1):  # 想调用几次写几次
    #     params = request_params(f"你好，第{i + 1}次调用")
    #     client.run(params)