import requests
import json
import uuid
import pandas as pd
from requests.exceptions import RequestException, Timeout

# 接口地址
# api_url = "http://10.170.249.86:8800/digital-artisan-chat2/botChat/stream"
# api_url = "http://10.170.249.86:8800/digital-artisan-chat2/h5/stream"
api_url = "http://10.170.249.86:8800/digital-artisan-chat2/botChat/stream"


# def generate_request_id():
#     """生成唯一的requestId"""
#     return str(uuid.uuid4())


# def generate_conversation_id():
#     """生成唯一的conversationId（示例，实际可能需要从历史对话获取）"""
#     return str(uuid.uuid4())


# 动态构建请求体（避免固定ID导致的问题）
def build_request_body(question):
    return {
        "question": question.strip(),
        "assistantId": 1113,
        "image": "",
        "requestId": "",
        "commonModelId": 44,
    }

# def build_request_body(question):
#     return {
#         "question": question.strip(),
#         "appKey": "ZXMQ1942485102093271040OOQ"
#     }


# 调用接口（设置超时时间为60秒）
def call_api(request_body):
    headers = {
        "Content-Type": "application/json",
        "artisan-token": "9a5c1e1686b1ea73d0ed8828a76a3048|WEB|148a93a4c99f45e7a846390e0a499caa"  # 替换为有效token
    }
    try:
        # 关键设置：超时时间60秒（连接+读取总时长）
        response = requests.post(
            api_url,
            json=request_body,
            headers=headers,
            stream=True,
            timeout=120  # 总超时60秒
        )
        response.raise_for_status()  # 检查HTTP状态码（非200会抛出异常）
        return response
    except Timeout:
        # 明确处理超时异常（不中断流程）
        print(f"接口调用超时（60秒未响应），问题处理为空。")
        return None
    except RequestException as e:
        # 其他网络异常（如DNS失败、连接拒绝等）
        print(f"接口请求失败（非超时）: {str(e)}，问题处理为空。")
        return None


# 从响应数据中提取parseDesc（核心逻辑）
def extract_parse_desc(data):
    """从接口返回的JSON数据中提取parseDesc字段"""
    try:
        if "dataMessage" in data and isinstance(data["dataMessage"], dict):
            return data["dataMessage"].get("parseDesc")
        return None
    except (KeyError, TypeError):
        return None


# 处理接口返回的流式内容（收集parseDesc并打印）
def process_response(response, question):
    parse_descs = []  # 存储当前问题的所有parseDesc

    if not response:
        print(f"问题 [{question}]：无有效响应（超时或网络错误）")
        return parse_descs

    try:
        response.encoding = 'utf-8'

        for line in response.iter_lines():
            if not line:
                continue

            line_str = line.decode('utf-8').strip()
            if line_str.startswith("data:"):
                json_str = line_str[5:].strip()
                try:
                    data = json.loads(json_str)
                    parse_desc = extract_parse_desc(data)
                    if parse_desc:
                        print(f"问题 [{question}]：回答 → {parse_desc}")
                        parse_descs.append(parse_desc)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"问题 [{question}] 处理响应时发生未知错误: {str(e)}")

    return parse_descs


# 主函数（超时后继续处理下一行）
def main():
    input_file = "input.txt"
    excel_output = "chat_results.xlsx"

    # 读取问题列表
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            questions = [line.strip() for line in f if line.strip()]
        if not questions:
            print(f"错误：文件 {input_file} 内容为空或全为空行。")
            return
    except Exception as e:
        print(f"读取文件失败: {str(e)}")
        return

    all_results = []
    max_answers = 0

    for question in questions:
        print(f"\n正在处理问题：{question}")
        try:
            request_body = build_request_body(question)
            response = call_api(request_body)  # 可能返回None（超时/网络错误）

            parse_descs = process_response(response, question)
            current_answer_count = len(parse_descs)

            if current_answer_count > max_answers:
                max_answers = current_answer_count

            all_results.append({
                "问题": question,
                "回答列表": parse_descs
            })
            print(f"问题 [{question}] 处理完成，获取到 {current_answer_count} 条回答。")

        except Exception as e:
            # 理论上不会触发，因call_api已处理异常
            all_results.append({
                "问题": question,
                "回答列表": []
            })
            print(f"问题 [{question}] 处理时发生未知错误: {str(e)}")

    # 生成Excel数据
    output_data = []
    if max_answers > 0:
        columns = ["问题"] + [f"回答{i}" for i in range(1, max_answers + 1)]
    else:
        columns = ["问题"]

    for result in all_results:
        row = {"问题": result["问题"]}
        answer_list = result["回答列表"]
        for i in range(1, max_answers + 1):
            row[f"回答{i}"] = answer_list[i - 1] if (i - 1 < len(answer_list)) else ""
        output_data.append(row)

    # 写入Excel
    try:
        df = pd.DataFrame(output_data)
        df.to_excel(excel_output, index=False, engine='openpyxl')
        print(f"\n所有问题处理完成！结果已写入Excel：{excel_output}")
        print(f"总行数：{len(output_data)}，最大回答数：{max_answers}")
    except Exception as e:
        print(f"写入Excel失败: {str(e)}")


if __name__ == "__main__":
    main()