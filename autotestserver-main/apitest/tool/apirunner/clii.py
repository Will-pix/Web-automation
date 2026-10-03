# -*- coding: utf-8 -*-
import os
import sys
import pytest

from apitest.tool.apirunner.core.CasesPlugin import CasesPlugin

def run():
    print("进入到pytest run")
    # 获取 python运行参数
    # 1. 读取命令行传入的参数-这里的实际存储为：['--cases=../examples', '-sv', '--capture=tee-sys'，'TestRunner完整路径']
    #sys.argv 是 Python 标准库 sys 模块中的一个列表，它用于获取命令行传递给 Python 脚本的所有参数
    #startswith是检查字符串是否已-开头，如果是就加入
    pytest_cmd_config = []
    for arg in sys.argv:
        if arg.startswith("-"):
            pytest_cmd_config.append(arg)
    #所以这句话的真是目的是打印出TestRunner在哪里，
    # 只是实现方式是先把cli的目录找出来，
    # 因为他知道这个cli目录与加的字符串core，是一个层级
    # os.path.join()是拼接路径，os.path.dirname(__file__)是当前路径的父路径
    # print(os.path.join(os.path.dirname(__file__), "core/TestRunner.py"))
    # 2. 构建pytest参数
    #这句话，是实际将TestRunner的文件路径存到了pytest_args的列表里
    pytest_args = [os.path.join(os.path.dirname(__file__), "core/TestRunner.py")]
    #这句话是将上面的文件信息和参数也都放里
    pytest_args.extend(pytest_cmd_config)

    # print("pytest run执行参数：", pytest_args)
    #plugins参数是一个列表，放入需要执行的插件
    pytest.main(pytest_args, plugins=[CasesPlugin()])
    #pytest 拥有一套完整的生命周期，在不同的阶段会触发不同的钩子函数。当你通过 pytest.main 启动 pytest 时，pytest 会查找并加载所有已注册的插件，一旦到了特定的阶段，就会自动调用插件里对应的钩子函数。
    # 1.会先进行插件的钩子CasesPlugin内的pytest_addoption，添加参数及参数值，并且这个阶段就结束了
    # 2.下个阶段，. 测试用例收集，参数化处理等等的准备工作全部执行完毕，会继续调用CasesPlugin内的pytest_generate_tests，
    # 3. 第三个阶段pytest_collection_modifyitems钩子，第三个钩子函数-主要处理 pytest 收集到的测试用例进行修改和调整
    # 4.pytest 会自动找到 TestRunner 类下的 test_case_execute 方法并将其作为测试用例执行，这主要得益于 pytest 的测试发现机制以及 CasesPlugin 插件的参数化处理


if __name__ == '__main__':
    run()
    # 测试执行入口
    # print(os.path.join(os.path.dirname(__file__),'core', "TestRunner.py"))
    # pytest_args = ["-s", "-v", "--capture=sys",
    #                os.path.join(os.path.dirname(__file__),'core', "TestRunner.py"),
    #                "--clean-alluredir",
    #                "--alluredir=allure-results",
    #                "--type=alone",
    #                "--cases=../examples"]
    # print("run pytest：", pytest_args)
    # pytest.main(pytest_args, plugins=[CasesPlugin()])
    #
    # # 集成 allure 示例
    # os.system(r"allure generate -c -o report")  # 等于你在命令行里面执行 allure


# =========函数调用方式
# import io
# import sys
# import os
# import pytest
# from apitest.tool.apirunner.core.CasesPlugin import CasesPlugin
# from apitest.tool.apirunner.core.TestResultPlugin import TestResultPlugin
# # 设置 Python 解释器的默认编码
# sys.stdout.reconfigure(encoding='utf-8')
# sys.stderr.reconfigure(encoding='utf-8')
# def run(pytest_args):
#     # 处理命令行参数
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     test_runner_path = os.path.join(current_dir, "core/TestRunner.py")
#     final_pytest_args = [test_runner_path] + pytest_args
#     print("pytest run执行参数：", final_pytest_args)
#     # 设置返回信息
#     test_result_plugin = TestResultPlugin()
#     exit_code = pytest.main(final_pytest_args, plugins=[CasesPlugin(),test_result_plugin])
#     return {
#         "exit_code": exit_code,
#         "results": test_result_plugin.results,
#         "output": test_result_plugin.output
#
#     }
