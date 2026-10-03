import os

import pytest

# from webrun.parse.CaseParser import case_parser
# from webrun.core.globalContext import g_context
from webtest.tool.webrun.parse.CaseParser import case_parser
from webtest.tool.webrun.core.globalContext import g_context

class CasesPlugin:
    """
    pytest插件 - 用于pytest运行时的用例配置信息加载
    应用了 pytest 钩子函数 (方法名不能改动)
    """

    def pytest_addoption(self, parser):

        """
        增加pytest运行的配置项
        """
        parser.addoption(
            "--type", action="store", default="yaml", help="测试用例类型"
        )
        parser.addoption(
            "--cases", action="store", default="../examples", help="测试用例目录"
        )
        # 添加一个指定的关键字目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        KEY_WORDS_DIR = os.path.join(current_dir, "../../../keyswords")
        parser.addoption(
            # "--keyDir",action="store", default="/Users/hcflask/hcweb/webtest/keyswords",help="拓展关键字目录"
            "--keyDir", action="store", default=KEY_WORDS_DIR, help="拓展关键字目录"

        )

    def pytest_generate_tests(self, metafunc):
        """
        method_meta: 运行的方法信息 ：测试用例执行之前执行（对测试数据进行处理）
        """

        # 读取用户传过来的参数
        case_type = metafunc.config.getoption("type")
        cases_dir = metafunc.config.getoption("cases")
        key_dir = metafunc.config.getoption("keyDir")

        # 把这个key_dir 放入到公共变量去
        g_context().set_dict("key_dir",key_dir)

        # 重点：读取测试用例,同时需要进行参数化
        data = case_parser(case_type, cases_dir)
        # case_type：yaml    cases_dir：F:\ProjectHcEdu\platform\web-engine\examples

        # 把测试用例作为参数化，交给 runner 执行 :  caseinfo 拿到了处理后的数据
        if "caseinfo" in metafunc.fixturenames:
            metafunc.parametrize("caseinfo", data['case_infos'], ids = data['case_names'])

    def pytest_collection_modifyitems(self,items):
        """
        用例收集完毕之后被调用，可以用来调整测试用例执行顺序；
        """
        for item in items:
            item.name = item.name.encode("utf-8").decode("unicode_escape")
            item._nodeid = item.callspec.id