import json
import requests
from webtest.tool.webrun.core.globalContext import g_context
from webtest.tool.webrun.utils.VarRender import refresh

class assert_eql_variable:

    def __init__(self, driver):
        self.driver = driver

    def assert_eql_variable(self, **kwargs):
        # 断言处理 - 相等
        # 预期值
        target = kwargs["数据内容"]
        # 获取全局变量
        all_context = g_context().show_dict()
        # print("当前的全部变量为",all_context)
        # 提取的环境变量
        current = kwargs["目标对象"]
        # print("要提取的值是",current)
        current = str(g_context().get_dict(current))
        # all_context = g_context().show_dict()
        current = refresh(current,all_context)
        target = refresh(target,all_context)

        # print("实际提取的值是:",current)
        print("预期值：",target)
        print(type(target))
        print("效验值:",current)
        print(type(current))
        # 断言
        assert target == current
