import requests
import pandas as pd
import json

# 定义接口的URL
# API_URL = "http://10.170.128.157:9004/pvWind/queryWindEnergyRateMonth" # 风能利用率
# API_URL = "http://10.170.128.157:9004/dk/query" # 日报月报
# API_URL = "http://10.170.128.157:9004/windpower/queryWindPowerDown" # 停机记录
# API_URL = "http://10.170.128.157:9004/dk/queryFanCommunicationInterruption" # 通讯中断
API_URL = "http://10.170.128.157:9004/pvWind/queryWindWgz" # 长周期
# API_URL = "" # 台账


# 读取Excel文件
def read_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None


# 调用接口并获取返回结果
def call_api(payload):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回JSON格式的响应数据
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"其他错误: {e}")
    return None


# 主程序
def main():
    input_file = "input.xlsx"  # 输入文件路径
    output_file = "output.xlsx"  # 输出文件路径

    df = read_excel(input_file)
    if df is None:
        return

    if '入参' not in df.columns:
        print("Excel文件中缺少'入参'列！")
        return

    # 创建一个空列表来存储出参结果
    out_params = []

    # 遍历每一行，调用接口并打印入参和出参
    for index, row in df.iterrows():
        in_param = row['入参']
        try:
            # 将入参从字符串转换为JSON对象
            in_param_json = json.loads(in_param)
            # 调用接口
            out_param = call_api(in_param_json)
            # 将出参结果格式化为美观的JSON字符串
            formatted_out_param = json.dumps(out_param, ensure_ascii=False, indent=4)
            # 将格式化后的出参结果添加到列表中
            out_params.append(formatted_out_param)
            # 打印入参和出参
            print(f"入参: {in_param}")
            print(f"出参: {formatted_out_param}")
            print("-" * 50)  # 分隔线
        except json.JSONDecodeError as e:
            print(f"第 {index + 1} 行的入参格式错误: {e}")
            out_params.append("格式错误")

    # 将出参结果写入到新的列中
    df['出参'] = out_params

    # 将结果写入新的Excel文件
    df.to_excel(output_file, index=False)
    print(f"结果已写入到文件: {output_file}")


if __name__ == "__main__":
    main()