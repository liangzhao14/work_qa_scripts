import requests
import json

# 接口地址
api_url = "http://10.170.249.86:8801/digital-artisan-chat2/botChat/stream"

# 固定的请求体
request_body = {
    "question": "截至2025年3月底，萩芦风电场利用小时与去年同比情况做一下比较。",
    "spaceIds": [],
    "docIds": [],
    "selectModelIds": [],
    "assistantId": 1113,
    "image": "",
    "requestId": "c9bfd1ae-c793-41ab-ba1c-ca6b65b4bb1b",  # 使用平台上的成功 requestId
    "commonModelId": 39,
    "conversationId": "a16afffb93f14cb4916a9685d322279a"  # 使用平台上的成功 conversationId
}

# 调用接口
def call_api(request_body):
    headers = {
        "Content-Type": "application/json",
        "artisan-token": "9a5c1e1686b1ea73d0ed8828a76a3048|WEB|cff932eefdc4440283a628ea48c87e5d"
    }
    response = requests.post(api_url, data=json.dumps(request_body), headers=headers, stream=True)
    return response

# 处理接口返回的内容
def process_response(response):
    try:
        # 逐行解析返回的内容
        for line in response.iter_lines():
            if line:
                # 去掉每行的 "data:" 前缀
                line = line.decode('utf-8')
                if line.startswith("data:"):
                    line = line[5:].strip()
                    # 解析 JSON 数据
                    data = json.loads(line)
                    print(f"完整的返回数据：{data}")
                    if "dataMessage" in data and "parseDesc" in data["dataMessage"]:
                        parse_desc = data["dataMessage"]["parseDesc"]
                        question = request_body["question"].strip()  # 去掉问题末尾的换行符
                        print(f"问题：{question}")
                        print(f"回答：{parse_desc}")
                        print("-" * 50)
                    elif "answerText" in data:
                        answer_text = data["answerText"]
                        print(f"问题：{request_body['question'].strip()}")
                        print(f"回答：{answer_text}")
                        print("-" * 50)
    except json.JSONDecodeError as e:
        print(f"解析 JSON 时发生错误：{e}")
    except Exception as e:
        print(f"发生错误：{e}")

# 主函数
def main():
    # 调用接口
    response = call_api(request_body)

    # 处理返回的内容
    process_response(response)

if __name__ == "__main__":
    main()