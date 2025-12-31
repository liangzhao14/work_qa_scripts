import math
import os
import time
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError


class UploadFolder:
    def __init__(self,folder_path):
        self.token = '8f28340c12401c5667730a8fc706ccc6|WEB|6fce55c7395148b28a89fbe7247ef816'
        self.base_url = r'http://shenwanszgj.lingyangplat.com/iflytek'
        self.log = ""
        self.file_process = 0
        self.folder_path = folder_path
        self.total_file = self.count_files(self.folder_path)

    def create_dir(self,dir_name,space_id,parent_id,position):
        url = rf'{self.base_url}/digital-artisan-space/file/createDir'
        headers = {"Content-Type": "application/json", "Artisan-Token": self.token}
        body = {"name":dir_name,"spaceId":space_id,"type":0,"parentId":parent_id,"position":position}
        response = requests.post(url=url,headers=headers,json=body,timeout=600)
        time.sleep(1)
        dir_id = response.json().get('data')
        return dir_id

    def upload_file(self,file_name,space_id,file_path,parent_id,position):
        url1 = rf'{self.base_url}/digital-artisan-space/file/uploadNameCheck'
        headers1 = {"Content-Type": "application/json", "Artisan-Token": self.token}
        body1 = {"name":[file_name],"spaceId":space_id}
        response1 = requests.post(url=url1,headers=headers1,json=body1,timeout=600)
        time.sleep(1)
        file_list = response1.json().get('data')
        if file_name in file_list:
            print('文件已存在')
            self.log += f'"{file_path}" 文件已存在\n'
            return f'"{file_path}" 文件已存在'
        else:
            url2 = rf'{self.base_url}/digital-artisan-space/file/upload'
            headers2 = {'artisan-token': self.token}
            files = {'file': open(file_path, 'rb')}
            params = {
                'parentId': parent_id,
                'position': position,
                'spaceId': space_id,
                'splitType': 7
            }
            try:
                response2 = requests.post(url=url2, files=files, params=params, headers=headers2,timeout=600)
                time.sleep(1)
                # file_id = response2.json().get('data')
                print(f'上传成功\n\n')
            except Timeout:
                print('上传失败\n\n')
                self.log += f'"{file_path}" 文件上传失败 原因超时\n'
            except Exception as e:
                print('上传失败\n\n')
                self.log += f'"{file_path}" 文件上传失败 原因未知\n'


    def get_list_by_space_id(self,space_id):
        file_list = {}
        page = 1
        page_size = 100
        url = rf'{self.base_url}/digital-artisan-space/file/listBySpace'
        headers = {"Content-Type": "application/json", "Artisan-Token": self.token}
        body = {"spaceId":space_id,"name":"","pageIndex":page,"pageSize":page_size}
        response = requests.post(url=url,headers=headers,json=body,timeout=600)
        time.sleep(1)
        data = response.json().get('data')
        total = data.get('total')
        total_page = math.ceil(total / page_size)
        lists = data.get('list') or []
        for file in lists:
            file_list[f'{file.get("name")}'] = file.get('id')
        while page < total_page:
            page += 1
            body = {"spaceId": space_id, "name": "", "pageIndex": page, "pageSize": page_size}
            response = requests.post(url=url, headers=headers, json=body,timeout=600)
            time.sleep(1)
            lists = response.json().get('data').get('list')
            for file in lists:
                file_list[f'{file.get("name")}'] = file.get('id')
        return file_list

    def get_list_by_folder_id(self,folder_id):
        file_list = {}
        page = 1
        page_size = 100
        url = rf'{self.base_url}/digital-artisan-space/file/access'
        headers = {"Content-Type": "application/json", "Artisan-Token": self.token}
        body = {"fileId":folder_id,"name":"","pageIndex":page,"pageSize":page_size}
        response = requests.post(url=url,headers=headers,json=body,timeout=600)
        time.sleep(1)
        data = response.json().get('data')
        total = data.get('total')
        total_page = math.ceil(total / page_size)
        lists = data.get('list') or []
        for file in lists:
            file_list[f'{file.get("name")}'] = file.get('id')
        while page < total_page:
            page += 1
            body = {"fileId": folder_id, "name": "", "pageIndex": page, "pageSize": page_size}
            response = requests.post(url=url, headers=headers, json=body,timeout=600)
            time.sleep(1)
            lists = response.json().get('data').get('list')
            for file in lists:
                file_list[f'{file.get("name")}'] = file.get('id')
        return file_list

    def count_files(self,path):
        total_files = 0

        for root,_, files in os.walk(path):
            total_files += len(files)

        return total_files

    def check_file_upload(self, file_name, file_size):
        # 定义允许的后缀列表及其对应的大小限制（单位：字节）
        extension_limits = {
            'pdf': 200 * 1024 * 1024,  # 200 MB
            'doc': 50 * 1024 * 1024,  # 50 MB
            'docx': 50 * 1024 * 1024,  # 50 MB
            'md': 20 * 1024 * 1024,  # 20 MB
            'txt': 20 * 1024 * 1024,  # 20 MB
            'ppt': 80 * 1024 * 1024,  # 80 MB
            'pptx': 80 * 1024 * 1024,  # 80 MB
            'xls': 20 * 1024 * 1024,  # 20 MB
            'xlsx': 20 * 1024 * 1024,  # 20 MB
            'png': 20 * 1024 * 1024,  # 20 MB
            'jpg': 20 * 1024 * 1024,  # 20 MB
            'jpeg': 20 * 1024 * 1024,  # 20 MB
            'mp3': 1024 * 1024 * 1024,  # 1024 MB
            'mp4': 1024 * 1024 * 1024  # 1024 MB
        }

        # 处理文件名中的路径
        filename = file_name
        if '/' in file_name:
            filename = file_name.rsplit('/', 1)[-1]
        if '\\' in file_name:
            filename = file_name.rsplit('\\', 1)[-1]

        # 检查文件名是否包含扩展名
        if '.' not in filename:
            return False

        # 获取后缀并转换为小写
        file_ext = filename.rsplit('.', 1)[-1].lower()

        # 检查后缀是否在允许的列表中
        if file_ext not in extension_limits:
            return False
        else:
            if file_size <= extension_limits[file_ext]:
                return True
            else:
                return False


    def upload_folder(self,path,space_id,position='/0',parent_id=0,):
        entries = os.listdir(path)
        if parent_id == 0:
            file_list = self.get_list_by_space_id(space_id)
        else:
            file_list = self.get_list_by_folder_id(parent_id)
        for entry in entries:
            full_path = os.path.join(path, entry)

            if os.path.isdir(full_path):
                # 如果是文件夹
                # 判断文件夹是否存在 如果不存在则创建一个
                if entry in file_list:
                    dir_id = file_list.get(entry)
                else:
                    dir_id = self.create_dir(entry,space_id,parent_id,position)
                    print(f'文件夹：{entry}创建成功')
                new_position = position + f'/{dir_id}'
                self.upload_folder(full_path,space_id,new_position,dir_id)

            else:
                # 如果是文件
                # print(' ' * indent + f"{{文件: {entry}}}")
                file_size = os.path.getsize(full_path)
                self.file_process += 1
                print(f"开始上传：{entry} 大小：{(file_size/1024/1024):.2f}M 进度：{self.file_process}/{self.total_file}")
                if self.check_file_upload(entry,file_size):
                    self.upload_file(entry,space_id,full_path,parent_id,position)
                else:
                    print(f'上传失败\n\n')
                    self.log += f'文件：{full_path} 大小：{(file_size/1024/1024):.2f}M 文件格式或大小不支持，上传失败\n'


if __name__ == "__main__":
    a = UploadFolder(r'H:\本地知识库 - 副本\班组\运行四值')
    a.upload_folder(r'H:\本地知识库 - 副本\班组\运行四值',109)
    start_time = int(time.time() * 1000)
    with open(f'output_log_{start_time}.txt', 'w', encoding='utf-8') as file:
        file.write(a.log)
    # b = a.check_file_type('a.zip')
    # print(b)