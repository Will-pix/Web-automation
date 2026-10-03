import json
import requests
from webtest.tool.webrun.core.globalContext import g_context
import subprocess
import shlex
from webtest.tool.webrun.utils.VarRender import refresh

class api_request:

    def __init__(self, driver):
        self.driver = driver

    def api_request(self, **kwargs):
        all_context = g_context().show_dict()

        # 要使用变量
        var_name = kwargs["var_name"]
        curl_cmd = kwargs["curl_cmd"]
        path = kwargs.get("path")  # 新增参数：指定要提取的路径

        # curl_cmd = curl_cmd.replace('\\', '\\\n')
        # print("curl_cmd的值:",curl_cmd)
        curl_cmd = curl_cmd.replace('\\', '').replace('\n', ' ').strip()
        # 压缩多个空格为一个
        curl_cmd = ' '.join(curl_cmd.split())
        print("处理后的curl命令:", curl_cmd)

        curl_cmd = refresh(curl_cmd,all_context)
        # 执行 Curl 命令
        result = subprocess.run(
            curl_cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        response_data = json.loads(result.stdout)
        print("接口返回的完整数据:", response_data)  # 新增这行
        if path:
            extracted_value = self._extract_value_by_path(response_data, path)
            g_context().set_dict(var_name, extracted_value)
            print(f"从路径 '{path}' 提取的值存入变量 '{var_name}': {extracted_value}")
        else:
            # 如果没有指定路径，存储完整响应
            g_context().set_dict(var_name, response_data)
            print(f"完整响应存入变量 '{var_name}': {response_data}")


        # 存储结果到全局变量
        # g_context().set_dict(var_name,response_data)
        all_context = g_context().show_dict()
        print("当前的全部变量为",all_context)

    def _extract_value_by_path(self, data, path):
        """根据路径（如 'data.0.case_desc'）从嵌套数据中提取值"""
        parts = path.split('.')  # 分割路径，例如 'data.0.case_desc' → ['data', '0', 'case_desc']
        value = data

        for part in parts:
            try:
                if part.isdigit():
                    # 如果是数字，尝试作为列表索引
                    value = value[int(part)]
                else:
                    # 否则作为字典键
                    value = value[part]
            except (KeyError, IndexError, TypeError):
                print(f"路径 '{path}' 中的 '{part}' 不存在或类型不匹配")
                return None

        return value