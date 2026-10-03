# -*- coding: utf-8 -*-
import requests, jsonpath, re, json
from apitest.tool.apirunner.extend.script import run_script
from apitest.tool.apirunner.utils.AssertUtils import assert_exec
from apitest.tool.apirunner.utils.VarRender import refresh
from apitest.tool.apirunner.core.globalContext import g_context
import allure

class TestRunner:
    def test_case_execute(self, caseinfo):
        first_desc = caseinfo.get("desc", "")
        context_desc = caseinfo.get("context", {}).get("desc", "")
        # title = f"{first_desc}_{context_desc}"
        title = f"{context_desc}_{first_desc}"
        allure.dynamic.title(title)
        """
            http接口调用-核心执行器
        """
        print("++++++++++++++++++++++++++++++++++++++++++")
        print("用例执行前信息: ", caseinfo)
        print("++++++++++++++++++++++++++++++++++++++++++")
        # 获取用例的步骤
        steps = caseinfo["steps"]
        # 获取用例的上下文变量
        context = caseinfo.get("context", None)
        print("请求前的局部上下文变量context:", context)
        print("请求前的全局变量show_dict: ", g_context().show_dict())
        # 如果用例的上下文不是空的
        if context is not None:
            # 创建一个新字典，用于存储除 assertions 和 extractions 之外的键值对
            context_without_special_fields = {}
            for key, value in context.items():
                if key not in ['assertions', 'extractions']:
                    context_without_special_fields[key] = value
            print("排除后的context为", context_without_special_fields)
            # 将处理后的局部变量添加到全局变量中，如果有重复的就更新
            g_context().set_by_dict(context_without_special_fields)
        # 遍历测试步骤
        for step in steps:
            # 1. 请求前 - 执行前置脚本(脚本也可以引用变量)
            #refresh该函数使用 jinja2 模板引擎，将 target 中的变量占位符（使用 {{variable_name}} 格式）替换为 context 字典中对应的值。
            #这里获取全局变量，查找pre_script里的是否与全局变量有相同，如果有就替换，仅替换pre_script自身的
            pre_script = refresh(step.get("pre_script", None), g_context().show_dict())
            # 这个方法将前置脚本，步骤，和全局变量都传进入--为了执行前行前置脚本
            run_script.exec_script(pre_script,step,g_context().show_dict())

            # 2. 请求前 - 所有请求相关的参数做个变量渲染-提取出step的变量，然后去全局变量找是否可以替换{{}}的，替换完再给request_content
            request_content = { "url": step.get("url", None),
                                "method": step.get("method", None),
                                "params": step.get("params", None),
                                "data": step.get("data", None),
                                "json": step.get("json", None),
                                "headers": step.get("headers", None),
                                "cookies": step.get("cookies", None),
                                "timeout": step.get("timeout", None)}
            request_content = eval(refresh(request_content, g_context().show_dict()))
            print("执行前的request_content类型是: ", type(request_content))
            # 检查 json 字段是否为字符串，如果是则转换为字典
            if isinstance(request_content.get("json"), str):
                try:
                    request_content["json"] = json.loads(request_content["json"])
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误: {e}")
                    continue
            print("++++++++++++++++++++++++++++++++++++++++++")
            print("用例替换变量后信息: ", request_content)
            print("++++++++++++++++++++++++++++++++++++++++++")
            # 3. 具体发起请求进行操作 ，发起HTTP请求，进行返回结果断言
            response = requests.request(**request_content)
            # 手动指定编码
            response.encoding = 'utf-8'  # 假设编码为 UTF-8，可根据实际情况修改
            # response.encoding = response.apparent_encoding
            #这里将执行结果加到步骤了里
            step.update({
                "response": response
            })
            print("++++++++++++++++++++++++++++++++++++++++++")
            print("响应码为: ", response.status_code)
            print("++++++++++++++++++++++++++++++++++++++++++")
            print("响应头为: ", response.headers)
            print("++++++++++++++++++++++++++++++++++++++++++")
            print("响应内容为: ", response.text)
            print("++++++++++++++++++++++++++++++++++++++++++")
            # 判断 context 是否有ddt
            if context is not None:
                # 如果有断言
                if context is not None and 'assertions' in context:
                    for assertion in context['assertions']:
                        assert_type = assertion["type"]# 断言类型
                        assert_target = assertion["target"]# 断言路径
                        expected_value = assertion["expected"]# 预期值
                        # 如果断言的是响应码
                        if assert_target == 'status_code':
                            # 获取实际响应码
                            target_value = response.status_code
                        # 如果断言的是响应头内容
                        elif assert_target.startswith('headers.'):
                            header_key = assert_target.split('.')[1]
                            target_value = response.headers.get(header_key)
                        else:
                            # 使用 JSONPath 表达式获取目标值-响应体
                            target_value = jsonpath.jsonpath(response.json(), assert_target)
                            if target_value:
                                target_value = target_value[0]
                            else:
                                target_value = None

                            # 执行断言
                        if assert_type == "exists":  # 存在
                            assert target_value is not None, f"断言失败: {assert_target} {assert_type} {expected_value}"
                        elif assert_type == 'contains':  # 包含
                            assert str(expected_value) in str(
                                target_value), f"断言失败: {assert_target} {assert_type} {expected_value}"
                        elif assert_type == 'equals':  # 相同
                            assert str(target_value) == str(
                                expected_value), f"断言失败: {assert_target} {assert_type} {expected_value}"
                        else:
                            raise ValueError(f"不支持的断言类型: {assert_type}")
                        print(f"断言成功: {assert_target} {assert_type} {expected_value}")
                # 判断是否有要提取的变量
                if context is not None and 'extractions' in context:
                    for extraction in context['extractions']:
                        var_name = extraction['var_name']
                        extract_target = extraction['target']
                        # 使用 JSONPath 表达式提取数据
                        extracted_value = jsonpath.jsonpath(response.json(), extract_target)
                        if extracted_value:
                            extracted_value = extracted_value[0]
                            # 将提取的数据存储到全局变量
                            g_context().set_dict(var_name, extracted_value)
                            print(f"数据提取成功: {var_name} = {extracted_value}")
                        else:
                            print(f"数据提取失败: {extract_target}")
            # 没有ddt走后置
            else:
                # 4. 后置脚本(脚本也可以引用变量) 断言，参数提取-查找pre_script里的是否与全局变量有相同，如果有就替换，仅替换pre_script自身的
                # pre_script = refresh(step.get("post_script", None), g_context().show_dict())
                post_script = refresh(step.get("post_script", None), g_context().show_dict())
                # run_script.exec_script(pre_script,step,g_context().show_dict())
                run_script.exec_script(post_script, step, g_context().show_dict())


