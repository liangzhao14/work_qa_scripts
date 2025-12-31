import concurrent.futures
import threading
import LLMzy
import atexit
import signal
import pandas
import time
import urllib3

# 关闭所有 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

max_workers = 5
start_time = int(time.time() * 1000)
localhost = "https://test-expert.ai.cnpc"
df = pandas.read_excel(r'D:/ZSY/1128/basic/HYDJ/expert.xlsx')
file_path = fr'D:/ZSY/1128/output/HYDJ/chat_{max_workers}路_{start_time}.xlsx'
col_dict = df.to_dict(orient='records')
# questions = ["天空为什么是蓝色的"] * 1000
for m in range(0,len(col_dict),20):
    batch = col_dict[m:m+20]
    # 创建线程池
    print("创建线程池")
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    AskLLM = LLMzy.AskLLM(localhost=localhost,file_path=file_path)
    futures = [thread_pool.submit(AskLLM.ask_zy, question=batch[i]['question'],answer=batch[i]['answer'],assistantId=batch[i]['assistant']) for i in range(len(batch))]
    try:
        results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=None)]


    except concurrent.futures.TimeoutError:
        print("Timeout error occurred, stopping program...")
    except Exception as e:
        print(f"An exception occurred: {e}")
    finally:
        # 关闭线程池
        thread_pool.shutdown(wait=True)
        print("关闭线程池")
        AskLLM.create_excel()