import base64
import hashlib
import hmac
from datetime import datetime, timezone
import requests  # 新增：导入requests库用于发送HTTP请求

gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

key_id = "longyuan-common-chat"
secret_key = b"5b0d907e24926125f5646302e43d0c2f"
request_method = "post"
request_path = "/digital-artisan-analyze/data/api/getChatHistory"
algorithm = "hmac-sha256"
body = """{


  "userId": "1a32ad12f32f",
  "userToken": "9a5c1e1686b1ea73d0ed8828a76a3048|WEB|6de60bb3cede4f4dab7b149a371a4ceb",
  "regionRights": [
    "黑龙江",
    "北京"
  ],
    "assistantId": "1104"

}"""

# 构造签名字符串
signing_string = (
    f"{key_id}\n"
    f"{request_method} {request_path}\n"
    f"date: {gmt_time}\n"
)

# 生成签名
signature = hmac.new(secret_key, signing_string.encode('utf-8'), hashlib.sha256).digest()
signature_base64 = base64.b64encode(signature).decode('utf-8')

# 计算请求体的SHA-256摘要并Base64编码
body_digest = hashlib.sha256(body.encode('utf-8')).digest()
body_digest_base64 = base64.b64encode(body_digest).decode('utf-8')

# 构造请求头
headers = {
    "Date": gmt_time,
    "Digest": f"SHA-256={body_digest_base64}",
    "Authorization": (
        f'Signature keyId="{key_id}",algorithm="{algorithm}",'
        f'headers="@request-target date",'
        f'signature="{signature_base64}"'
    ),
    "Content-Type": "application/json"  # 新增：指定内容类型为JSON
}

# 定义基地址（需根据实际情况替换）
base_url = "http://10.170.249.86:9901"  # 请替换为实际的服务端点
url = base_url + request_path  # 拼接完整URL

# 发送POST请求
try:

    response = requests.post(url, headers=headers, data=body)
    response.encoding = 'utf-8'

    # 输出响应状态码和内容
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)  # 根据实际需求可改为response.json()
except requests.exceptions.RequestException as e:
    print(f"请求发生异常：{e}")
