import AskRequests
import concurrent.futures
import atexit
import signal
import pandas as pd
import getExcelData
import AskRequests
# 全部跑完之后，最后在进行写入excel
# localhost = r'http://10.81.81.82:8800'
localhost = r'http://10.170.249.86:8800'


class AskThreadNew():
    def __init__(self):
        #读取表中数据
        obj = getExcelData.QuestionClass()
        self.QA = obj.questionMethod()
        print(self.QA,"111")
        #[{'docId': nan, 'mainVenifyContent': nan, 'question': '甘肃龙源5月6日限出力是多少\n\n', 'answer': nan, 'LLMresult': '', 'paragraph1': '', 'paragraph2': '', 'paragraph3': '', 'paragraph4': '', 'paragraph5': ''}] 111

        # 初始化
        #写表
        self.AskQuestion = AskRequests.AskRequsets(localhost=localhost)
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        print("创建线程池")

    def getResult(self):
        for m in range(0, len(self.QA)):
            batch = self.QA[m]
            # 创建线程池
            # assistantId = 873
            futures = [self.thread_pool.submit(self.AskQuestion.make_request, question=batch['question'],
                                               answer=batch['answer'], assistantId=1113, spaceId=[],
                                               docId=batch['docId'], mainVenifyContent=batch['mainVenifyContent'])]
            try:
                results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=None)]
                print(results,"33333")

            except concurrent.futures.TimeoutError:
                print("Timeout error occurred, stopping program...")
                self.endThread()
            except Exception as e:
                print(f"An exception occurred: {e}")
                # self.endThread()
            finally:
                # 关闭线程池
                # thread_pool.shutdown(wait=True)
                if m == len(self.QA) - 1:
                    self.endThread()

    def endThread(self):
        self.thread_pool.shutdown(wait=True)
        print("关闭线程池")
        # 将内容写入excel，将图片写入excel
        self.AskQuestion.create_excel()
        # self.AskQuestion.writeAnswerImage()


askRequest = AskThreadNew()
askRequest.getResult()


class AskRequsets:
    def getResult(self):
        pass