#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hashlib
import hmac
import json
import sys
from datetime import datetime, timezone

import requests
import sseclient  # pip install sseclient-py

# ----------------- 参数配置 -----------------
key_id       = "longyuan-common-chat"
secret_key   = b"5b0d907e24926125f5646302e43d0c2f"
request_path = "/digital-artisan-chat2/supervision/api/stream"
# base_url     = "http://10.170.249.86:9901"
base_url     = "http://10.170.249.86:6600"# 如需 6600 端口请自行替换
url          = base_url + request_path

gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

body = {
    "userId": "1a32ad12f32f",
    "userToken": "9a5c1e1686b1ea73d0ed8828a76a3048|WEB|2cef0db99aa24504922744940cbc9390",
    "regionRights": ["黑龙江", "北京"],
    "assistantId": "1104",
    "question": "这些场站存在什么共性问题？",
    "selectedDoc": [
        "081-国能陕西新能源新庄风电场二期-2024技术监督查评报告.pdf",
        "027 湖北龙源新能源有限公司叶家河光储电站2024年技术监督查评报告-2024.pdf"
    ],
    "conversationId": "1",
    "requestId": "99c90740ad104ba1a3ec79dc76761d3a"
}
body_json = json.dumps(body, ensure_ascii=False)

# ----------------- 打印“每一步” -----------------
print("【1】构造待签名字符串...")
signing_string = f"{key_id}\nPOST {request_path}\ndate: {gmt_time}\n"
print("signing_string =\n" + signing_string)

print("【2】使用 HMAC-SHA256 计算签名...")
signature = hmac.new(secret_key, signing_string.encode('utf-8'), hashlib.sha256).digest()
signature_b64 = base64.b64encode(signature).decode()
print("signature(base64) =", signature_b64)

print("【3】计算请求体 SHA-256 Digest...")
body_digest = base64.b64encode(hashlib.sha256(body_json.encode()).digest()).decode()
print("Digest: SHA-256=" + body_digest)

headers = {
    "Date": gmt_time,
    "Digest": f"SHA-256={body_digest}",
    "Authorization": (
        f'Signature keyId="{key_id}",algorithm="hmac-sha256",'
        f'headers="@request-target date",signature="{signature_b64}"'
    ),
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}
print("【4】构造 headers...")
for k, v in headers.items():
    print(f"  {k}: {v}")

print("\n【5】准备发送 POST 流式请求...")
print("POST", url)
print("-" * 60)

# ----------------- 发送 & 逐行打印 -----------------
try:
    resp = requests.post(url, headers=headers, data=body_json, stream=True, timeout=120)
    print("【6】HTTP 响应状态码:", resp.status_code, resp.reason)
    if resp.status_code != 200:
        print("非 200 响应，完整 body：")
        print(resp.text)
        sys.exit(1)

    # 使用 SSE 客户端逐行解析
    client = sseclient.SSEClient(resp)
    for event in client.events():
        try:
            payload = json.loads(event.data)
        except json.JSONDecodeError:
            # 不是 JSON 就原样打印
            print("[RAW]", event.data)
            continue

        # 如果有 thought 字段，先打印思考过程
        if "thought" in payload and payload["thought"]:
            print("[THINK]", payload["thought"])

        # 如果有增量文本，打印出来
        if "delta" in payload and payload["delta"]:
            print("[DELTA]", payload["delta"], end="", flush=True)

        # 结束标志
        if payload.get("finish") is True:
            print("\n[FINISH] 服务器返回 finish=true，流结束。")
            break

except requests.exceptions.RequestException as e:
    print("【X】网络异常：", e)
    print("请确认：")
    print("  - 地址 http://10.170.249.86:9901 是否可访问？")
    print("  - 端口 9901/6600 是否已放行？")
    print("  - 是否在 VPN/内网环境？")