# -*- coding: utf-8 -*-
# from apirunner.parse.CaseParser import case_parser
from apitest.tool.apirunner.parse.CaseParser import case_parser


class CasesPlugin:
    """
    pytest插件 - 用于pytest运行时的用例配置信息加载
    应用了 pytest 钩子函数
    """
    #这个钩子函数会先执行，他的作用是加两个自定义选项（显示标注自定义参数），一个是测试用例的类型yaml一个是测试用例的目录
    def pytest_addoption(self, parser):

        """
        增加pytest运行的配置项option_string也就是--type标识，理解为注册自定义参数，一个key放到执行参数里，action=store表示确定存到参数里，
        里说但仅就pytest_addoption，还没有进一步告知pytest要拿--type要做什么，只是把这两个自定义变量参数加入执行参数中default与help就是参数值
        """
        parser.addoption(
            "--type", action="store", default="yaml", help="测试用例类型"
        )
        parser.addoption(
            "--cases", action="store", default="../examples", help="测试用例目录"
        )

    #这个钩子函数会第二个执行，他的作用是收集测试用例并整合，拆分参数化等处理，最后完成所有用例的准备
    def pytest_generate_tests(self, metafunc):
        """
        method_meta: 运行的方法信息
        metafunc 是 pytest 框架在调用 pytest_generate_tests 时传入的一个对象，它包含了当前测试函数的元信息。
        """
        # 读取用户传过来的参数-这里的type与cases其实刚才的自定义参数，他们是要获取参数值的
        case_type = metafunc.config.getoption("type")
        cases_dir = metafunc.config.getoption("cases")
        # 读取测试用例这里的方法是将两个参数值传给case_parser做路径解析
        #data接到的值数据结构为处理后的{"case_name":[], "cases_info":[]}
        data = case_parser(case_type, cases_dir)
        print("data的值是",data)
        desc_values = [case_info['desc'] for case_info in data['case_infos']]
        print("++++++++++++++++++++++++++++++++++++++++++")
        print("用例顺序为:", desc_values)
        print("++++++++++++++++++++++++++++++++++++++++++")
        # 把测试用例作为参数化，交给 runner 执行
        #metafunc.fixturenames 是一个列表，里面包含了当前测试函数所需要的所有 fixture 名称。
        # Fixture 是 pytest 框架里的一种机制，用于为测试函数提供前置条件、数据或者资源。
        #这行代码的作用是检查当前测试函数是否需要名为 caseinfo 的 fixture。
        # 若 metafunc.fixturenames 列表中包含 "caseinfo"，
        # 就意味着当前测试函数需要 caseinfo 这个参数，接着就可以对该测试函数进行参数化。
        if "caseinfo" in metafunc.fixturenames:
            # 那么这句话，就是将实际的参数化或非参数化的执行数据等，都加载进去，相当于数据真的准备完毕并加载了
            metafunc.parametrize("caseinfo", data['case_infos'], ids=data['case_names'])

    # 第三个钩子函数-主要处理 pytest 收集到的测试用例进行修改和调整
    #对测试用例的名称进行编码转换，以确保名称能正确显示。
    # 将测试用例的节点 ID 设置为其参数化调用规范中的 ID，方便后续测试执行和结果展示。
    def pytest_collection_modifyitems(self,items):
        for item in items:
            # print("pytest_collection_modifyitems的item",item)
            item.name = item.name.encode("utf-8").decode("unicode_escape")
            # print("pytest_collection_modifyitems的item.name ",item.name )
            # item._nodeid = item.callspec.id
            # print("pytest_collection_modifyitems的item._nodeid ",item._nodeid )
            item._nodeid = item._nodeid.encode("utf-8").decode("unicode_escape")
            start_index = item._nodeid.find('[')
            end_index = item._nodeid.find(']')
            if start_index != -1 and end_index != -1:
                item._nodeid = item._nodeid[start_index + 1:end_index]





            # print(f"Original test case name: {item.name}")
            # try:
            #     # 尝试直接使用 Unicode 字符串
            #     decoded_name = item.name.encode('raw_unicode_escape').decode('unicode_escape')
            #     item.name = decoded_name
            #     print(f"Decoded test case name: {item.name}")
            #     item._nodeid = item.callspec.id
            # except Exception as e:
            #     print(f"Error processing test case name: {item.name}, {e}")
