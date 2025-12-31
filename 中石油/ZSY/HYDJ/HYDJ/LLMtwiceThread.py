import concurrent.futures
import threading
import LLMtwice
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
df = pandas.read_excel(r'D:/work/ZSY/1128/basic/HYDJ/twice.xlsx')
file_path = fr'D:/work/ZSY/1128/output/HYDJ/chat_{max_workers}路_{start_time}.xlsx'
questions = df.to_dict(orient='records')
# questions = ["天空为什么是蓝色的"] * 1000
for m in range(0,len(questions),20):
    batch = questions[m:m+20]
    # 创建线程池
    print("创建线程池")
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    AskLLM = LLMtwice.AskLLM(localhost=localhost,file_path=file_path)
    futures = [thread_pool.submit(AskLLM.ask_llm_twice, first_question=batch[i]['first_question'], second_question=batch[i]['second_question']) for i in range(len(batch))]
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