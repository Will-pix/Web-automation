import json
import os
import re
import shutil
import sys
import time
import uuid
import yaml
import subprocess

from flask import Blueprint, request, current_app

from core.resp_model import respModel
from extensions import database
from webtest.api.clear_report import folder_cleanup_main
from webtest.api.feishu_report import webinfo_feishu
from platformconfig.service.runtime_store import build_public_report_url
from webtest.model.WebBrowserModel import WebBrowser
from webtest.model.WebDbBaseModel import WebDbBase
from webtest.model.WebInfoModel import WebInfo
from datetime import datetime

# 模块信息
from webtest.model.WebInfoStepModel import WebInfoStep
from webtest.model.WebKeyWordModel import WebKeyWord
from webtest.model.WebProjectModel import WebProject
from webtest.model.WebInfoPreModel import WebInfoPre

module_name = "WebInfo"  # 模块名称
module_model = WebInfo
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    # 已删除多余的with语句
    datas = module_model.query.all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # 已删除多余的with语句
        filter_list = []
        # 添加操作类型模糊搜索条件
        case_name = request.json.get("case_name", "")
        if len(case_name) > 0:
            filter_list.append(module_model.case_name.like(f'%{case_name}%'))
        project_id = request.json.get("project_id", 0)
        if type(project_id)  is not str and project_id >0:
            filter_list.append(module_model.project_id == project_id)

        # 3. 新增条件1：按创建人ID查询（精确匹配，ID无需模糊）
        create_by = request.json.get("create_by")  # 前端传创建人ID，不传则不筛选
        if create_by:
            filter_list.append(module_model.create_by == create_by)

        # 4. 新增条件2：按修改人ID查询（精确匹配）
        update_by = request.json.get("update_by")  # 前端传修改人ID，不传则不筛选
        if update_by:
            filter_list.append(module_model.update_by == update_by)

        # 5. 新增条件3：按负责人ID查询（精确匹配）
        principal = request.json.get("principal")  # 前端传修改人ID，不传则不筛选
        if principal:
            filter_list.append(module_model.principal == principal)

        # 是否前置
        is_pre = request.json.get("is_pre")  # 前端传修改人ID，不传则不筛选
        if is_pre:
            filter_list.append(module_model.is_pre == is_pre)

        # 数据库查询
        datas = module_model.query.filter(*filter_list).order_by(module_model.create_time.desc()).limit(page_size).offset((page - 1) * page_size).all()
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
        # 已删除多余的with语句
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
        # 校验用例名称不能以数字结尾（避免与pytest自动编号冲突）
        case_name = request.json.get("case_name", "")
        if case_name and re.search(r'\d+$', case_name):
            return respModel.error_resp(msg="用例名称不能以数字结尾，请修改后重试")
        
        # 已删除多余的with语句
        request.json["id"] = None  # ID自增长
        data = module_model(** request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
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
        # 校验用例名称不能以数字结尾（避免与pytest自动编号冲突）
        case_name = request.json.get("case_name", "")
        if case_name and re.search(r'\d+$', case_name):
            return respModel.error_resp(msg="用例名称不能以数字结尾，请修改后重试")
        
        # 已删除多余的with语句
        update_data = request.json
        # 修正更新方式：先查实例再赋值，触发基类before_update
        target_data = module_model.query.filter_by(id=update_data["id"]).first()
        if target_data:
            for key, value in update_data.items():
                if key != "id":  # 排除主键
                    setattr(target_data, key, value)
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        # 已删除多余的with语句
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

# web执行
@module_route.route(f"/{module_name}/debugTest", methods=["POST"])
def debugTest():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("current_dir是",current_dir)
    # 获取配置中指定的 临时文件生成地址
    cases_dir = current_app.config['CASES_ROOT_WEB_DIR']
    cases_dir = os.path.join(current_dir, cases_dir)

    # 该次执行唯一ID
    execute_uuid = uuid.uuid4().__str__()
    # 1.0 创建 该次执行对应的文件夹
    run_tmp_dir = os.path.join(cases_dir, execute_uuid)
    os.makedirs(run_tmp_dir, exist_ok=True)

    # 获取传入用例id
    data_id = int(request.json["id"])
    # 已删除多余的with语句
    # 根据id查询用用例信息
    web_info = module_model.query.filter_by(id=data_id).first()
    # 根据id查询用例下的步骤信息
    web_steps = WebInfoStep.query.order_by(WebInfoStep.run_order.asc()).filter_by(web_info_id=data_id).all()

    # 新增：用例的前置步骤信息
    pre_cases = WebInfoPre.query.order_by(WebInfoPre.run_order.asc()).filter_by(web_info_id=data_id).all()

    # 获取传入的浏览器id-查询浏览器全部信息
    browser_id = request.json["browser_id"]
    browser_info = WebBrowser.query.filter_by(id=browser_id).first()

    # 数据库查询, 附带当前项目的数据库信息-根据用例信息里的项目id查询项目下的数据库信息
    filter_list = []
    filter_list.append(WebDbBase.project_id == web_info.project_id)  # 当前项目
    filter_list.append(WebDbBase.is_enabled == "1")  # 是启动的状态
    db_infos = WebDbBase.query.filter(*filter_list).all()

    # 第一步： 组装 context.yaml 对应的信息
    test_case_config = {"_browser":{}, "_database":{}}

    # 0. 调试变量， 如果存在调试参数，则添加到 context 中-json字符串转python对象
    if web_info.param_data:
        for d in json.loads(web_info.param_data):
            test_case_config.update({d["key"]: d["value"]})

    # 1. 加载项目数据库配置信息保存到 context.yaml
    for db_info in db_infos:
       # test_case_config["_database"].update({db_info.ref_name: eval(db_info.db_info) })
       test_case_config["_database"].update({db_info.ref_name: json.loads(db_info.db_info)})

    # 2. 加载浏览器配置信息 (待完善)
    # config-2. 加载浏览器配置信息
    test_case_config.update({"_browser": {
        "grid_url": (browser_info.remote_url or "").strip(),
        "driver_path": (browser_info.driver_path or "").strip(),
        "capability": {"browserName": (browser_info.enName or "").strip()}}})

    # 当该字段有数据则进行对应的转换，否则是一个空字典
    browser_debug_val = (browser_info.browser_debug or "").strip()
    if len(browser_debug_val) > 0:
        # test_case_config["_browser"]["capability"].update(eval(browser_info.browser_debug))
        test_case_config["_browser"]["capability"].update(json.loads(browser_debug_val))

    # 生成yaml文件夹-将配置信息先生成yaml
    test_case_filename = f"context.yaml"
    test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
    # generate_yaml(test_case_config, test_case_yaml_file)
    with open(test_case_yaml_file, 'w', encoding='utf-8') as context_file:
        # yaml.dump将字典转为yaml格式字符串，写入context_file，default_flow_style=False代表数据的层级结构（换行）,allow_unicode代表允许输出yaml字符串中包含unicode字符
        yaml.dump(test_case_config, context_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

    # 填充测试用例信息
    test_case_data = {
        "desc": web_info.case_name,
        "steps": [], # 测试步骤
    }
    # 如果存在 前置脚本，则添加
    if web_info.pre_request:
        test_case_data["pre_script"] = []
        test_case_data["pre_script"].insert(0, web_info.pre_request)
    # 如果存在 后置脚本，则添加
    if web_info.post_request:
        test_case_data["post_script"] = []
        test_case_data["post_script"].insert(0, web_info.post_request)

    # 准备用例的存储文件
    case_file_name = uuid.uuid4()
    test_case_filename = f"{1}_{case_file_name}.yaml"
    test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)

    # 用例步骤的存储
    all_case_steps = []

    # 新增：遍历添加前置用例的步骤（只添加 is_enabled=True 的步骤）
    print("\n" + "=" * 60)
    print(f"🔍 开始加载前置用例步骤，共 {len(pre_cases)} 个前置用例")
    print("=" * 60)
    for idx, pre_info_data in enumerate(pre_cases, 1):
        print(f"\n📋 [{idx}/{len(pre_cases)}] 处理前置用例 ID: {pre_info_data.pre_info_id}, run_order: {pre_info_data.run_order}")
        
        # 查询前置用例的所有步骤
        pre_info_steps = WebInfoStep.query.order_by(WebInfoStep.run_order.asc()).filter_by(
            web_info_id=pre_info_data.pre_info_id).all()
        print(f"   查询到 {len(pre_info_steps)} 个步骤")
        
        # 筛选启用的步骤
        pre_enabled_steps = [step for step in pre_info_steps if step.is_enabled]
        pre_disabled_steps = [step for step in pre_info_steps if not step.is_enabled]
        
        # 打印筛选结果
        if pre_disabled_steps:
            disabled_info = "; ".join([f"步骤[{step.run_order}]：{step.step_desc}" for step in pre_disabled_steps])
            print(f"   ⏭️  过滤掉 {len(pre_disabled_steps)} 个未启用步骤：{disabled_info}")
        
        print(f"   ✅ 添加 {len(pre_enabled_steps)} 个启用的步骤到执行列表")
        all_case_steps.extend(pre_enabled_steps)
    
    print("=" * 60)
    print(f"✅ 前置用例步骤加载完成，共添加 {len(all_case_steps)} 个步骤")
    print("=" * 60 + "\n")

    # 原始代码：直接将所有步骤添加到执行列表
    # all_case_steps.extend(web_steps)
    # 优化后：只添加 is_enabled=True 的当前用例步骤
    print(f"🔍 开始加载当前用例步骤")
    filtered_steps = [step for step in web_steps if step.is_enabled]  # 筛选启用的步骤
    # 筛选被过滤掉的步骤（未启用的，用于打印日志）
    disabled_steps = [step for step in web_steps if not step.is_enabled]
    # 打印被过滤掉的步骤信息
    if disabled_steps:  # 只有存在被过滤的步骤时才打印
        # 用列表推导式拼接所有禁用步骤的描述和顺序，用分号分隔
        disabled_info = "; ".join([f"步骤顺序[{step.run_order}]：{step.step_desc}" for step in disabled_steps])
        print(f"==== 被过滤的未启用步骤：{disabled_info} ====")
    print(f"✅ 当前用例添加 {len(filtered_steps)} 个启用的步骤")
    all_case_steps.extend(filtered_steps)  # 仅添加筛选后的步骤
    
    print(f"\n📊 执行步骤汇总：前置用例步骤 + 当前用例步骤 = {len(all_case_steps)} 个步骤\n")

    # 遍历添加对应的测试步骤
    for web_step in all_case_steps:
        # 已删除多余的with语句
        # 获取对应的数据进行拼接
        apiKeyData = WebKeyWord.query.filter_by(id=web_step.key_word_id).first()
        stepData = {web_step.step_desc: {
            "关键字": apiKeyData.keyword_fun_name
        }}
        # 加载每个步骤中的参数配置，更新到步骤信息中
        stepData[web_step.step_desc].update(json.loads(web_step.ref_variable))
        test_case_data["steps"].append(stepData)

    with open(test_case_yaml_file, 'w', encoding='utf-8') as context_file:
        # yaml.dump将字典转为yaml格式字符串，写入context_file，default_flow_style=False代表数据的层级结构（换行）,allow_unicode代表允许输出yaml字符串中包含unicode字符
        yaml.dump(test_case_data, context_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

    # 文件生成后生成完毕后
    report_root_dir = current_app.config['WEB_REPORT_ROOT_DIR']  # 测试报告目录
    report_root_dir =  os.path.join(current_dir, report_root_dir) # 测试报告目录

    key_words_dir = current_app.config['KEY_WORDS_DIR']  # 关键字目录
    key_words_dir = os.path.join(current_dir, key_words_dir) # 关键字目录

    os.makedirs(report_root_dir, exist_ok=True)  # 创建目录

    report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data")  # 测试数据保存目录
    report_html_path = os.path.join(report_root_dir, execute_uuid)  # 测试html报告

    # 构建cli目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建 cli.py 文件的绝对路径i
    # cli_file_path = os.path.join(current_dir, '../tool/webrun/cli.py')
    WEB_CLI_DIR = current_app.config['WEB_CLI_DIR']
    cli_file_path = os.path.join(current_dir, WEB_CLI_DIR)

    # 设置给子进程的环境变量
    flask_env = os.getenv('FLASK_ENV', 'development')
    if flask_env == 'production':
        project_root = '/app'
    else:
        project_root = os.path.dirname(os.path.dirname(current_dir))
    os.environ["PYTHONPATH"] = f"{project_root}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
    env = os.environ
    remote_command = f'"{sys.executable}" "{cli_file_path}" --cases="{run_tmp_dir}" --keyDir="{key_words_dir}" -sv --capture=tee-sys --alluredir="{report_data_path}" 2>&1'
    subprocess_value = subprocess.check_output(remote_command, shell=True, universal_newlines=True, env=env)

    # 打印子进程输出中 AI 相关的日志
    print("[AI-DEBUG] === pytest 子进程 AI 日志开始 ===")
    for line in subprocess_value.split("\n"):
        s = line.strip()
        if s and any(kw in s for kw in ["AI", "模型", "豆包", "api_key", "api_base", "HTTP状态码", "响应内容", "OPENAI_API_KEY", "choices", "分解", "步骤", "坐标", "bbox", "判断", "断言", "提取", "滑动", "拖拽", "等待", "Error", "Traceback", "raise", "Exception", "__init__", "RuntimeError", "AttributeError", "ImportError", "TypeError"]):
            print(f"[AI-DEBUG] {s}")
    print("[AI-DEBUG] === pytest 子进程 AI 日志结束 ===")

    # 从 pytest 输出中匹配测试结果 -- 搜索 "= X failed, Y passed" 格式
    history_desc = ""
    for line in reversed(subprocess_value.split("\n")):
        if re.search(r'\d+\s*(failed|passed)', line):
            history_desc = line.replace("=", "").strip()
            break
    if not history_desc:
        # 降级：用最后一行
        history_desc = subprocess_value.split("\n")[-2].replace("=", "")

    # 匹配失败数量
    failed_match = re.search(r'(\d+)\s*failed', history_desc)
    failed_count = int(failed_match.group(1)) if failed_match else 0

    # 匹配通过数量
    passed_match = re.search(r'(\d+)\s*passed', history_desc)
    passed_count = int(passed_match.group(1)) if passed_match else 0

    # 总数
    num = int(failed_count + passed_count)
    if num == 0:
        # 解析失败，打印原始输出以便排查
        print("[AI-DEBUG] 无法解析pytest结果，原始输出最后3000字符:")
        print(subprocess_value[-3000:])
        num = 1  # 避免除零

    # 匹配执行总时间（格式：in 5.71s 或 in 1m20s 等）
    time_match = re.search(r'in\s*([\d.]+[smh]+)', history_desc)
    execution_time = time_match.group(1) if time_match else ""

    pass_rate = (passed_count / num) * 100
    pass_rate_str = f"{pass_rate:.2f}%"

    project_name = WebProject.query.get(web_info.project_id).project_name

    print(f"总数{num}")
    print(f"失败{failed_count}")
    print(f"通过{passed_count}")
    print(f"执行总时间: {execution_time}")
    print(f"通过率: {pass_rate_str}")
    if pass_rate_str == "100.00%":
        print("状态通过")
        state = "通过"
        color= "green"
    else:
        print("状态失败")
        state = "不通过"
        color= "red"


    # 2. 生成html测试报告
    decode_all_result_json_files(report_data_path)
    # 构建命令
    # allure_path = "/usr/local/bin/allure"  # 替换为你的实际路径
    WEB_ALLURE_DIR = current_app.config['WEB_ALLURE_DIR']
    allure_path = WEB_ALLURE_DIR  # 替换为你的实际路径

    command = f'allure generate "{report_data_path}" -c -o "{report_html_path}"'
    subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
    # os.system(f"allure generate {report_data_path} -c -o {report_html_path}")  # 等于你在命令行里面执行 allure
    print("当前的报告路径", report_html_path + "/index.html")
    # return respModel().ok_resp(msg="成功",obj=browser_info)
    report_url = build_public_report_url(execute_uuid)


    # 删除本次测试数据
    shutil.rmtree(run_tmp_dir)
    print("删除了测试数据:",run_tmp_dir)

    # 删除测试报告
    folder_cleanup_main(folder_path=report_root_dir)
    # 调用飞书报告
    webinfo_feishu(
    project = project_name,
    webcase = web_info.case_name,
    case_id = web_info.id,
    run_type = "手动调试",
    run_num = num,
    run_pass = passed_count,
    run_fail = failed_count,
    run_rate = pass_rate_str,
    run_time = execution_time,
    report_url = report_url,
    color=color,
    state=state,
    principal = web_info.principal
    )

    return respModel.ok_resp_text(data={"report_id":execute_uuid}, msg="执行成功")


import os
import re


def decode_all_result_json_files(folder_path):
    unicode_pattern = re.compile(r'\\u([0-9a-fA-F]{4})')

    def replace_unicode(match):
        code = match.group(1)
        return chr(int(code, 16))  # 十六进制转 Unicode 字符

    def decode(obj):
        if isinstance(obj, str):
            return unicode_pattern.sub(replace_unicode, obj)
        elif isinstance(obj, dict):
            return {k: decode(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [decode(item) for item in obj]
        return obj

    # 遍历文件夹
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith("-result.json"):  # 筛选目标文件
                file_path = os.path.join(root, file)
                try:
                    # 读取文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 解码 Unicode
                    decoded_data = decode(data)

                    # 写回文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(decoded_data, f, ensure_ascii=False, indent=2)

                    print(f"已处理文件: {file_path}")
                except Exception as e:
                    print(f"处理文件 {file_path} 失败: {e}")

# 复制
@module_route.route(f"/{module_name}/copyCase", methods=["POST"])
def copyCase():
    try:
        # 获取传入的值
        caseid = int(request.json["caseid"])
        newcasename = (request.json["newcasename"])
        # 验证传入的值是否存在用例
        # 已删除多余的with语句
        original_info = module_model.query.filter_by(id=caseid).first()
        if not original_info:
            return respModel.error_resp(msg="原测试用例不存在")
        # 构建新的用例数据
        new_info_data = {
            "id": None,  # 自增 ID
            "project_id": original_info.project_id,
            "case_name": newcasename,
            "case_desc": original_info.case_desc,
            "param_data": original_info.param_data,
            "pre_request": original_info.pre_request,
            "post_request": original_info.post_request,
            "is_pre": original_info.is_pre,
            "debug_info": original_info.debug_info,
            "create_time": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
        }
        # 创建用例
        new_info = module_model(** new_info_data)
        database.session.add(new_info)
        database.session.flush()  # 触发自增，获取新用例 ID
        new_info_id = new_info.id
        # database.session.commit()
        # 查询原用例关联的步骤
        original_steps = WebInfoStep.query.filter_by(web_info_id=caseid).all()
        if original_steps:
            for original_step in original_steps:
                # 构建新步骤数据（清空 id，关联新用例 ID）
                new_step_data = {
                    "id": None,
                    "web_info_id": new_info_id,
                    "key_word_id": original_step.key_word_id,
                    "step_desc": original_step.step_desc,
                    "ref_variable": original_step.ref_variable,
                    "run_order": original_step.run_order,
                    "create_time": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
                }
                new_step = WebInfoStep(** new_step_data)
                database.session.add(new_step)
        #提交总事务
        database.session.commit()
        return respModel.ok_resp(msg="复制成功{}".format(new_info_id))
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
