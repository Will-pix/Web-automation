import shutil
# from os.path import join
import allure
from core.resp_model import respModel
from extensions import database
from flask import Blueprint, request, current_app
from apitest.model.ApiCollectionModel import ApiCollection
from datetime import datetime
import json, os, subprocess, uuid, yaml
from apitest.model.ApiCaseModel import ApiCase

# 模块信息
from apitest.model.ApiHistoryModel import ApiHistoryModel

module_name = "ApiCollection"  # 模块名称
module_model = ApiCollection
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # with application.app_context():
        filter_list = []
        # ====筛选条件(如果有筛选条件，在这里拓展 - filter)
        # 添加名称模糊搜索条件
        collection_name = request.json.get("collection_name", "")
        if len(collection_name) > 0:
            filter_list.append(module_model.collection_name.like(f'%{collection_name}%'))
        # 添加 项目筛选条件
        project_id = request.json.get("project_id", 0)
        if type(project_id) is not str and project_id > 0:
            filter_list.append(module_model.project_id == project_id)
        # =====结束
        # 数据库查询
        datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        # with application.app_context():
            # 数据库查询
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
    """ 新增数据 """
    try:
        # with application.app_context():
        request.json["id"] = None  # ID自增长
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
    """ 修改数据 """
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
    """ 删除数据  删除的同时，需要处理掉中间表"""
    try:
        # with application.app_context():
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")



# 测试集执行
@module_route.route(f"/{module_name}/excuteTest", methods=["GET"])
def execute_test():
    # 获取配置中指定的，文件生成地址--数据："/Users/hcflask/hcweb/apitest/testfile"
    cases_dir = current_app.config['CASES_ROOT_DIR']
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cases_dir = os.path.join(current_dir, cases_dir)
    # 获取前端传入要执行的测试套件集合ID,args是获取url的参数，get用法--数据：测试集id
    collection_id = request.args.get("id")
    # 数据库上下文
    with application.app_context():
        # 创建数据库会话
        session = database.session
        # 通过创建的会话，获取集合模型的数据--数据：获取的是该集合详细信息
        collection = session.query(module_model).filter_by(id=collection_id).first()
        # 创建一个空列表-装填测试集的参数化参数--数据：一定要放一个空字典，为了在没有参数化时也可以遍历执行一次
        collection_params = [{}]
        # 如果有 collection_params 代表 可能需要 多次执行该套件
        if collection.collection_params:
            # json字符串转为字典-并覆盖空列表
            collection_params = json.loads(collection.collection_params)
        # 循环生成 对应的 测试用例 yaml 文件及文件夹,执行次数==测试集参数个数
        for collection_param in collection_params:
            # 该次执行唯一ID，通过魔术方法转为字符串
            execute_uuid = uuid.uuid4().__str__()
            # （临时生成）创建 该次 测试套件执行对应的文件夹，数据：/Users/hcflask/hcweb/apitest/testfile+uuid（join会在两个值中间加上/）
            collection_dir = os.path.join(cases_dir,execute_uuid)
            # 实际创建文件夹-exist_ok的作用是如果有相同的文件夹则什么都不做
            os.makedirs(collection_dir,exist_ok=True)
            # 组装环境变量，生成context.yaml文件
            # context的空字典
            context_data = {}
            # 如果测试集环境变量存在则赋值
            if collection.collection_env:
                # json字符串转为字典-并覆盖空字典
                context_data =json.loads(collection.collection_env)
            # 将测试集的参数化数据加入到环境参数里-如果相同则修改
            context_data.update(collection_param)
            # (临时)创建context.yml的文件地址，放进创建的文件夹内,数据：/Users/hcflask/hcweb/apitest/testfile+uuid+/context.yaml
            context_yaml_file = os.path.join(collection_dir,"context.yaml")
            # 实际创建文件并放进文件夹内
            with open(context_yaml_file, 'w', encoding='utf-8') as context_file:
                # yaml.dump将字典转为yaml格式字符串，写入context_file，default_flow_style=False代表数据的层级结构（换行）,allow_unicode代表允许输出yaml字符串中包含unicode字符
                yaml.dump(context_data, context_file, default_flow_style=False, encoding='utf-8',allow_unicode=True)
            # ↑到此创建一个文件夹，并且在文件夹内插入了一个context.yaml的文件，这个文件包含了测试集的环境变量与参数变量（这两个都可能为空,数据会为{}）
            # ↓接下来需要生成用例的yaml文件
            # 获取集合关联的 ApiCase 中间表数据,通过测试集id获取
            api_cases = session.query(ApiCase).filter_by(collection_id=collection.id).all()
            # 遍历这个中间表数据
            for api_case in api_cases:
                # 通过中间表数据的接口id，获取接口的详细信息
                api_info = session.query(ApiInfo).get(api_case.api_info_id)
                # print("此时的api_info",api_info.id)
                # 填充测试用例信息-yaml的模版信息
                test_case_data = {
                    "desc": f"{api_info.api_name}_{api_info.id}",
                    "steps":[
                        {
                            "url":api_info.request_url,
                            "method":api_info.request_method,
                        }
                    ]
                }
                # 获取中间表的接口参数化信息，如果不存在就为空
                params_data = api_case.param_data or None
                # 如果用例参数化为空就不添加，不为空就加入到用例的ddts内
                if params_data:
                    # 在添加前，需要先json字符串转为字典
                    test_case_data["ddts"] = json.loads(params_data)
                # 如果接口存在请求头就添加
                if api_info.request_headers:
                    # 因为request_headers是一个列表，所以需要循环取出，放入一个字典里
                    requests_header = {}
                    # 遍历前，request_headers还是json字符串，需要转python对象列表，并遍历每个键值元素
                    for d in json.loads(api_info.request_headers):
                        # 这里，分别取出元素的key和value,用update，这样如果有相同的key，则会覆盖更新
                        requests_header.update({d["key"]: d["value"]})
                    # 检查 requests_header 字典是否为空
                    if len(requests_header.items()) > 0:
                        # 插入到steps（已存在）下的下标第一个，header（不存在）创建并赋值
                        test_case_data["steps"][0]["header"] = requests_header
                # 如果接口存在form_data就添加
                if api_info.request_form_datas:
                    # 因为request_form_data是一个列表，所以需要循环取出，放入一个字典里
                    requests_datas = {}
                    for d in json.loads(api_info.request_form_datas):
                        requests_datas.update({d["key"]: d["value"]})
                    if len(requests_datas.items()) > 0:
                        test_case_data["steps"][0]["data"] = requests_datas
                # 2. 仅在 www_form_datas 不为空时添加，注意：上面和这里使用相同的方式，属于2选1，会生成覆盖数据的可能
                if api_info.request_www_form_datas:
                    requests_datas = {}
                    for d in json.loads(api_info.request_www_form_datas):
                        requests_datas.update({d["key"]: d["value"]})
                    if len(requests_datas.items()) > 0:
                        test_case_data["steps"][0]["data"] = requests_datas
                # 3.仅在 params 不为空时添加
                if api_info.request_params:
                    requests_params = {}
                    for d in json.loads(api_info.request_params):
                        requests_params.update({d["key"]: d["value"]})
                    if len(requests_params.items()) > 0:
                        test_case_data["steps"][0]["params"] = requests_params
                # 4.仅在 json_data 不为空时添加，注意：1.request可以将一个json字符串自动转为json进行请求（前提是字符串格式合规）
                # 2.其它添加项需要转化的原因是他们有需要额外处理的部分才能加入到总数据里
                if api_info.requests_json_data:
                    test_case_data["steps"][0]["json"] = api_info.requests_json_data
                # 5.如果存在 前置脚本，则添加
                if api_info.pre_request:
                    test_case_data["steps"][0]["pre_script"] = api_info.pre_request
                # 6.如果存在 后置脚本，则添加
                if api_info.post_request:
                    test_case_data["steps"][0]["post_script"] = api_info.post_request
                # 以上主信息完成，接下来需要将他们生成yaml文件并保存到文件夹里
                # 将测试用例数据写入 YAML 文件，格式为 执行顺序_名称.yaml
                # 生成uuid数据
                case_file_name = uuid.uuid4()
                # 生成文件名称-获取中间表的顺序+uuid+格式文件名
                test_case_filename = f"{api_case.run_order}_{case_file_name}.yaml"
                # 将文件夹的路径地址+上面的获取中间表的顺序+uuid+格式文件名
                test_case_yaml_file = os.path.join(collection_dir, test_case_filename)
                # 测试用例的总结构数据为
                print("测试用例的总结构数据为",test_case_data)
                # 将上面的临时存储名称加上yaml的总数据，放进文件夹里
                with open(test_case_yaml_file, "w", encoding="utf-8") as test_case_file:
                    # yaml.dump将字典转为yaml格式字符串，test_case_file，default_flow_style=False代表数据的层级结构（换行）,allow_unicode代表允许输出yaml字符串中包含unicode字符
                    yaml.dump(test_case_data, test_case_file,default_flow_style=False,encoding='utf-8',allow_unicode=True)
                # 到这里，用例的所有数据文件都执行完毕，并存储在一个文件夹里
                # 获取测试报告的目录，数据：/Users/hcflask/hcweb/apitest/report
    report_root_dir = current_app.config['REPORT_ROOT_DIR']
    report_root_dir = os.path.join(current_dir, report_root_dir)            # 拼接报告地址+复用创建文件夹的uuid，数据：/Users/hcflask/hcweb/apitest/report/uuid/-data
    report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data") # 测试数据
    # 拼接报告html地址+复用创建文件夹的uuid，数据：/Users/hcflask/hcweb/apitest/report/uuid
    report_html_path = os.path.join(report_root_dir, execute_uuid)  # 测试html报告
    # 到此，会将测试报告与html都放在一个文件夹中
    # 执行测试
    # 构建当前文件的绝对路径
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # # 构建 cli.py 文件的绝对路径-当前文件的上一级下的/tool/apirunner/cli.py
    # cli_file_path = os.path.join(current_dir, '../tool/apirunner/cli.py')
    # # 这里通过python命令执行，传递cli所在的路径，传递yaml所在的文件夹目录，传递报告的执行参数与报告的存储路径
    # remote_command = f"python {cli_file_path} --cases={collection_dir} -sv --capture=tee-sys --alluredir={report_data_path} "
    # command_output = subprocess.check_output(remote_command, shell=True,
    #                                          universal_newlines=True, encoding='utf-8', errors='ignore')
    # # 转义处理，将 Unicode 编码转换为实际字符
    # decoded_output = command_output.encode('raw_unicode_escape').decode('unicode_escape')
    # print("返回的数据：", decoded_output)


    # ========函数调用方式
    from apitest.tool.apirunner.cli import run
    # 构建参数信息
    pytest_cmd_config = [
        f"--cases={collection_dir}",
        "-sv",
        "--capture=tee-sys",
        f"--alluredir={report_data_path}"
    ]
    try:
        # 调用 run 函数
        result = run(pytest_cmd_config)
        exit_code = result["exit_code"]

        results = result["results"]
        output = result["output"]
        print("执行器返回的result:",result)
        # 构建 Allure 命令
        API_ALLURE_DIR = current_app.config["API_ALLURE_DIR"]
        allure_path = API_ALLURE_DIR  # 替换为你的实际路径
        # command = f"allure generate {report_data_path} -clean -o {report_html_path}"
        command = [allure_path, "generate", report_data_path, "-c", "-o", report_html_path]

        # 执行命令
        result = subprocess.run(command, shell=False, check=True, text=True, capture_output=True)
        print("命令执行输出:", result.stdout)
        # output_str = ''.join(output)  # 将输出信息列表转换为字符串
        # 删除测试数据
        shutil.rmtree(collection_dir)
        # 删除测试报告data
        shutil.rmtree(report_data_path)
        # 执行通过统计
        print("执行器返回的result:",result)
        result_list = []
        for i in results:
            result_list.append(i["outcome"])
        result_passed = result_list.count("passed")
        result_failed = result_list.count("failed")
        result_num = len(result_list)
        history_desc = "总数:{},通过{},失败{}".format(result_num, result_passed, result_failed)
        # 统计总数
        print("统计总数", history_desc)
        # 存储执行，id，集合id，简述，报告id，时间
        report = ApiHistoryModel(id=0, collection_id=collection_id, history_desc=history_desc,
                                 history_detail=execute_uuid,
                                 create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        session.add(report)
        session.commit()
        if exit_code == 0:
            return respModel.ok_resp(msg="执行结束，测试成功", dic_t={"results": results})
        else:
            return respModel.ok_resp(msg="执行结束，测试失败", dic_t={"results": results})
    except Exception as e:
        return respModel.error_resp(msg=f"执行 pytest 时出现错误: {str(e)}")
    # ========







        # return respModel.ok_resp(msg="执行结束", dic_t={"output": decoded_output})
# 给任务调用
def execute_test_task(collection_id):
    # 获取配置中指定的，文件生成地址--数据："/Users/hcflask/hcweb/apitest/testfile"
    cases_dir = current_app.config['CASES_ROOT_DIR']
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cases_dir = os.path.join(current_dir, cases_dir)
    # 获取前端传入要执行的测试套件集合ID,args是获取url的参数，get用法--数据：测试集id
    # collection_id = request.args.get("id")
    # 数据库上下文
    with application.app_context():
        # 创建数据库会话
        session = database.session
        # 通过创建的会话，获取集合模型的数据--数据：获取的是该集合详细信息
        collection = session.query(module_model).filter_by(id=collection_id).first()
        # 创建一个空列表-装填测试集的参数化参数--数据：一定要放一个空字典，为了在没有参数化时也可以遍历执行一次
        collection_params = [{}]
        # 如果有 collection_params 代表 可能需要 多次执行该套件
        if collection.collection_params:
            # json字符串转为字典-并覆盖空列表
            collection_params = json.loads(collection.collection_params)
        # 循环生成 对应的 测试用例 yaml 文件及文件夹,执行次数==测试集参数个数
        for collection_param in collection_params:
            # 该次执行唯一ID，通过魔术方法转为字符串
            execute_uuid = uuid.uuid4().__str__()
            # （临时生成）创建 该次 测试套件执行对应的文件夹，数据：/Users/hcflask/hcweb/apitest/testfile+uuid（join会在两个值中间加上/）
            collection_dir = os.path.join(cases_dir,execute_uuid)
            # 实际创建文件夹-exist_ok的作用是如果有相同的文件夹则什么都不做
            os.makedirs(collection_dir,exist_ok=True)
            # 组装环境变量，生成context.yaml文件
            # context的空字典
            context_data = {}
            # 如果测试集环境变量存在则赋值
            if collection.collection_env:
                # json字符串转为字典-并覆盖空字典
                context_data =json.loads(collection.collection_env)
            # 将测试集的参数化数据加入到环境参数里-如果相同则修改
            context_data.update(collection_param)
            # (临时)创建context.yml的文件地址，放进创建的文件夹内,数据：/Users/hcflask/hcweb/apitest/testfile+uuid+/context.yaml
            context_yaml_file = os.path.join(collection_dir,"context.yaml")
            # 实际创建文件并放进文件夹内
            with open(context_yaml_file, 'w', encoding='utf-8') as context_file:
                # yaml.dump将字典转为yaml格式字符串，写入context_file，default_flow_style=False代表数据的层级结构（换行）,allow_unicode代表允许输出yaml字符串中包含unicode字符
                yaml.dump(context_data, context_file, default_flow_style=False, encoding='utf-8',allow_unicode=True)
            # ↑到此创建一个文件夹，并且在文件夹内插入了一个context.yaml的文件，这个文件包含了测试集的环境变量与参数变量（这两个都可能为空,数据会为{}）
            # ↓接下来需要生成用例的yaml文件
            # 获取集合关联的 ApiCase 中间表数据,通过测试集id获取
            api_cases = session.query(ApiCase).filter_by(collection_id=collection.id).all()
            # 遍历这个中间表数据
            for api_case in api_cases:
                # 通过中间表数据的接口id，获取接口的详细信息
                api_info = session.query(ApiInfo).get(api_case.api_info_id)
                # print("此时的api_info",api_info.id)
                # 填充测试用例信息-yaml的模版信息
                test_case_data = {
                    "desc": f"{api_info.api_name}_{api_info.id}",
                    "steps":[
                        {
                            "url":api_info.request_url,
                            "method":api_info.request_method,
                        }
                    ]
                }
                # 获取中间表的接口参数化信息，如果不存在就为空
                params_data = api_case.param_data or None
                # 如果用例参数化为空就不添加，不为空就加入到用例的ddts内
                if params_data:
                    # 在添加前，需要先json字符串转为字典
                    test_case_data["ddts"] = json.loads(params_data)
                # 如果接口存在请求头就添加
                if api_info.request_headers:
                    # 因为request_headers是一个列表，所以需要循环取出，放入一个字典里
                    requests_header = {}
                    # 遍历前，request_headers还是json字符串，需要转python对象列表，并遍历每个键值元素
                    for d in json.loads(api_info.request_headers):
                        # 这里，分别取出元素的key和value,用update，这样如果有相同的key，则会覆盖更新
                        requests_header.update({d["key"]: d["value"]})
                    # 检查 requests_header 字典是否为空
                    if len(requests_header.items()) > 0:
                        # 插入到steps（已存在）下的下标第一个，header（不存在）创建并赋值
                        test_case_data["steps"][0]["header"] = requests_header
                # 如果接口存在form_data就添加
                if api_info.request_form_datas:
                    # 因为request_form_data是一个列表，所以需要循环取出，放入一个字典里
                    requests_datas = {}
                    for d in json.loads(api_info.request_form_datas):
                        requests_datas.update({d["key"]: d["value"]})
                    if len(requests_datas.items()) > 0:
                        test_case_data["steps"][0]["data"] = requests_datas
                # 2. 仅在 www_form_datas 不为空时添加，注意：上面和这里使用相同的方式，属于2选1，会生成覆盖数据的可能
                if api_info.request_www_form_datas:
                    requests_datas = {}
                    for d in json.loads(api_info.request_www_form_datas):
                        requests_datas.update({d["key"]: d["value"]})
                    if len(requests_datas.items()) > 0:
                        test_case_data["steps"][0]["data"] = requests_datas
                # 3.仅在 params 不为空时添加
                if api_info.request_params:
                    requests_params = {}
                    for d in json.loads(api_info.request_params):
                        requests_params.update({d["key"]: d["value"]})
                    if len(requests_params.items()) > 0:
                        test_case_data["steps"][0]["params"] = requests_params
                # 4.仅在 json_data 不为空时添加，注意：1.request可以将一个json字符串自动转为json进行请求（前提是字符串格式合规）
                # 2.其它添加项需要转化的原因是他们有需要额外处理的部分才能加入到总数据里
                if api_info.requests_json_data:
                    test_case_data["steps"][0]["json"] = api_info.requests_json_data
                # 5.如果存在 前置脚本，则添加
                if api_info.pre_request:
                    test_case_data["steps"][0]["pre_script"] = api_info.pre_request
                # 6.如果存在 后置脚本，则添加
                if api_info.post_request:
                    test_case_data["steps"][0]["post_script"] = api_info.post_request
                # 以上主信息完成，接下来需要将他们生成yaml文件并保存到文件夹里
                # 将测试用例数据写入 YAML 文件，格式为 执行顺序_名称.yaml
                # 生成uuid数据
                case_file_name = uuid.uuid4()
                # 生成文件名称-获取中间表的顺序+uuid+格式文件名
                test_case_filename = f"{api_case.run_order}_{case_file_name}.yaml"
                # 将文件夹的路径地址+上面的获取中间表的顺序+uuid+格式文件名
                test_case_yaml_file = os.path.join(collection_dir, test_case_filename)
                # 测试用例的总结构数据为
                print("测试用例的总结构数据为",test_case_data)
                # 将上面的临时存储名称加上yaml的总数据，放进文件夹里
                with open(test_case_yaml_file, "w", encoding="utf-8") as test_case_file:
                    # yaml.dump将字典转为yaml格式字符串，test_case_file，default_flow_style=False代表数据的层级结构（换行）,allow_unicode代表允许输出yaml字符串中包含unicode字符
                    yaml.dump(test_case_data, test_case_file,default_flow_style=False,encoding='utf-8',allow_unicode=True)
                # 到这里，用例的所有数据文件都执行完毕，并存储在一个文件夹里
                # 获取测试报告的目录，数据：/Users/hcflask/hcweb/apitest/report

            report_root_dir = application.config['REPORT_ROOT_DIR']
            report_root_dir = os.path.join(current_dir, report_root_dir)
            # 拼接报告地址+复用创建文件夹的uuid，数据：/Users/hcflask/hcweb/apitest/report/uuid/-data
            report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data") # 测试数据
            # 拼接报告html地址+复用创建文件夹的uuid，数据：/Users/hcflask/hcweb/apitest/report/uuid
            report_html_path = os.path.join(report_root_dir, execute_uuid)  # 测试html报告
            # 到此，会将测试报告与html都放在一个文件夹中
            # 执行测试
            # 构建当前文件的绝对路径
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            # # 构建 cli.py 文件的绝对路径-当前文件的上一级下的/tool/apirunner/cli.py
            # cli_file_path = os.path.join(current_dir, '../tool/apirunner/cli.py')
            # # 这里通过python命令执行，传递cli所在的路径，传递yaml所在的文件夹目录，传递报告的执行参数与报告的存储路径
            # remote_command = f"python {cli_file_path} --cases={collection_dir} -sv --capture=tee-sys --alluredir={report_data_path} "
            # command_output = subprocess.check_output(remote_command, shell=True,
            #                                          universal_newlines=True, encoding='utf-8', errors='ignore')
            # # 转义处理，将 Unicode 编码转换为实际字符
            # decoded_output = command_output.encode('raw_unicode_escape').decode('unicode_escape')
            # print("返回的数据：", decoded_output)


            # ========函数调用方式
            from apitest.tool.apirunner.cli import run
            # 构建参数信息
            pytest_cmd_config = [
                f"--cases={collection_dir}",
                "-sv",
                "--capture=tee-sys",
                f"--alluredir={report_data_path}"
            ]
            try:
                # 调用 run 函数
                result = run(pytest_cmd_config)
                exit_code = result["exit_code"]

                results = result["results"]
                output = result["output"]
                print("执行器返回的result:",result)
                # 构建 Allure 命令
                # command = f"allure generate {report_data_path} -clean -o {report_html_path}"
                API_ALLURE_DIR = application.config["API_ALLURE_DIR"]
                allure_path = API_ALLURE_DIR  # 替换为你的实际路径
                command = [allure_path, "generate", report_data_path, "-c", "-o", report_html_path]

                # 执行命令
                result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
                print("命令执行输出:", result.stdout)
                # output_str = ''.join(output)  # 将输出信息列表转换为字符串
                # 删除测试数据
                shutil.rmtree(collection_dir)
                # 删除测试报告data
                shutil.rmtree(report_data_path)
                # 执行通过统计
                print("执行器返回的result:",result)
                result_list = []
                for i in results:
                    result_list.append(i["outcome"])
                result_passed = result_list.count("passed")
                result_failed = result_list.count("failed")
                result_num = len(result_list)
                history_desc = "总数:{},通过{},失败{}".format(result_num, result_passed, result_failed)
                # 统计总数
                print("统计总数", history_desc)
                # 存储执行，id，集合id，简述，报告id，时间
                report = ApiHistoryModel(id=0, collection_id=collection_id, history_desc=history_desc,
                                         history_detail=execute_uuid,
                                         create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
                session.add(report)
                session.commit()
                if exit_code == 0:
                    return respModel.ok_resp(msg="执行结束，测试成功", dic_t={"results": results})
                else:
                    return respModel.ok_resp(msg="执行结束，测试失败", dic_t={"results": results})
            except Exception as e:
                return respModel.error_resp(msg=f"执行 pytest 时出现错误: {str(e)}")














