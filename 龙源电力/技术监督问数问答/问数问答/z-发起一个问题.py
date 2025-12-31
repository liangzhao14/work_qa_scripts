import base64
import hashlib
import hmac
from datetime import datetime, timezone
import requests
import json

# 当前 GMT 时间
gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

# 配置信息
key_id = "longyuan-common-chat"                # key id
secret_key = b"5b0d907e24926125f5646302e43d0c2f"    # secret key
request_method = "POST"             # HTTP 方法
request_path = "/digital-artisan-chat2/botChat/api/stream"              # 路径
algorithm = "hmac-sha256"           # 算法

# 请求体
body = """{
      "assistantId":1103,
      "commonModelId": 37,
      "question":"请帮我生成海上龙源2025年03月的运行分析月报",
      "userId": "longyuanuser",
      "userToken": "",
      "regionRights": ["海上"]
}"""

# 构建签名字符串
signing_string = (
  f"{request_method} {request_path}\n"
  f"date: {gmt_time}\n"
  f"digest: SHA-256={base64.b64encode(hashlib.sha256(body.encode('utf-8')).digest()).decode('utf-8')}\n"
)

# 生成签名
signature = hmac.new(secret_key, signing_string.encode('utf-8'), hashlib.sha256).digest()
signature_base64 = base64.b64encode(signature).decode('utf-8')

# 构建请求头
headers = {
  "Date": gmt_time,
  "Digest": f"SHA-256={base64.b64encode(hashlib.sha256(body.encode('utf-8')).digest()).decode('utf-8')}",
  "Authorization": (
    f'Signature keyId="{key_id}",algorithm="{algorithm}",'
    f'headers="request-target date digest",'
    f'signature="{signature_base64}"'
  ),
  "Content-Type": "application/json"
}

# 定义基地址
base_url = "http://10.170.249.86:9901"  # 替换为实际的服务端点
url = base_url + request_path  # 拼接完整 URL

# 发送 POST 请求
try:
    response = requests.post(url, headers=headers, data=body.encode('utf-8'))
    response.encoding = 'utf-8'

    # 输出响应状态码和内容
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)  # 根据实际需求可改为 response.json()
except requests.exceptions.RequestException as e:
    print(f"请求发生异常：{e}")