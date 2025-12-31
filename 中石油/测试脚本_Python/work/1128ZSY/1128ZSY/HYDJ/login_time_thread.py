import os
import pandas as pd
import threading
import time
from LLManswerSingle import AskLLM

# 记录程序启动时间（毫秒）
program_start_time = int(time.time() * 1000)
# 登录时间
login_time=[]
# 登录用户
login_name=[]
def login_and_record(account):
    username = account['username']
    password = account['password']
    localhost = "https://test-expert.ai.cnpc"
    file_path = r'D:\work\ZSY\1128\output\HYDJ\login_time_results.xlsx'

    try:
        ask_llm = AskLLM(localhost, file_path)
        # 记录登录开始时间（毫秒）
        login_start_time = int(time.time() * 1000)
        ask_llm.login(username, password)
        # 记录登录成功时间（毫秒）
        login_success_time = int(time.time() * 1000)
        elapsed_time = login_success_time - login_start_time

        # 将结果写入到另一个表格中
        df = pd.DataFrame({'username': [username], 'elapsed_time': [elapsed_time]})
        print(elapsed_time)
        login_time.append(elapsed_time)
        login_name.append(username)
        if os.path.exists(file_path):
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, sheet_name='Sheet1', header=False, index=False)
        else:
            df.to_excel(file_path, engine='openpyxl', index=False)
    except Exception as e:
        print(f"账号 {username} 登录失败：{e}")

if __name__ == "__main__":
    # 读取包含账号信息的Excel表格
    accounts_df = pd.read_excel(r'D:\work\ZSY\1128\basic\HYDJ/accounts.xlsx')
    accounts = accounts_df.to_dict('records')
    # print(accounts)

    # 创建线程列表
    threads = []
    for account in accounts:
        # print(account)
        thread = threading.Thread(target=login_and_record, args=(account,))
        threads.append(thread)
        thread.start()


    # 等待所有线程完成
    for thread in threads:
        thread.join()

    data_result = {}
    data_result = zip(login_name, login_time)
    df = pd.DataFrame(data_result, columns=['username', 'elapsed_time(ms)'])
    output_file = r"D:\work\ZSY\1128\output\HYDJ\login_time_results.xlsx"
    df.to_excel(output_file, index=False)