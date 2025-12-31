import concurrent.futures
import threading
import LLManswerSingle
import atexit
import signal
import pandas
import time
import urllib3
import pymysql
import pandas as pd

# 关闭所有 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SQL():
    def select_sql(self):
        df = pandas.read_excel(r'D:/ZSY/1128/basic/HYDJ/summary.xlsx')
        data = df.to_dict(orient='records')
        print(data)

        db_config = {
            'host': '11.54.88.199',  # 数据库服务器的IP地址
            'port': 23306,  # 数据库端口号
            'user': 'kllm_expert_news',  # 数据库用户名
            'password': 'Cnpc%2024!@#',  # 数据库密码
            'database': 'kllm_expert_news',  # 要连接的数据库名称
            'charset': 'utf8mb4',  # 字符集
            # 'cursorclass': pymysql.cursors.DictCursor  # 返回结果作为字典
        }

        # 连接到数据库
        connection = pymysql.connect(**db_config)

        try:
            with connection.cursor() as cursor:
                # 编写你的查询语句
                for i in range(100):
                    sql = f"insert into kllm_hot_news (id,type,title,link,publish_time,content,summary,source_url,source_name,news_id,create_time,modified_time) " \
                          f"values (" \
                          f"'{data[i]['bussinessId']}'," \
                          f"'测试'," \
                          f"'{data[i]['question']}'," \
                          f"'http://mp.weixin.qq.com/s?src=11&timestamp=1510219229&ver=504&signature=-yp1IJU1bAQc-bJYheLr5ERwAm0UhCSJJ1ewx--8bVt3h2e1I37n4WGXnMUXWY4z-MthbZwxra3J1cigFuyLSOCKEf*opYIWxP5PU2oI1Tkj6LSo*Nlg9rDUoYwk-lzS&new=1'," \
                          f"NULL," \
                          f"'{data[i]['question']}'," \
                          f"NULL," \
                          f"'http://mp.weixin.qq.com/s?src=11&timestamp=1510219229&ver=504&signature=-yp1IJU1bAQc-bJYheLr5ERwAm0UhCSJJ1ewx--8bVt3h2e1I37n4WGXnMUXWY4z-MthbZwxra3J1cigFuyLSOCKEf*opYIWxP5PU2oI1Tkj6LSo*Nlg9rDUoYwk-lzS&new=1'," \
                          f"'测试'," \
                          f"NULL," \
                          f"'2024-11-19 10:20:20'," \
                          f"'2024-11-19 10:20:20')"  # 替换为你的实际查询语句
                    # print(sql)
                    # 执行查询
                    print(sql)
                    cursor.execute(sql)
                    connection.commit()

                # 获取查询结果
                result = cursor.fetchall()

                # 打印查询结果
                # result = (result[0][0]).replace("'",'"')
                # result = json.loads(result)
                # print(result['question'])
                result = result[0][0] if result else ""
                print(result)
        finally:
            # 关闭数据库连接
            connection.close()
        return result

if __name__ == '__main__':
    a = SQL().select_sql()