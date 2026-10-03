class upload_xiti:
    """处理上传习题文件到燎原stage环境的流程"""
    def __init__(self, driver=None):
        self.driver = driver
        # 固定核心URL（与upload_liaoyuan保持一致）
        self.url_oss_token = 'https://7to12-stage.yangcong345.com/backend/yc-oss/token?bucket=yc-course&expires=1800'
        self.url_oss_upload = 'https://onion-oss-stage.yangcong345.com/token/upload'
        self.url_login = 'https://liaoyuan-stage-api.yangcongxueyuan.com/user/login'
        self.url_create_task = 'https://liaoyuan-stage-api.yangcongxueyuan.com/task/bulkCreateRootTasks'
    def upload_xiti(self, **kwargs):
        # 1. 获取必需参数（与upload_liaoyuan一致的直接取值方式）
        stage_value = kwargs['学段']
        subject_value = kwargs['学科']
        filename_key = kwargs['文件名']

        # 2. 本地文件处理（参考upload_liaoyuan的简洁路径和命名逻辑）
        # 固定默认路径为../tool/（与upload_liaoyuan一致，更适配平台环境）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(current_dir, '../tool/')  # 直接拼接路径
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
        file_base_name = kwargs.get('file_base_name', "pdc自动化测试")  # 保留可配置基础名

        try:
            # 查找目标文件（支持docx和pdf，与原功能一致）
            all_files = os.listdir(upload_dir)
            target_files = [f for f in all_files if f.lower().endswith(('.docx', '.pdf'))]
            match_file = difflib.get_close_matches(file_base_name, target_files, 1, cutoff=0.1)[0]

            # 重命名文件（加时间戳，保留原扩展名）
            original_ext = os.path.splitext(match_file)[1]  # 获取实际扩展名
            new_file_name = f"{file_base_name}{timestamp}{original_ext}"
            old_path = os.path.join(upload_dir, match_file)
            new_path = os.path.join(upload_dir, new_file_name)
            os.rename(old_path, new_path)

            # 记录文件名（参考upload_liaoyuan的文本文件记录方式）
            with open(os.path.join(upload_dir, 'ly_name.txt'), 'w') as f:
                f.write(f"{file_base_name}{timestamp}")  # 存无扩展名的名称
            g_context().set_dict(filename_key, f"{file_base_name}{timestamp}")
            print(f"处理后文件名：{new_file_name}")

        except Exception as e:
            print(f"文件处理失败：{e}")
            return False
        # 3. 读取记录的文件名（与upload_liaoyuan逻辑对齐）
        with open(os.path.join(upload_dir, 'ly_name.txt'), 'r') as f:
            name_data = f.read()  # 无扩展名的文件名
        file_path = os.path.join(upload_dir, f"{name_data}{original_ext}")  # 完整文件路径
        # 4. 获取OSS上传令牌（简化响应处理，直接解析）
        try:
            res_token = requests.post(self.url_oss_token, verify=False)
            token = json.loads(res_token.text)['data']['token']
            print("OSS令牌获取成功")
        except Exception as e:
            print(f"OSS令牌获取失败：{e}，响应：{res_token.text if 'res_token' in locals() else ''}")
            return False
        # 5. 上传文件到OSS（直接读取文件并上传）
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                headers = {'authorization': token}
                res_upload = requests.post(self.url_oss_upload, headers=headers, files=files, verify=False)
                upload_data = json.loads(res_upload.text)['data']
                oss_domain = upload_data['domain']
                oss_key = upload_data['key']
                print(f"文件上传到OSS成功，路径：{oss_domain}/{oss_key}")
        except Exception as e:
            print(f"OSS文件上传失败：{e}，响应：{res_upload.text if 'res_upload' in locals() else ''}")
            return False
        # 6. 登录燎原系统（固定账号，直接获取token）
        try:
            login_data = {"phone": "88888888888", "role": "onion", "password": "123456a"}
            res_login = requests.post(self.url_login, data=login_data, verify=False)
            login_token = json.loads(res_login.text)['token']
            print("燎原登录成功")
        except Exception as e:
            print(f"燎原登录失败：{e}，响应：{res_login.text if 'res_login' in locals() else ''}")
            return False
        # 7. 创建任务（参数保持原功能，结构更紧凑）
        try:
            # 构造任务参数（保留原支持的可选参数，默认值不变）
            task_data = {
                "rootTasks": [{"filename": name_data, "filepath": f"{oss_domain}/{oss_key}"}],
                "stage_subject": f"{stage_value}-{subject_value}",
                "inspectorGroup": kwargs.get('inspectorGroup', 'UI_TEST'),
                "platform": kwargs.get('platform', 'cb'),
                "year": kwargs.get('year', '2025'),
                "scene": kwargs.get('scene', 'refineProblem'),
                "provinceCodes": kwargs.get('provinceCodes', ['000000']),
                "cityCodes": kwargs.get('cityCodes', []),
                "testPointTagId": kwargs.get('testPointTagId', ''),
                "sourceTag": kwargs.get('sourceTag', '11'),
                "goalId": kwargs.get('goalId', '962cadc2-53f4-11e7-85f5-277d4956742e'),
                "needReview": kwargs.get('needReview', False)
            }
            headers = {'authorization': f'Bearer {login_token}'}
            res_task = requests.post(self.url_create_task, json=task_data, headers=headers, verify=False)
            task_result = json.loads(res_task.text)
            print(f"任务创建响应：{task_result}")
            return task_result.get('success', False)
        except Exception as e:
            print(f"任务创建失败：{e}，响应：{res_task.text if 'res_task' in locals() else ''}")
            return False
# 示例用法
# if __name__ == '__main__':
#     uploader = upload_xiti()
#     success = uploader.upload_xiti(学段='2', 学科='1', 文件名='test_key')
#     print(f"上传结果：{'成功' if success else '失败'}")
import base64
import json
import os
import requests
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.support.wait import WebDriverWait
import time
