import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
# from PIL import Image as PILImage
import io
# import xlrd
# import urllib.parse
class QuestionClass():
    def questionMethod(self):
        file_path = r'D:\Users\admin\Desktop\AskRequest\AskRequest\11.xlsx'
        try:
          df = pd.read_excel(file_path)
          # 检查是否有数据
          if not df.empty:
             array = []
             for content in df.values:
               #     array.extend(content)
                   dict = {'docId':content[0],
                           'mainVenifyContent':content[1],
                           'question':content[2],
                           'answer':content[3],
                           'LLMresult':"",
                           'paragraph1':"",
                           'paragraph2':"",
                           'paragraph3':"",
                           'paragraph4':"",
                           'paragraph5':"",
                           }
                   
                   array.append(dict)
               #     print(f'读取的内容是-----{content[0]}')
             #print(array)
             return array
          else:
             print("读取的数据为空")
        except FileNotFoundError:
             print("文件未找到，请检查路径是否正确")
        except Exception as e:
             print(f"读取Excel时发生错误：{e}")
        
         
obj =   QuestionClass()
obj.questionMethod() 
