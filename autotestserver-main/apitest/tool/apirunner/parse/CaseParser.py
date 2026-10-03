# -*- coding: utf-8 -*-
# 用例解析器， 根据你传过来的参数，选择不同的解析器
import os

from apitest.tool.apirunner.parse.YamlCaseParser import yaml_case_parser
from apitest.tool.apirunner.parse.yamlCaseParser_alone import yaml_case_parser_alone


def case_parser(case_type, case_dir):
    """
    type： 用例类型
    dir: 用例所在文件夹
    return: 返回 {"case_name":[], "cases_info":[]}
    """
    #传入的用例目录路径 case_dir 转换为绝对路径
    config_path = os.path.abspath(case_dir)
    # print("用例读取中...", dir)
    #这里要对yaml文件做处理-传入的是最开始传入的文件夹（里面两个yaml文件）的绝对路径
    if case_type == 'yaml':
        # 这里会返回处理后的{"case_name":[], "cases_info":[]}
        return yaml_case_parser(config_path)
    elif case_type == 'alone':
        return yaml_case_parser_alone(config_path)

    return {"case_name": [], "cases_info": []}


def test_yaml_case_parser():
    # 单元测试 ，检查 yaml_case_parser 方法的正确性
    data = case_parser("yaml", "../../examples")
    # print(data)