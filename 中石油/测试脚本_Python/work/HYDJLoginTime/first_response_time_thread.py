import os

import pandas as pd
import threading
import time
from LLManswerSingle import AskLLM

# 全局变量，用于记录每个线程的第一次响应时间
first_response_times = {}

def process_question(account, question):
    username = account['username']
    password = account['password']
    localhost = "https://dev-expert.ai.cnpc"
    file_path = 'D:/new_results.xlsx'

    try:
        ask_llm = AskLLM(localhost, file_path)
        ask_llm.login(username, password)
        start_time = time.time() * 1000
        conversationId = ask_llm.ask_llm(question, "", 3)
        elapsed_time = time.time() * 1000 - start_time

        # 获取并记录第一次响应时间
        first_response_time = first_response_times[threading.get_ident()] if threading.get_ident() in first_response_times else "N/A"

        # 将结果写入到新表格中
        df = pd.DataFrame({'username': [username], 'question': [question], 'elapsed_time': [elapsed_time], 'first_response_time': [first_response_time]})
        if os.path.exists(file_path):
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, sheet_name='Sheet1', header=False, index=False)
        else:
            df.to_excel(file_path, engine='openpyxl', index=False)
    except Exception as e:
        print(f"账号 {username} 提问 {question} 失败：{e}")

def ask_llm_wrapper(account, question):
    global first_response_times
    thread_id = threading.get_ident()
    start_time = time.time() * 1000
    try:
        ask_llm = AskLLM("https://dev-expert.ai.cnpc", "")
        ask_llm.login(account['username'], account['password'])
        conversationId = ask_llm.ask_llm(question, "", 3)
        elapsed_time = time.time() * 1000 - start_time
        first_response_times[thread_id] = ask_llm.ask_llm.first_response_time
    except Exception as e:
        print(f"账号 {account['username']} 提问 {question} 失败：{e}")

if __name__ == '__main__':
    # 读取包含账号信息的Excel表格
    accounts_df = pd.read_excel('D:/accounts.xlsx')
    accounts = accounts_df.to_dict('records')

    questions = ["JAVA工程师的工作职责", "它是软件开发工程师吗？"]

    # 创建线程列表
    threads = []
    for account in accounts:
        for question in questions:
            thread = threading.Thread(target=ask_llm_wrapper, args=(account, question))
            threads.append(thread)
            thread.start()

    # 等待所有线程完成第一次响应时间的获取
    for thread in threads:
        thread.join()

    # 再次创建线程列表，用于处理问题并写入结果
    process_threads = []
    for account in accounts:
        for question in questions:
            process_thread = threading.Thread(target=process_question, args=(account, question))
            process_threads.append(process_thread)
            process_thread.start()

    # 等待所有线程完成结果写入
    for process_thread in process_threads:
        process_thread.join()
