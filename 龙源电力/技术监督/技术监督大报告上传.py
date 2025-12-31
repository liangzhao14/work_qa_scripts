import base64
import hashlib
import hmac
from datetime import datetime, timezone
import requests
import json

# 获取当前时间的GMT格式
gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

# 配置密钥和请求信息
key_id = "longyuan-common-chat"
secret_key = b"5b0d907e24926125f5646302e43d0c2f"
request_method = "POST"
request_path = "/digital-artisan-space/api/supervision/file/myUpload"
algorithm = "hmac-sha256"
body = {
    "splitType": 7,
    "position": "/0/",
    "parentId": 0,
    "spaceId": 1334,
    "categoryOneId": 2373,
    "fileName": "D:/Users/admin/Desktop/case design/word/测试批注-006云南新能源公司祥云县朝阳村光伏项目2024年技术监督查评报告.docx"
}

# 构造签名字符串
signing_string = (
    f"{key_id}\n"
    f"{request_method} {request_path}\n"
    f"date: {gmt_time}\n"
)

# 生成签名
signature = hmac.new(secret_key, signing_string.encode('utf-8'), hashlib.sha256).digest()
signature_base64 = base64.b64encode(signature).decode('utf-8')

# 将字典转换为JSON格式的字符串并计算SHA-256摘要
body_json = json.dumps(body, sort_keys=True)  # 使用sort_keys=True确保字典的顺序一致
body_digest = hashlib.sha256(body_json.encode('utf-8')).digest()
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
    "Content-Type": "application/json"  # 指定内容类型为JSON
}

# 定义基地址（需根据实际情况替换）
base_url = "http://10.170.249.86:9901"  # 请替换为实际的服务端点
url = base_url + request_path  # 拼接完整URL

# 发送POST请求
try:
    response = requests.post(url, headers=headers, json=body)  # 使用json参数发送JSON数据
    response.encoding = 'utf-8'

    # 输出响应状态码和内容
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)  # 根据实际需求可改为response.json()
except requests.exceptions.RequestException as e:
    print(f"请求发生异常：{e}")