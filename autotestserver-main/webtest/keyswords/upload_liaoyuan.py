import difflib
import json
import os
import time
from webtest.tool.webrun.core.globalContext import g_context


import requests


class upload_liaoyuan:
    def __init__(self, driver):
        self.driver = driver

    def upload_liaoyuan(self,**kwargs):
        stage_value = kwargs['学段']
        subject_value = kwargs['学科']
        filename_value = kwargs['文件名']
        # 修改上传文件并记录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_value = '../tool/'
        filepath_value = os.path.join(current_dir, path_value)
        value = time.strftime('%Y-%m-%d-%H-%M-%S')
        file_name = os.listdir(filepath_value)
        pdf = difflib.get_close_matches('pdc自动化测试', file_name, 1, cutoff=0.1)[0]
        os.rename(filepath_value + pdf, filepath_value + "pdc自动化测试" + value + ".pdf")
        with open(filepath_value + "ly_name.txt", "w") as f:
            f.write("pdc自动化测试" + value)
        time.sleep(2)
        filely_name = "pdc自动化测试" + value
        g_context().set_dict(filename_value, filely_name)
        print("********上传的文件名：",filely_name)
        # 读取name
        with open(filepath_value + "ly_name.txt", "r") as f:
            name_data = f.read()

        # 获取上传文件所需要的token
        url_get_token = 'https://7to12-stage.yangcong345.com/backend/yc-oss/token?bucket=yc-course&expires=1800'
        response = requests.post(url_get_token, verify=False)
        response_data = response.content.decode('utf-8')
        response_dict = json.loads(response_data)
        token = response_dict['data']['token']

        # 调用uplpad
        uplpad_url = 'https://onion-oss-stage.yangcong345.com/token/upload'
        file_path = filepath_value + '{}.pdf'.format(name_data)
        f = open(file_path, 'rb')
        file = {'file': f}
        headers = {'authorization': '{}'.format(token)}
        response = requests.post(uplpad_url, headers=headers, files=file, verify=False)
        response_data = response.content.decode('utf-8')
        response_dict = json.loads(response_data)
        response_url = response_dict['data']['key']
        response_name = response_dict['data']['domain']
        f.close()

        # 上传表单
        # 获取燎原登录token
        login_url = 'https://liaoyuan-stage-api.yangcongxueyuan.com/user/login'
        login_data = {"phone": "88888888888", "role": "onion", "password": "123456a"}
        login_response = requests.post(login_url, login_data, verify=False)
        login_response_data = login_response.content.decode('utf-8')
        login_response_dict = json.loads(login_response_data)
        login_token = login_response_dict['token']

        # 上传表单
        creat_url = 'https://liaoyuan-stage-api.yangcongxueyuan.com/task/bulkCreateRootTasks'
        headers = {'authorization': 'Bearer ' + '{}'.format(login_token)}
        data = {"rootTasks": [
            {"filename": "{}".format(name_data), "filepath": "{}/{}".format(response_name, response_url)}],
            "stage_subject": "{}-{}".format(stage_value,subject_value), "inspectorGroup": "UI_TEST",
            "scene": "text", "testPaperType": "shiYingXingKaoShi",
            "paperTag": ["regular"], "grade": 1, "term": "last", "year": "2020"}
        requests.post(url=creat_url, headers=headers, json=data, verify=False)
        response.close()

