import json
import requests
from webtest.tool.webrun.core.globalContext import g_context
import subprocess
import shlex
from webtest.tool.webrun.utils.VarRender import refresh

class api_request_no:

    def __init__(self, driver):
        self.driver = driver

    def api_request_no(self, **kwargs):
        all_context = g_context().show_dict()

        # 要使用变量
        curl_cmd = kwargs["curl_cmd"]
        # curl_cmd = curl_cmd.replace('\\', '\\\n')
        # print("curl_cmd的值:",curl_cmd)
        curl_cmd = curl_cmd.replace('\\', '').replace('\n', ' ').strip()
        # 压缩多个空格为一个
        curl_cmd = ' '.join(curl_cmd.split())
        print("处理后的curl命令:", curl_cmd)
        curl_cmd = refresh(curl_cmd,all_context)
        # 执行 Curl 命令
        subprocess.run(
            curl_cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )