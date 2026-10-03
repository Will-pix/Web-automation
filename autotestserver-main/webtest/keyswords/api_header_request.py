import json
import requests
from webtest.tool.webrun.core.globalContext import g_context
import subprocess
import shlex
from webtest.tool.webrun.utils.VarRender import refresh

class api_header_request:

    def __init__(self, driver):
        self.driver = driver

    def api_header_request(self, **kwargs):
        all_context = g_context().show_dict()

        # 获取参数
        var_name = kwargs["var_name"]
        curl_cmd = kwargs["curl_cmd"]
        header_name = kwargs.get("header_name")  # 要提取的响应头名称
        
        # 处理curl命令，确保包含响应头
        # curl_cmd = curl_cmd.replace('\\', '\\\n')
        # print("原始curl命令:", curl_cmd)
        curl_cmd = curl_cmd.replace('\\', '').replace('\n', ' ').strip()
        # 压缩多个空格为一个
        curl_cmd = ' '.join(curl_cmd.split())
        print("处理后的curl命令:", curl_cmd)
        
        # 自动添加-i参数以获取响应头
        if ' -i ' not in curl_cmd and not curl_cmd.endswith(' -i') and not curl_cmd.startswith('curl -i'):
            curl_cmd = curl_cmd.replace('curl', 'curl -i', 1)
        
        curl_cmd = refresh(curl_cmd, all_context)
        print("处理后的curl命令:", curl_cmd)

        # 执行curl命令
        result = subprocess.run(
            curl_cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 解析响应头
        headers = self._parse_headers(result.stdout)
        
        # 存储结果
        if header_name:
            # 提取指定响应头（不区分大小写）
            value = headers.get(header_name.lower())
            g_context().set_dict(var_name, value)
            print(f"响应头 '{header_name}' 的值 '{value}' 已存入变量 '{var_name}'")
        else:
            # 存储所有响应头
            g_context().set_dict(var_name, headers)
            print(f"所有响应头已存入变量 '{var_name}'")

        print("当前全局变量:", g_context().show_dict())

    def _parse_headers(self, response):
        """简单解析响应头"""
        headers = {}
        # 分割响应头和响应体（空行为界）
        sections = response.split('\n\n', 1)
        if not sections:
            return headers
            
        # 处理响应头部分
        for line in sections[0].split('\n'):
            line = line.strip()
            if ': ' in line and not line.startswith('HTTP/'):
                key, value = line.split(': ', 1)
                headers[key.lower()] = value
        
        return headers
    