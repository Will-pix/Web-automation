import json
import os
import shutil
import subprocess
import uuid

import yaml
from core.resp_model import respModel
from extensions import database
from apitest.model.ApiInfoModel import ApiInfo
from flask import Blueprint, request, current_app
from apitest.model.ApiInfoModel import ApiInfo
from datetime import datetime

module_name = "ApiInfo"
module_model = ApiInfo
module_route = Blueprint(f"route_{module_name}", __name__)

@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    try:
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # with application.app_context():
        filter_list = []
        # 添加 项目筛选条件
        project_id = request.json.get("project_id", 0)
        if type(project_id) is not str and project_id > 0:
            filter_list.append(module_model.project_id == project_id)
        # 添加 模块筛选条件
        module_id = request.json.get("module_id", 0)
        if type(module_id) is not str and module_id > 0:
            filter_list.append(module_model.module_id == module_id)
        # 添加名称模糊搜索条件
        api_name = request.json.get("api_name", "")
        if len(api_name) > 0:
            filter_list.append(module_model.api_name.like(f'%{api_name}%'))
        # 数据库查询
        datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    try:
        data_id = int(request.args.get("id"))
        # with application.app_context():
        data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    try:
        # with application.app_context():
        request.json["id"] = None # ID自增长
        data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        database.session.add(data)
        # 获取新增后的ID并返回
        database.session.flush()
        data_id = data.id
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    try:
        # with application.app_context():
        module_model.query.filter_by(id=request.json["id"]).update(request.json)
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    try:
        # with application.app_context():
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.route(f"/{module_name}/debug", methods=["POST"])
def debug_execute():
    try:
        # 接收前端传递过来的 ApiInfo
        api_info = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        # 获取配置中指定的 临时文件生成地址
        cases_dir = current_app.config['CASES_ROOT_DIR']
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cases_dir = os.path.join(current_dir,cases_dir)
        # 该次执行唯一ID
        execute_uuid = uuid.uuid4().__str__()
        # 1.0 创建 该次执行对应的文件夹
        run_tmp_dir = os.path.join(cases_dir, execute_uuid)
        os.makedirs(run_tmp_dir, exist_ok=True)
        # 1.1 先组装 Debug变量 数据 生成 context.yaml 文件
        context_data = {}
        if api_info.debug_vars:
            for d in json.loads(str(api_info.debug_vars).replace("'", '"')):
                context_data.update({d["key"]: d["value"]})
        context_yaml_file = os.path.join(run_tmp_dir, "context.yaml")
        with open(context_yaml_file, "w", encoding="utf-8") as context_file:
            yaml.dump(context_data, context_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

        # 1.2 把数据转变为yaml 保存到 测试套件执行对应的文件夹
        # 填充测试用例信息
        test_case_data = {
            "desc": api_info.api_name,
            "steps": [
                {
                    "url": api_info.request_url,
                    "method": api_info.request_method,
                }
            ]
        }

        # 0. 如果存在请求头，则添加请求头
        if api_info.request_headers:
            requests_header = {}
            for d in json.loads(str(api_info.request_headers).replace("'", '"')):
                requests_header.update({d["key"]: d["value"]})
            if len(requests_header.items()) > 0:
                test_case_data["steps"][0]["header"] = requests_header
        # 1. 仅在 data 不为空时添加
        if api_info.request_form_datas:
            requests_datas = {}
            for d in json.loads(str(api_info.request_form_datas).replace("'", '"')):
                requests_datas.update({d["key"]: d["value"]})
            if len(requests_datas.items()) > 0:
                test_case_data["steps"][0]["data"] = requests_datas
        # 2. 仅在 www_form_datas 不为空时添加
        if api_info.request_www_form_datas:
            requests_datas = {}
            for d in json.loads(str(api_info.request_www_form_datas).replace("'", '"')):
                requests_datas.update({d["key"]: d["value"]})
            if len(requests_datas.items()) > 0:
                test_case_data["steps"][0]["data"] = requests_datas
        # 3.仅在 params 不为空时添加
        if api_info.request_params:
            requests_params = {}
            for d in json.loads(str(api_info.request_params).replace("'", '"')):
                requests_params.update({d["key"]: d["value"]})
            if len(requests_params.items()) > 0:
                test_case_data["steps"][0]["params"] = requests_params
        # 4.仅在 json_data 不为空时添加
        if api_info.requests_json_data:
            test_case_data["steps"][0]["json"] = api_info.requests_json_data
        # 5.如果存在 前置脚本，则添加
        if api_info.pre_request:
            test_case_data["steps"][0]["pre_script"] = api_info.pre_request
        # 6.如果存在 后置脚本，则添加
        if api_info.post_request:
            test_case_data["steps"][0]["post_script"] = api_info.post_request

        # 将测试用例数据写入 YAML 文件，格式为 执行顺序_名称.yaml
        case_file_name = uuid.uuid4()
        test_case_filename = f"1_{case_file_name}.yaml"
        test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
        with open(test_case_yaml_file, "w", encoding="utf-8") as test_case_file:
            yaml.dump(test_case_data, test_case_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 cli.py 文件的绝对路径i
        # cli_file_path = os.path.join(current_dir, '../tool/apirunner/clii.py')
        API_CLII_DIR = current_app.config['API_CLII_DIR']
        cli_file_path = os.path.join(current_dir, API_CLII_DIR)

        remote_command = f"python {cli_file_path} --cases={run_tmp_dir} -sv --capture=tee-sys "
        command_output = subprocess.check_output(remote_command, shell=True,
                                                 universal_newlines=True, encoding='utf-8',errors='ignore')
        # 转义处理，将 Unicode 编码转换为实际字符
        decoded_output = command_output.encode('raw_unicode_escape').decode('unicode_escape')
        # print("返回的数据：", decoded_output)
        try:
            shutil.rmtree(run_tmp_dir)
        except Exception as e:
            print(f"删除临时文件夹 {run_tmp_dir} 时出错: {e}")
        return respModel.ok_resp(msg="执行结束", dic_t={"output": decoded_output})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"执行出现错误：{e}")
