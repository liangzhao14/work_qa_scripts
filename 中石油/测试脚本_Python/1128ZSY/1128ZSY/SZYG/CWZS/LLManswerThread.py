import concurrent.futures
import threading
import LLManswerSingle
import atexit
import signal
import pandas
import time

max_workers = 10
start_time = int(time.time() * 1000)
localhost = "https://test-assistant.ai.cnpc"
file_path = fr'D:/ZSY/1128/output/SZYG/CWZS/chat_{max_workers}路_{start_time}.xlsx'
df = pandas.read_excel(r'D:/ZSY/1128/basic/SZYG/CWZS/questions.xlsx')
questions = df.iloc[:,0].tolist()
# questions = ["天空为什么是蓝色的"] * 1000
for m in range(0,len(questions),20):
    batch = questions[m:m+20]
    # 创建线程池
    print("创建线程池")
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    AskLLM = LLManswerSingle.AskLLM(localhost=localhost,file_path=file_path)
    futures = [thread_pool.submit(AskLLM.ask_llm, question=batch[i], assistantId=1, conversationId="") for i in range(len(batch))]
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