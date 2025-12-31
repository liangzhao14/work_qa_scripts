import requests
import json
import pandas as pd
import os

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

# 生成唯一的文件名
def generate_unique_filename(base_name, extension):
    counter = 1
    while True:
        filename = f"{base_name}_{counter}.{extension}"
        if not os.path.exists(filename):
            return filename
        counter += 1

# 主函数
def main():
    question_file = "questions.txt"  # 问题文件路径
    base_output_excel = "qa_results"  # 输出的 Excel 文件基础名称

    # 自定义请求体数据
    custom_data = {"type":1,"startTime":"2023-06-12","endTime":"2025-06-12",
"newEnergyStationList":["CWtGguHN","nW0bU308","hyHV7Wlq","1Pim9xjT","UC569CND","THxv1amx","GxmREmJb","G7IiT1bV","Gf3RfDc","9b9ae376f86e4141b088c54286b41677","536e9f2524a14e4eab308ba89f6ce3fb","b34jRudF","bGhv16L9","F9hKjq6y","766e727c90a44050b29eee7324fb151b","OxY6Fw3y","GsJsFdc","ahe2vKD5","LyXsFdc","9110f6d46d9245ec9e99c3d113ca92f7","2024012203","57467ca5a0c8491da1e56096a4ed4d11","226058b95a7b4211865a6a75c1f612dc","107fdf70e0ac443e912c2053705709ac","NR885fyp","6qHg7uxz","gdFdC079","FhPMT87r","YZpMeKzU","UedykAoI","VtBVtO7H","T0BZjEQI","l0dKsWvi","e2b346e6e572401c89b0b37cc4ceec6f","ec66b04bbca042d68b662157cb924586","lnh99UVO","qi4Il4G4","2023070302","zT4z7t9e","Rc8HPTq0","Wj1rOAWU","m6N9sn8Q","nVIe06Pe","clNPs71W","4a5923682885473fab50fcea74ecd35a","24901e7c1ebb46ff89aa20a70c6d71c3","a8e7ac2875e74891856baf1033437fcb","989b758829e244a284fd1df457437091","28ebbfb077b14255849110f4aa79a332","11567e1b7eef40f98cdc5309d331575a","aa93OPzX","Euil45F5","xfwiaWwr","iaiUir5a","b77f62ea640749b9aa36ba651d516c4d","tpqV127T","Lk9IqJ8G","f723jLQU","506e5cc66c1342e6a1b39748dc25f108","3bbc3d1fae4c4abd8a414a1dbc8e6d89","ELegM61o","TZ6ANEHv","JmQSl7a5","Ll8QUCby","eFYbmVVc","mGYmG2x6","Q0A0jY6J","dP5go1O9","Jr3UtGjN","dhAxcQg9","dPl1QyAj","NVMmyB9q","HljTxFd01Fdc","ycZTiEYo","dJNRu1MS","eZN06fAA","lq2hsJyN","Grpx35pK","AWELp1UK","7yzWsOa1","FdGxj01Dc","HljFdH3Fc","72f5baab39ba48d298ddfd3549a9a80a","wG14tEsv","58c43915adcc41e487ac127234632406","6d81a0ab07c24ae6bf6b29fff3accb81","154318","d4babe19bc004932855a9af01baeb24e","652fd59c86b1406aa5bee62badc8b18f","o4aA91ON","UlA17HNy","qRMaXNtJ","tTZ5Ov1z","dF9ApNSD","HGDBz6ad","LyJlWzFDC","LyJlQyFDC","HpNe06io","YE6vqa24","rRtk6Ze5","YXuiVtOl","WKVdDW4v","ReqoQ9aP","00vlTDRL","B1ebhLdk","WszZx7DQ","XHxW9c3c","28PBtq74","uLKo3FbJ","QyjyWLri","H5NOBSeQ","i3HWcIW8","hqwOpreW","MGUotN74","6ee1305e1ebe4a7884240d68ade2ad0e","mzF9K28e","8785131b47324abb8aff259d6bb90a35","yW889wNd","eoV9VSU2","LPFDC","24031102","64","7025cd6359bb4cd0ba4d68c109f575bb","65","086c2f896e8549b9853e6239633b3feb","oPXPeRUv","ikir9ROk","pekauW3w","3Vy3dSPy","9KgGAUQz","wXb70kLH","7ZJDYx3k","WILAUbOJ","9CKxe8Y3","LOwSHgbZ","xjeiTuId","QlkRDn22","Iiw67fRA","uns1awty","7O9zUAZY","WEgqSTq8","ky90MlWv","OGPeMo60","2023011929","lJ3pwm6R","TvehP8v6","a703d92507ee4e1284de65689fb36e34","m6jtF46W","5gC509dJ","X0sJ984W","CIE94tIr","LzpEXxO9","UMVgbOHi","66WZT0sN","aIbLHnMU","i1hP6XNk","QwFiGZqD","IllPy58U","dKDlKvMt","MX8hsfdcB","b090b555659a4790a12230eecd00a2a6","7ad9b57598514208beeedb5d6ef9d480","742436aa32bf48d7989d6361dc010443","09a2384e9f284862ac2aa78d52e17b2f","0a259b2b11034e17862a41609ecd1ae4","5cdb3fea6d604d4699c969afd3f991ef","MxBLKFcDz","LdgaHD36","35KrxS5s","aH50UFTG","6aG9Q6n9","A4oOeWCH","4XYfk5wb","scJnZzQR","VMyRvpQw","HRX65u7d","nNZUJQCQ","p58jTfwJ","c8e59131442e4c94b6b023c1e6a272ee","479b59154a154c55bd5cea7938e67f4c","Knl5e69I","s8tG1YD6","16c14068392f4af1b65ce8deee76c2c4","gw81pFZM","dzELC3O0","2023011912","e3baabe4d4754effa452a229cd93b098","1de35b827e8a4433a25623826f7b206d","P2qa0YG4","i7OBYb40","kPBhhp40","SL69sdlk","BLn6sDYE","74a9TZ4y","216xHecY","XO3bs7C9","66","XXt7zwk4","MSq1g80q","sqFWR933","93603f8196844a468e3aa069e760c3cf","1689048f412f4a7b82d3c99cd24cc2ea","67","b7K4UqfP","o0nIM4xg","VKFNSzh2","fhaNHqrk","wucakdUr","1qOq3ihv","MMyC0xoJ","Ze2XKLZg","p8ZCbmZ9","5ywN6Fx6","vnxXK900","814dca98718048099400e258ccf0f289","JmeOA355","V55XgoB8","9pQruht9","tcA3xqpS","XAucjhIN","F9te0QCC","CQfdQS1W","JSFDqq2wA","00218b1cf9fe47079d8b2ee5ecb7b125","521335b68d4740c1af56eca3a15566ec","HDwK0x90","dde6a65703074e4d859e312b88179843","ce79b771eb3e4444bef9396dc9cf1d85","47384f989878466f9be854a0db357e34","851d0b2aa2584bc0bf3c4e6e67c9f7a2","c1de217d56a64041baf75c1618760f2a","e41ffa323cdc4c9ea318290cb031a3d6","dongpanfengdianchang","DPV69","U88UZanH","bff2768ecfe5426bbfa61641680ee70f","o3ZgAl5a","wcUBl6X4","1b84e803b1e6477c8421950d69e26de3","4851e2123897474486ac64b7fc68c4c1","4RP9A7Y1","ekbjbQDQ","CHQ67spw","saQBQdRR","vwokn0Xq","Cz9HLHN7","zL5e0piX","51PjQYwA","29c1193eefb3431182530de9b85edd0c","2023070305","68","de22a5bd746c44ba92082d397b4c8eee","mfw40WUA","46651feb3d594a0a8db768d0294a848d","dpv70","2024012205","e7278ee43b5943629be514d90575a189","6b1ddaf37d2c4a6481f0364d34de3281","4HfJU5CY","c08ZbEpE","5kHqlKmG","IJJjGwVf","JShSLhDf","JSpHhSDC","2024012204","mGyVv824","VmiwCmn8","04d8edb4bffb4074bd214f663c380dcb","M5u7bBUN","fd978ad0b0a540baa6b10687dea027f6","2023122013","ShSlZfWdFbs","ocm5SI12","2024012247","ce02be34b0f24fd283ed4fcd582d8fa7","5003ffbb25d545b8a39f8dadd9e8c9ea","67e14068cb0540daa2f82ccd98156a4c","b0a7f1ee229347a59115df862a399c4b","cmC54qFJ","2024012248","o79yx6NW","Rcf603BN","B2F3hmgk","JzEa3b51","SDbbU954","p8r2MCUW","ExLa571H","EpOpn1Tz","fu5lcAe8","N1nlWwat","6yA7bJTK","ALiZbgq3","GUH7tDeH","AhTcFdc","AhHbHyFbs","c128b280d4894ce0975f6f894433d8e2","T9dD4oXa","04109791baad4584919b7a247b254d11","a7443bc9708745c4b98663ba46cac375","sjqG5D6R","kh9Vq45Z","cbd48afcd90246d8ad5cf12ac8648c4f","vs49wAMJ","54b2c91fdd8341d384f8d1d1616672ab","de3fdb81d3b64abc83fd0af6ecd84328","Ad1Ot48R","wsXc8M95","e1b96183024c4341b44d7bc06f32d467","AhSzHyFbs","ly87pE1Y","Pgsa10W2","d49f4e21622041878b88e21ce997fb3c","8f7864fd2ad64854928f382793c208a2","QjUKG0bA","ql6filkl","c1ou9aB9","GbzeXrpb","wFhb9iGg","djk9eHGB","fJ7iDewh","2024012229","AHz90kee","fd2e0dede7aa48099afd7abcecfa0208","40019a29d7344dbcb52b9dea8ab1b565","dc89add640494c058fd23aa03a8400af","6f12d5a4fa544a1baca71c214bb3d1f8","124bbc68dc334455ba0aa628ae4e05a4","2024012227","ac2405bde2e8414d82da6b55d6244e37","ESRSBch6","pVh96Ahy","W5ni6FV2","63","2024012231","a1ef17df5a8047b4a8eafca385e419ef","ZjJsWttgFbs","07d13446b9594dedb150a5f85c7f4dbc","3f3118a27ddf4e7aaa2b05fd3988887e","2024012230","Z94ZuGIs","16d9523dcd054626a7af2a9b39828dba","2022111402","uI60j8yf","3s7uO4ZY","rSuqKmC0","IVQBWO9g","pfsfc001","FIEAbzGw","BpYSyPXN","bFq99Vyh","jrjzuLx0","QU8oPcxw","TVToJUnC","vpoJnqge","qANq3iJg","f2a02330b8ec4b31aa1a5e6ca5c2e973","V646rjQY","5760db97c0844a529fe1187aa0f7ad6e","Imh5eB6E","5fb50cb26a7a478ea6dc82034c76a634","WQYsehXx","EMzKtfDO","wVl3a3fX","8t2wMz6l","2023122005","7b3063b4397d47e7821d1e88b0a5aff6","aef8ea5b763246a8896d6b31ece97134","2023122003","2024012241","bc98b06e6de54dad819c1ca63d2c727e","7a287390a8844cf7813677126266640b","25e92b6c15a94abe9da29cfa59096e2d","T0cbTJ3C","5abba6ee166147ceb9f5091bdf49254e","af30e6bbfd65484faf1d94d89fc3e158","55d7a2556a274e19be0ad4ebff8ac9e8","bMoT82L3","KuV12Rvh","6e410e24540d49a68aa77fdea2824068","2023122007","6a73c8288e8d4e84ad62cc5689d0bb25","2023122008","2024012242","2023122004","ve3MSV81","Vzq8IG78","00dbd8e06e394fbea5b2bd3afe4d0c90","dbtM4DW6","fb9b4df1ca874acf9c5a45f5f84e7cdc","358cc43860df4739b2cfb9e7e0bbab75","5ab56b146b6c4869ae5583afcfe7724c","2023122002","whlHdHP0","mEa7333T","w04dl9aN","0yE4N0WU","p2of4Xnm","xf8l11DX","500f3bc576ad44babf90c7ff63e130fc","JJp96f4r","262fbff2f9194e49bcaaee0e659477ed","L3cjKb07","b703877d0a434beb84788f8a654c80cb","Ex89APtL","2024012215","810094b9c45648c09a056b018a4231e2","n34bATcl","2024012221","DdSwb0C4","d939a086d10449a89a0124e8a5118d78","pKc1n8F1","2024012216","2024012217","op66I2RA","cc623ea2c4f041dd99b49c20b80f79b5","45eca74fee154a44b0e4774bb9f9104f","7fe91f686a6044088e5d198710b66776","Dc2g25WY","EBKl7dz8","2024012219","ZtxaJ803","2024012220","pb4Pr2Df","NOrYt0hU","LZUgndRj","caf77166ca3243b78b5d7b9541651b67","3a664353bc6f4250bff1c6a284bc5ca1","93b845d2a52649c58da1da71c22c4201","G8vps5QZ","461f640dc4c14e958da1471afa78e54b","4438ee821b224ac788801b8399cf2e88","NFn2Qr3R","ed1e267d6f7d43aa8ad375bf7f47670e","YyjM8U56","F413xtpX","d2b7a0bb31ef45a4ac343feff0f31c85","2023011914","BA6Fv3a1","dk69GVLW","q2EaHTvY","JrGxzOPP","H57PSSdc","HnJm01FC","7c1909b909994f88a0c2dcccda53ab2b","11d06a3a2d2e4f68a7d686e64e1abbc8","Dg03b4UP","K395ayNT","ecd6caa29bc246ff921b79a9ebe11745","q81kfFTE","BG6e4m0E","VW1pat28","q7aZ5v8I","b5cc88b7ee6a41e6a586618505ce03e5","NoC85gis","rrLGJ051","d755b20fd9ea466d87f00f1f95b0cd1d","I3uLx63O","W8Rq08je","vd4hbhQD","TEtNq71a","rQBvcj6S","65ebc435fa874d00a014fdaa16c5ebee","Obyt2F2S","da330bda1e344ed7ab0bc774ec74b808","2023011905","097315c4cd354faa98d67e4a39fd55e7","qqXV306W","1b979c80cf2746c39894b99d9b5b4375","2024012237","I599tEdm","d0JbMxCg","rIs0HFHx","LsGsFdc2","GxLfFdc","cp123456","iyOD1K72","160d292949374bc5b648755132caf01a","LyGxJkFdc","bXpK4o8q","Mgj866SG","e18969f36fae4336b324b7756843907a","Zd75oLQC","GxGpZxFbs","8e4c3eede2c04f28883fd6039daa3d57","S2DCJ3m4","C7nNWY6d","Jw5X9auq","6aec64ffe20040aeab5e8b508a56007d","AAtpSqB0","2024012225","cm75KUI4","jWsq089U","a3ec781a647841e4a74c1eb694d02fda","8b6fd495c1364d54973e61ca189f9052","fEYZxZTl","xXnBS7vA","3iTjfDU3","uqwJNJIV","308L6SAj","o4XtBFct","7QyPpDnh","SGqazWSD","6edc5271102f400da992e1235198b8e8","e18a4d749e444c9ba3bd44c94e46457c","A7b7exXR","b0ee6f0a35774434857f30f80ff16bda","YnZzsFdc","F59IelNY","a71bc56acd2144588803f0a5bc8a2dcb","7be74e1159b04d44a6e65ca7e666f3ae","G18aPDsG","c31c516728984c4d8d07d41498fdc584","ce727295afdd43c78fe82b4a273e4a46","MczwML65","zY2KiTlF","O4bgnFaN","vrmtGXTv","nXazJf51","nu3IMw1O","bbX1Zybv","LskQS12E","71414a3545ec4ed6b6d16ede6ef09286","L0Y52zgd","GzZtFdc","GZcpfdc","dpT5JWFh","46b96821dfba438982ddb20340ce15eb","5ea9dba31e334e68b7d36cff5f741633","3c5503950e1d499895862d5b7b9585e5","2a8da77bcb524eb88898ee2be8c6dce0","88eafa84b3594817a026c3caa7c76b17","229248504dc24382bcacfae8c40c2833","9ad9288c9d384633a0c0fa9994c00dac","2024012233","hSpqswa2","QycFdC1qw","SzpFDCq1s","52c810616c9547d4ad7684e11821d48f","2129d59985cc491caca30cbbb6cb0ff8","DSiuM7bw","UszjAXKl","Wkl123FDC","2023121412","2023121411"]}


    questions = read_questions(question_file)
    qa_data = []

    for question in questions:
        payload = create_request_body(question, custom_data)
        response = get_answer(payload)

        think_text = ""
        answer_text = ""

        if response and "error" in response[0]:
            think_text = response[0]["error"]
            answer_text = response[0]["error"]
        else:
            for data in response:
                if "thinkText" in data:
                    think_text += data["thinkText"].strip() + " "
                if "answerText" in data:
                    answer_text += data["answerText"].strip()

            # 去除多余的空格
            think_text = think_text.strip()
            answer_text = answer_text.strip()

        # 添加到数据列表
        qa_data.append([question, think_text, answer_text])

        # 打印到控制台（以 Markdown 格式）
        print(f"### 问题\n{question}\n")
        print(f"### 思考过程\n{think_text if think_text else 'No thinking process'}\n")
        print(f"### 回答结果\n{answer_text if answer_text else 'No answer from API'}\n")

    # 生成唯一的文件名
    output_excel = generate_unique_filename(base_output_excel, "xlsx")

    # 保存到 Excel
    df = pd.DataFrame(qa_data, columns=["问题", "思考过程", "回答结果"])
    df.to_excel(output_excel, index=False)
    print(f"问答结果已保存到 {output_excel}")

if __name__ == "__main__":
    main()