import base64
import hashlib
import hmac
from datetime import datetime, timezone
import requests
import json

gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

key_id = "longyuan-common-chat"                # key id
secret_key = b"5b0d907e24926125f5646302e43d0c2f"    # secret key
request_method = "POST"             # HTTP method
request_path = "/digital-artisan-chat2/dialog/api/guideQuestion"              # route URI
algorithm= "hmac-sha256"           # can use other algorithms in allowed_algorithms
body = {
    "assistantId": 946,
    "userId": "longyuanuser",
    "question": "联合动力1.5MW机组齿轮箱温控阀如何更换？",
    "userToken": "",
    "regionRights": []
}


signing_string = (
  f"{key_id}\n"
  f"{request_method} {request_path}\n"
  f"date: {gmt_time}\n"
)


# create signature
signature = hmac.new(secret_key, signing_string.encode('utf-8'), hashlib.sha256).digest()
signature_base64 = base64.b64encode(signature).decode('utf-8')

# 将字典转换为 JSON 格式的字符串并编码为字节串
body_json = json.dumps(body, ensure_ascii=False)
body_bytes = body_json.encode('utf-8')

# create the SHA-256 digest of the request body and base64 encode it
body_digest = hashlib.sha256(body_bytes).digest()
body_digest_base64 = base64.b64encode(body_digest).decode('utf-8')

headers = {
  "Date": gmt_time,
  "Digest": f"SHA-256={body_digest_base64}",
  "Authorization": (
    f'Signature keyId="{key_id}",algorithm="{algorithm}",'
    f'headers="@request-target date",'
    f'signature="{signature_base64}"'
  ),
  "Content-Type": "application/json"
}


# 定义基地址（需根据实际情况替换）
base_url = "http://10.170.249.86:9901"  # 替换为实际的服务端点
url = base_url + request_path  # 拼接完整 URL



# 发送 POST 请求
try:
    response = requests.post(url,headers=headers, data=body_json)
    response.encoding = 'utf-8'


    print(response.text)  # 根据实际需求可改为 response.json()
except requests.exceptions.RequestException as e:
    print(f"请求发生异常：{e}")

