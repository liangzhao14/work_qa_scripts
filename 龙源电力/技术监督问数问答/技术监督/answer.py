import requests
import json
import pandas as pd

# 接口信息
API_URL = "http://10.170.129.69/teach_data_api/conversation/question11"  # 替换为实际的接口地址
REQUEST_METHOD = "POST"  # 请求方式
HEADERS = {
    "Content-Type": "application/json"
}  # 请求头，根据实际情况调整


# 从文件中逐行读取问题
def read_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        questions = file.readlines()
    return [q.strip() for q in questions]


# 创建请求体
def create_request_body(question, custom_data=None):
    payload = {
        "query": question
    }
    if custom_data:
        payload.update(custom_data)
    return payload


# 发送请求获取回答
def get_answer(payload):
    try:
        response = requests.request(REQUEST_METHOD, API_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()  # 检查 HTTP 错误
        if response.text:  # 检查响应内容是否为空
            try:
                # 解析流式返回的 JSON 数据
                lines = response.text.splitlines()
                data_list = [json.loads(line.split(":", 1)[1]) for line in lines if line.startswith("data:")]
                return data_list  # 返回所有数据
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}")
                print(f"Response content: {response.text}")
                return [{"error": f"JSON decode error: {json_err}"}]
        else:
            print("Warning: Empty response")
            return [{"error": "No response from API"}]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return [{"error": f"HTTP error: {http_err}"}]
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return [{"error": f"Request error: {err}"}]


# 将问题和回答保存到 Excel
def save_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["问题", "回答"])
    df.to_excel(output_file, index=False)


# 主函数
def main():
    question_file = "questions.txt"  # 问题文件路径
    output_excel = "qa_results.xlsx"  # 输出的 Excel 文件路径

    # 自定义请求体数据
    custom_data = {"type": 1, "startTime": "2023-06-11", "endTime": "2025-06-11",
                   "newEnergyStationList": ["CWtGguHN", "nW0bU308", "hyHV7Wlq", "1Pim9xjT", "UC569CND", "THxv1amx",
                                            "GxmREmJb", "G7IiT1bV", "Gf3RfDc", "9b9ae376f86e4141b088c54286b41677",
                                            "536e9f2524a14e4eab308ba89f6ce3fb", "b34jRudF", "bGhv16L9", "F9hKjq6y",
                                            "766e727c90a44050b29eee7324fb151b", "OxY6Fw3y", "GsJsFdc", "ahe2vKD5",
                                            "LyXsFdc", "9110f6d46d9245ec9e99c3d113ca92f7", "2024012203",
                                            "57467ca5a0c8491da1e56096a4ed4d11", "226058b95a7b4211865a6a75c1f612dc",
                                            "107fdf70e0ac443e912c2053705709ac", "NR885fyp", "6qHg7uxz", "gdFdC079",
                                            "FhPMT87r", "YZpMeKzU", "UedykAoI", "VtBVtO7H", "T0BZjEQI", "l0dKsWvi",
                                            "e2b346e6e572401c89b0b37cc4ceec6f", "ec66b04bbca042d68b662157cb924586",
                                            "lnh99UVO", "qi4Il4G4", "2023070302", "zT4z7t9e", "Rc8HPTq0", "Wj1rOAWU",
                                            "m6N9sn8Q", "nVIe06Pe", "clNPs71W", "4a5923682885473fab50fcea74ecd35a",
                                            "24901e7c1ebb46ff89aa20a70c6d71c3", "a8e7ac2875e74891856baf1033437fcb",
                                            "989b758829e244a284fd1df457437091", "28ebbfb077b14255849110f4aa79a332",
                                            "11567e1b7eef40f98cdc5309d331575a", "aa93OPzX", "Euil45F5", "xfwiaWwr",
                                            "iaiUir5a", "b77f62ea640749b9aa36ba651d516c4d", "tpqV127T", "Lk9IqJ8G",
                                            "f723jLQU", "506e5cc66c1342e6a1b39748dc25f108",
                                            "3bbc3d1fae4c4abd8a414a1dbc8e6d89", "ELegM61o", "TZ6ANEHv", "JmQSl7a5",
                                            "Ll8QUCby", "eFYbmVVc", "mGYmG2x6", "Q0A0jY6J", "dP5go1O9", "Jr3UtGjN",
                                            "dhAxcQg9", "dPl1QyAj", "NVMmyB9q", "HljTxFd01Fdc", "ycZTiEYo", "dJNRu1MS",
                                            "eZN06fAA", "lq2hsJyN", "Grpx35pK", "AWELp1UK", "7yzWsOa1", "FdGxj01Dc",
                                            "HljFdH3Fc", "72f5baab39ba48d298ddfd3549a9a80a", "wG14tEsv",
                                            "58c43915adcc41e487ac127234632406", "6d81a0ab07c24ae6bf6b29fff3accb81",
                                            "154318", "d4babe19bc004932855a9af01baeb24e",
                                            "652fd59c86b1406aa5bee62badc8b18f", "o4aA91ON", "UlA17HNy", "qRMaXNtJ",
                                            "tTZ5Ov1z", "dF9ApNSD", "HGDBz6ad", "LyJlWzFDC", "LyJlQyFDC", "HpNe06io",
                                            "YE6vqa24", "rRtk6Ze5", "YXuiVtOl", "WKVdDW4v", "ReqoQ9aP", "00vlTDRL",
                                            "B1ebhLdk", "WszZx7DQ", "XHxW9c3c", "28PBtq74", "uLKo3FbJ", "QyjyWLri",
                                            "H5NOBSeQ", "i3HWcIW8", "hqwOpreW", "MGUotN74",
                                            "6ee1305e1ebe4a7884240d68ade2ad0e", "mzF9K28e",
                                            "8785131b47324abb8aff259d6bb90a35", "yW889wNd", "eoV9VSU2", "LPFDC",
                                            "24031102", "64", "7025cd6359bb4cd0ba4d68c109f575bb", "65",
                                            "086c2f896e8549b9853e6239633b3feb", "oPXPeRUv", "ikir9ROk", "pekauW3w",
                                            "3Vy3dSPy", "9KgGAUQz", "wXb70kLH", "7ZJDYx3k", "WILAUbOJ", "9CKxe8Y3",
                                            "LOwSHgbZ", "xjeiTuId", "QlkRDn22", "Iiw67fRA", "uns1awty", "7O9zUAZY",
                                            "WEgqSTq8", "ky90MlWv", "OGPeMo60", "2023011929", "lJ3pwm6R", "TvehP8v6",
                                            "a703d92507ee4e1284de65689fb36e34", "m6jtF46W", "5gC509dJ", "X0sJ984W",
                                            "CIE94tIr", "LzpEXxO9", "UMVgbOHi", "66WZT0sN", "aIbLHnMU", "i1hP6XNk",
                                            "QwFiGZqD", "IllPy58U", "dKDlKvMt", "MX8hsfdcB",
                                            "b090b555659a4790a12230eecd00a2a6", "7ad9b57598514208beeedb5d6ef9d480",
                                            "742436aa32bf48d7989d6361dc010443", "09a2384e9f284862ac2aa78d52e17b2f",
                                            "0a259b2b11034e17862a41609ecd1ae4", "5cdb3fea6d604d4699c969afd3f991ef",
                                            "MxBLKFcDz", "LdgaHD36", "35KrxS5s", "aH50UFTG", "6aG9Q6n9", "A4oOeWCH",
                                            "4XYfk5wb", "scJnZzQR", "VMyRvpQw", "HRX65u7d", "nNZUJQCQ", "p58jTfwJ",
                                            "c8e59131442e4c94b6b023c1e6a272ee", "479b59154a154c55bd5cea7938e67f4c",
                                            "Knl5e69I", "s8tG1YD6", "16c14068392f4af1b65ce8deee76c2c4", "gw81pFZM",
                                            "dzELC3O0", "2023011912", "e3baabe4d4754effa452a229cd93b098",
                                            "1de35b827e8a4433a25623826f7b206d", "P2qa0YG4", "i7OBYb40", "kPBhhp40",
                                            "SL69sdlk", "BLn6sDYE", "74a9TZ4y", "216xHecY", "XO3bs7C9", "66",
                                            "XXt7zwk4", "MSq1g80q", "sqFWR933", "93603f8196844a468e3aa069e760c3cf",
                                            "1689048f412f4a7b82d3c99cd24cc2ea", "67", "b7K4UqfP", "o0nIM4xg",
                                            "VKFNSzh2", "fhaNHqrk", "wucakdUr", "1qOq3ihv", "MMyC0xoJ", "Ze2XKLZg",
                                            "p8ZCbmZ9", "5ywN6Fx6", "vnxXK900", "814dca98718048099400e258ccf0f289",
                                            "JmeOA355", "V55XgoB8", "9pQruht9", "tcA3xqpS", "XAucjhIN", "F9te0QCC",
                                            "CQfdQS1W", "JSFDqq2wA", "00218b1cf9fe47079d8b2ee5ecb7b125",
                                            "521335b68d4740c1af56eca3a15566ec", "HDwK0x90",
                                            "dde6a65703074e4d859e312b88179843", "ce79b771eb3e4444bef9396dc9cf1d85",
                                            "47384f989878466f9be854a0db357e34", "851d0b2aa2584bc0bf3c4e6e67c9f7a2",
                                            "c1de217d56a64041baf75c1618760f2a", "e41ffa323cdc4c9ea318290cb031a3d6",
                                            "dongpanfengdianchang", "DPV69", "U88UZanH",
                                            "bff2768ecfe5426bbfa61641680ee70f", "o3ZgAl5a", "wcUBl6X4",
                                            "1b84e803b1e6477c8421950d69e26de3", "4851e2123897474486ac64b7fc68c4c1",
                                            "4RP9A7Y1", "ekbjbQDQ", "CHQ67spw", "saQBQdRR", "vwokn0Xq", "Cz9HLHN7",
                                            "zL5e0piX", "51PjQYwA", "29c1193eefb3431182530de9b85edd0c", "2023070305",
                                            "68", "de22a5bd746c44ba92082d397b4c8eee", "mfw40WUA",
                                            "46651feb3d594a0a8db768d0294a848d", "dpv70", "2024012205",
                                            "e7278ee43b5943629be514d90575a189", "6b1ddaf37d2c4a6481f0364d34de3281"]}

    questions = read_questions(question_file)
    qa_data = []

    for question in questions:
        payload = create_request_body(question, custom_data)
        response = get_answer(payload)

        if response and "error" in response[0]:
            qa_data.append([question, response[0]["error"]])
        else:
            # 合并所有返回的数据为一个完整的回答
            complete_answer = ""
            for data in response:
                if "thinkText" in data:
                    complete_answer += data["thinkText"].strip() + " "
                if "answerText" in data:
                    complete_answer += data["answerText"].strip()

            # 去除多余的空格
            complete_answer = complete_answer.strip()

            # 添加到数据列表
            qa_data.append([question, complete_answer if complete_answer else "No answer from API"])

        # 打印到控制台（以 Markdown 格式）
        print(f"### 问题\n{question}\n")
        print(f"### 回答\n{complete_answer if complete_answer else 'No answer from API'}\n")

    # 保存到 Excel
    save_to_excel(qa_data, output_excel)
    print(f"问答结果已保存到 {output_excel}")


if __name__ == "__main__":
    main()