import base64
import hashlib
import hmac
from datetime import datetime, timezone
import requests
import json

# -------------------------------------------------
print("【Step 0】准备基础变量")
# -------------------------------------------------
gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
print(f"GMT 时间: {gmt_time}")

key_id = "longyuan-common-chat"
secret_key = b"5b0d907e24926125f5646302e43d0c2f"
request_method = "POST"
request_path = "/digital-artisan-chat2/botChat/api/stream"
algorithm = "hmac-sha256"
print(f"key_id: {key_id}")
print(f"secret_key: {secret_key}")
print(f"request_method: {request_method}")
print(f"request_path: {request_path}")
print(f"algorithm: {algorithm}")

# -------------------------------------------------
print("\n【Step 1】构造请求体 body")
# -------------------------------------------------
body = {
    "question": "生成甘肃龙源2025年运行分析报告",
    "noTyping": "false",
    "assistantId": 1113,
    "commonModelId": 33,
    "regionRights": ["龙源电力", "甘肃"]
}
print("body 内容:")
print(json.dumps(body, ensure_ascii=False, indent=2))

# -------------------------------------------------
print("\n【Step 2】生成签名字符串 signing_string")
# -------------------------------------------------
signing_string = (
    f"{key_id}\n"
    f"{request_method} {request_path}\n"
    f"date: {gmt_time}\n"
)
print("signing_string:")
print(repr(signing_string))  # repr 让换行符可见

# -------------------------------------------------
print("\n【Step 3】计算 HMAC-SHA256 签名")
# -------------------------------------------------
signature = hmac.new(secret_key, signing_string.encode('utf-8'), hashlib.sha256).digest()
signature_base64 = base64.b64encode(signature).decode('utf-8')
print("signature (Base64):", signature_base64)

# -------------------------------------------------
print("\n【Step 4】序列化并编码 body")
# -------------------------------------------------
body_json = json.dumps(body, ensure_ascii=False)
body_bytes = body_json.encode('utf-8')
print("body_json:\n", body_json)
print("body_bytes 长度:", len(body_bytes))

# -------------------------------------------------
print("\n【Step 5】计算 body 的 SHA-256 Digest")
# -------------------------------------------------
body_digest = hashlib.sha256(body_bytes).digest()
body_digest_base64 = base64.b64encode(body_digest).decode('utf-8')
print("Digest (Base64):", body_digest_base64)

# -------------------------------------------------
print("\n【Step 6】构造最终 headers")
# -------------------------------------------------
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
print("headers:")
for k, v in headers.items():
    print(f"  {k}: {v}")

# -------------------------------------------------
print("\n【Step 7】拼接完整 URL")
# -------------------------------------------------
# 请根据实际可访问的地址切换
base_url = "http://10.170.249.86:6600"  # 或 9901
url = base_url + request_path
print("完整 URL:", url)

# -------------------------------------------------
print("\n【Step 8】发送 POST 请求")
# -------------------------------------------------
try:
    print(">>> 正在发送请求 ...")
    response = requests.post(url, headers=headers, data=body_json, timeout=60)
    response.encoding = 'utf-8'
    print("\n【响应状态码】", response.status_code)
    print("\n【响应头】")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")
    print("\n【响应正文】")
    print(response.text)
except requests.exceptions.RequestException as e:
    print("\n【请求异常】", e)
    print("提示：当前网络可能无法访问该地址，请确认：")
    print("1) 你是否处于内网或已连接 VPN；")
    print("2) 10.170.249.86:6600/9901 是否真的在线；")
    print("3) 尝试浏览器直接访问或 `telnet 10.170.249.86 6600` 看能否连通。")