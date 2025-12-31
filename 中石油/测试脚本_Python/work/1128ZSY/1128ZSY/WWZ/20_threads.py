import concurrent.futures
import threading
import single
import atexit
import signal
import pandas as pd
import time
from tqdm import tqdm, trange
import urllib3

# 关闭所有 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

max_workers = 20
localhost = "https://test-assistant.ai.cnpc"
rdf = pd.DataFrame(columns=["问题", 
                            "大模型答案", "召回url", 
                            "召回1", "召回2", "召回3", "召回4", "召回5"])

df = pd.read_excel('D:\\WWZ\\测试集.xlsx')
questions = list(df['问题'])

for m in trange(0,len(questions),20):
    batch = questions[m:m+20]
    # 创建线程池
    print("创建线程池")
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    AskLLM = single.Test(localhost=localhost)
    futures = [thread_pool.submit(AskLLM.get_recall, question=batch[i]) for i in range(len(batch))]
    try:
        results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=None)]
        for result_each in results:
            question_each, result, paragraphs, urls = result_each[0], result_each[1], result_each[2], result_each[3]
            new_row = {"问题": question_each,
                    "大模型答案": result, 
                    "召回url": str(urls),
                    "召回1": paragraphs[0], 
                    "召回2": paragraphs[1], 
                    "召回3": paragraphs[2], 
                    "召回4": paragraphs[3], 
                    "召回5": paragraphs[4]}
            rdf = pd.concat([rdf, pd.DataFrame([new_row])], ignore_index=True)
    except:
        print(m)
    # 关闭线程
    thread_pool.shutdown(wait=True)


rdf.to_excel("D:\\WWZ\\测试结果20路输出.xlsx", header=True, index=False)