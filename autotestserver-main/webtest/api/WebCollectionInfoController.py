import re
import shutil
import sys

from flask import Blueprint, request, g, current_app  # 导入g获取用户信息
from core.resp_model import respModel
from extensions import database
# from app import application
from webtest.api.clear_report import folder_cleanup_main
from webtest.api.feishu_report import collection_feishu, collection_feishu_time
from platformconfig.service.runtime_store import build_public_report_url
from webtest.model.WebCollectionInfoModel import WebCollectionInfo  # 修改导入的模型类
from datetime import datetime

from webtest.model.WebProjectModel import WebProject
from webtest.model.WebTimeTaskModel import WebTimeTask  # 导入定时任务模型

module_name = "WebCollectionInfo"  # 模块名称
module_model = WebCollectionInfo
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # 已删除多余的with语句
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

        collection_env_type = request.json.get("collection_env_type")  # 前端转环境，不传则不筛选
        if collection_env_type:
            filter_list.append(module_model.collection_env_type == collection_env_type)

        # =====结束
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
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据：修正为实例化更新，触发基类before_update """
    try:
        # 已删除多余的with语句
        update_data = request.json
        # 先查实例，再赋值（触发基类时间更新）
        target_data = module_model.query.filter_by(id=update_data["id"]).first()
        if target_data:
            for key, value in update_data.items():
                if key != "id":  # 排除主键
                    setattr(target_data, key, value)
        
        # 同步更新定时任务表的collection_env_type
        if "collection_env_type" in update_data:
            collection_id = update_data["id"]
            new_env_type = update_data["collection_env_type"]
            
            # 查找所有关联的定时任务
            time_tasks = WebTimeTask.query.filter_by(collection_id=collection_id).all()
            
            # 更新每个定时任务的collection_env_type（如果不同）
            for task in time_tasks:
                if task.collection_env_type != new_env_type:
                    task.collection_env_type = new_env_type
        
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据  删除的同时，需要处理掉中间表"""
    try:
        # 已删除多余的with语句
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

# 扩展接口 - 执行用例接口
# 这里开始远程调用逻辑，生成两个文件夹,文件夹名字用UUID为后缀
import json, os, subprocess, uuid, yaml
# 模块信息,依次导入的包
from webtest.model.WebBrowserModel import WebBrowser
from webtest.model.WebDbBaseModel import WebDbBase
from webtest.model.WebCollectionDetailModel import WebCollectionDetail
from webtest.model.WebInfoModel import WebInfo
from webtest.model.WebInfoStepModel import WebInfoStep
from webtest.model.WebKeyWordModel import WebKeyWord
from webtest.model.WebHistoryModel import WebHistoryModel
from webtest.model.WebInfoPreModel import WebInfoPre
from webtest.model.WebHistoryTimeModel import WebHistoryTimeModel

@module_route.route(f"/{module_name}/excuteTest", methods=["POST"])
def excuteTest():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    session = database.session
    # 获取配置中指定的 临时文件生成地址
    cases_dir = current_app.config['CASES_ROOT_WEB_DIR']
    cases_dir = os.path.join(current_dir, cases_dir)

    # 该次执行唯一ID
    execute_uuid = uuid.uuid4().__str__()
    # 1.0 创建 该次执行对应的文件夹
    run_tmp_dir = os.path.join(cases_dir, execute_uuid)
    os.makedirs(run_tmp_dir, exist_ok=True)

    try:
        # 获取执行类型
        run_type_value = request.json.get("run_type","手动调试")
        # 获取测试计划ID
        data_id = int(request.json["id"])
        # 已删除多余的with语句（视图接口在请求上下文内）
        # 1. 测试计划信息
        web_collection_info = module_model.query.filter_by(id=data_id).first()

        # 2. 测试计划 执行对应的浏览器的数据
        browser_info = WebBrowser.query.filter_by(id=web_collection_info.browser_id).first()

        # 3. 数据库查询, 附带当前项目的数据库信息
        filter_list = []
        filter_list.append(WebDbBase.project_id == web_collection_info.project_id)  # 当前项目
        filter_list.append(WebDbBase.is_enabled == "1")  # 是启动的状态
        db_infos = WebDbBase.query.filter(*filter_list).all()

        # 第一步： 组装 context.yaml 对应的信息
        test_case_config = {"_browser":{}, "_database":{}}
        # 0. 环境变量， 如果存在，则添加到 context 中
        if web_collection_info.collection_env:
            for d in json.loads(web_collection_info.collection_env):
                test_case_config.update({d["key"]: d["value"]})

        # 1. 加载项目数据库配置信息保存到 context.yaml
        for db_info in db_infos:
           test_case_config["_database"].update({db_info.ref_name: json.loads(db_info.db_info) })

        # 2. 加载浏览器配置信息 (待完善)
        test_case_config.update({"_browser": {
                                              "grid_url": (browser_info.remote_url or "").strip(),
                                              "driver_path": (browser_info.driver_path or "").strip(),
                                              "capability": {"browserName": (browser_info.enName or "").strip()}
                                              }
                                 })

        # 当该字段有数据则进行对应的转换，否则是一个空字典
        browser_debug_val = (browser_info.browser_debug or "").strip()
        if len(browser_debug_val) > 0:
            test_case_config["_browser"]["capability"].update(json.loads(browser_debug_val))

        # 生成context.yaml文件夹
        test_case_filename = f"context.yaml"
        test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
        with open(test_case_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_case_config, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)

        # 第二步： 生成每一步的测试用例信息
        # 已删除多余的with语句
        # 数据库查询,用来接收当前 Collection关联的对应的测试用例
        case_infos = WebCollectionDetail.query.order_by(WebCollectionDetail.run_order.asc()).filter_by(collection_info_id=data_id).all()

        # 2.1 遍历每一个用例，生成对应的 yaml文件
        for case_info in case_infos:
            # 测试用例信息
            case_file_name = uuid.uuid4()
            test_case_filename = f"{case_info.run_order}_{case_file_name}.yaml"
            test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)

            # 已删除多余的with语句
            # 数据库查询 WebInfo
            web_info = WebInfo.query.filter_by(id=case_info.web_info_id).first()
            # 数据库查询,用来接收当前 WebInfo的测试步骤
            web_steps = WebInfoStep.query.order_by(WebInfoStep.run_order.asc()).filter_by(
                web_info_id=case_info.web_info_id).all()
            
            # 新增：查询前置用例列表
            pre_cases = WebInfoPre.query.order_by(WebInfoPre.run_order.asc()).filter_by(
                web_info_id=case_info.web_info_id).all()

            # 填充测试用例信息 - 基本格式
            test_case_data = {
                "desc": web_info.case_name,
                "steps": [],  # 测试步骤
                "context": {
                    "_case_id": web_info.id,  # 传递用例ID
                    "_case_principal": web_info.principal if web_info.principal else "无"  # 传递负责人
                }
            }

            # 2.1.0 DDT数据驱动信息
            ddt_datas = json.loads(case_info.ddt_param_data)
            if len(ddt_datas) > 0 : test_case_data["ddts"] = [] # 如果有数据则填充
            for ddt_data in ddt_datas:
                d = {}
                for data in ddt_data:
                    d.update({data["key"]: data["value"]})
                test_case_data["ddts"].append(d)

            # 2.1.1 前后置脚本信息
            if web_info.pre_request:
                test_case_data["pre_script"] = []
                test_case_data["pre_script"].insert(0,web_info.pre_request)
            if web_info.post_request:
                test_case_data["post_script"] = []
                test_case_data["post_script"].insert(0,web_info.post_request)

            # 2.1.2 测试步骤
            all_case_steps = []
            
            # 新增：遍历添加前置用例的步骤（只添加 is_enabled=True 的步骤）
            print("\n" + "=" * 60)
            print(f"🔍 用例[{web_info.case_name}] 开始加载前置用例步骤，共 {len(pre_cases)} 个前置用例")
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
            
            # 优化后：只添加 is_enabled=True 的当前用例步骤
            print(f"🔍 用例[{web_info.case_name}] 开始加载当前用例步骤")
            filtered_steps = [step for step in web_steps if step.is_enabled]
            disabled_steps = [step for step in web_steps if not step.is_enabled]
            if disabled_steps:
                disabled_info = "; ".join([f"步骤顺序[{step.run_order}]：{step.step_desc}" for step in disabled_steps])
                print(f"==== 被过滤的未启用步骤：{disabled_info} ====")
            print(f"✅ 当前用例添加 {len(filtered_steps)} 个启用的步骤")
            all_case_steps.extend(filtered_steps)
            
            print(f"\n📊 用例[{web_info.case_name}] 执行步骤汇总：前置用例步骤 + 当前用例步骤 = {len(all_case_steps)} 个步骤\n")

            # 遍历测试步骤，生成 执行器需要的格式数据
            for web_step in all_case_steps:
                # 已删除多余的with语句
                # 获取对应的数据进行拼接
                keyWordData = WebKeyWord.query.filter_by(id=web_step.key_word_id).first()
                stepData = {web_step.step_desc: {
                    "关键字": keyWordData.keyword_fun_name
                }}
                # 加载每个步骤中的参数配置，更新到步骤信息中
                stepData[web_step.step_desc].update(json.loads(web_step.ref_variable))
                test_case_data["steps"].append(stepData)

            # 生成用例yaml文件
            with open(test_case_yaml_file, 'w', encoding='utf-8') as test_case_yaml_file:
                yaml.dump(test_case_data, test_case_yaml_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

        # 文件生成后生成完毕后，获取配置目录
        report_root_dir = current_app.config['WEB_REPORT_ROOT_DIR']  # 测试报告目录
        report_root_dir = os.path.join(current_dir, report_root_dir)

        key_words_dir = current_app.config['KEY_WORDS_DIR']  # 关键字目录
        key_words_dir = os.path.join(current_dir, key_words_dir)

        # 绝对文件位置-数据-报告
        os.makedirs(report_root_dir, exist_ok=True)
        report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data")  # 测试数据保存目录
        report_html_path = os.path.join(report_root_dir, execute_uuid)  # 测试html报告

        # 构建cli目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        WEB_CLI_DIR = current_app.config['WEB_CLI_DIR']  # 关键字目录
        cli_file_path = os.path.join(current_dir, WEB_CLI_DIR)


        # 执行记录
        collection_state_add(web_collection_info.id)
        # 执行结果
        collection_run_result_update(web_collection_info.id,2)


        # 设置给子进程的环境变量
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            project_root = '/app'
        else:
            project_root = os.path.dirname(os.path.dirname(current_dir))
        os.environ["PYTHONPATH"] = f"{project_root}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
        env = os.environ
        remote_command = f'"{sys.executable}" "{cli_file_path}" --cases="{run_tmp_dir}" --keyDir="{key_words_dir}" -vv -rA --capture=tee-sys --alluredir="{report_data_path}" '
        command_output = subprocess.check_output(remote_command, shell=True, universal_newlines=True, env=env)
        history_desc = command_output.split("\n")[-2].replace("=", "") # 截取最后一段

        # 打印 AI 相关日志
        print("[AI-DEBUG] === pytest 子进程 AI 日志开始 ===")
        for line in command_output.split("\n"):
            s = line.strip()
            if s and any(kw in s for kw in ["AI", "模型", "豆包", "api_key", "api_base", "HTTP状态码", "响应内容", "OPENAI_API_KEY", "choices", "分解", "步骤", "坐标", "bbox", "判断", "断言", "提取", "滑动", "拖拽", "等待", "Error", "error", "Traceback"]):
                print(f"[AI-DEBUG] {s}")
        print("[AI-DEBUG] === pytest 子进程 AI 日志结束 ===")
        print("执行信息:", convert_unicode_by_re(command_output))

        print("执行信息结束")

        # 调用函数处理所有 JSON 文件
        decode_all_result_json_files(report_data_path)
        
        # 从Allure result.json中提取用例执行结果
        allure_results = parse_allure_results(report_data_path)
        print(f"[DEBUG] Allure解析结果 - 通过: {len(allure_results['passed'])} 个, 失败: {len(allure_results['failed'])} 个")
        
        print("remote_command值：",execute_uuid)
        # print("command_output值：",command_output)
        print("history_desc值：",history_desc)

        # 匹配失败数量
        failed_match = re.search(r'(\d+)\s*failed', history_desc)
        failed_count = int(failed_match.group(1)) if failed_match else 0

        # 匹配通过数量
        passed_match = re.search(r'(\d+)\s*passed', history_desc)
        passed_count = int(passed_match.group(1)) if passed_match else 0

        # 总数
        num = int(failed_count+passed_count)

        # 执行时长
        time_match = re.search(r'in\s*([\d.]+[smh]+)', history_desc)
        execution_time = time_match.group(1) if time_match else ""

        # 通过率
        pass_rate = (passed_count / num) * 100
        pass_rate_str = f"{pass_rate:.2f}%"

        # 项目名
        project_name = WebProject.query.get(web_collection_info.project_id).project_name

        print(f"总数{num}")
        print(f"失败{failed_count}")
        print(f"通过{passed_count}")
        print(f"执行总时间: {execution_time}")
        print(f"通过率: {pass_rate_str}")
        if pass_rate_str == "100.00%":
            print("状态通过")
            state = "通过"
            color = "green"
        else:
            print("状态失败")
            state = "不通过"
            color = "red"

        # ========== 关键修改：从Allure结果中提取用例详情 ==========
        # 直接使用从 allure result.json 中解析的数据（包含准确的case_id）
        failed_cases_detail = []
        pass_cases_detail = []
        
        # 数据一致性检查
        if failed_count > 0 and not allure_results["failed"]:
            print(f"[WARNING] 数据不一致：pytest显示{failed_count}个失败，但Allure结果中没有失败用例！")
            print(f"[WARNING] 可能原因：用例状态为broken或Allure JSON文件解析失败")
        
        # 处理失败用例
        if failed_count > 0 and allure_results["failed"]:
            print("\n" + "=" * 50 + " 失败用例详情 " + "=" * 50)
            for idx, case_info in enumerate(allure_results["failed"], 1):
                failed_cases_detail.append({
                    "case_name": case_info["case_name"],
                    "case_id": case_info["case_id"],
                    "principal": case_info["principal"]
                })
                print(f"\n{idx}. 用例名：{case_info['case_name']}")
                print(f"   用例ID：{case_info['case_id']}")
                print(f"   负责人：{case_info['principal']}")
            print("\n" + "=" * 106)
        
        # 处理通过用例
        if passed_count > 0 and allure_results["passed"]:
            print("\n" + "=" * 50 + " 通过用例详情 " + "=" * 50)
            for idx, case_info in enumerate(allure_results["passed"], 1):
                pass_cases_detail.append({
                    "case_name": case_info["case_name"],
                    "case_id": case_info["case_id"],
                    "principal": case_info["principal"]
                })
                print(f"\n{idx}. 用例名：{case_info['case_name']}")
                print(f"   用例ID：{case_info['case_id']}")
                print(f"   负责人：{case_info['principal']}")
            print("\n" + "=" * 106)
        # ========== 用例详情提取结束 ===========

        # 组合返回
        history_desc = "总数:{},通过{},失败{}".format(num, passed_count, failed_count)

        # 2. 生成html测试报告
        WEB_ALLURE_DIR = current_app.config['WEB_ALLURE_DIR']  # 关键字目录
        allure_path = WEB_ALLURE_DIR  # 替换为你的实际路径

        command = f'allure generate "{report_data_path}" -c -o "{report_html_path}"'
        subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print("当前的报告路径", report_html_path + "/index.html")

        report_url = build_public_report_url(execute_uuid)

        # 删除本次测试数据
        shutil.rmtree(run_tmp_dir)
        print("删除了测试数据:", run_tmp_dir)

        # 删除测试报告
        folder_cleanup_main(folder_path=report_root_dir)

        print("failed_cases_detail:",failed_cases_detail)
        # 调用飞书报告
        collection_feishu(
            project=project_name,
            collection=web_collection_info.collection_name,
            collection_id=web_collection_info.id,
            run_type=run_type_value,
            run_num=num,
            run_pass=passed_count,
            run_fail=failed_count,
            run_rate=pass_rate_str,
            run_time=execution_time,
            report_url=report_url,
            color=color,
            state=state,
            principal=web_collection_info.principal,
            # 用例部分信息
            # 关键修改：传递统一的结构化失败用例信息列表（替代零散字段）
            failed_cases = failed_cases_detail,
            collection_env_type=web_collection_info.collection_env_type

        )

        collection_state_close(web_collection_info.id)
        # 执行结果
        if pass_rate_str == "100.00%":
            collection_run_result_update(web_collection_info.id, 1)
        else:
            collection_run_result_update(web_collection_info.id, 0)
        # 记录结果
        # 已删除多余的with语句
        # 存储执行，id，集合id，简述，报告id，时间
        report = WebHistoryModel(collection_info_id=data_id, history_desc=history_desc,collection_env_type=web_collection_info.collection_env_type,
                                 history_detail=execute_uuid,collection_principal=web_collection_info.principal,failed_cases_detail=json.dumps(failed_cases_detail, ensure_ascii=False),
                                 pass_cases_detail=json.dumps(pass_cases_detail, ensure_ascii=False),
                                 run_time=execution_time,
                                 create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        session.add(report)
        session.commit()
        return respModel.ok_resp_text(data={"data": history_desc}, msg="执行成功")

    except Exception as e:
        print(e)
        collection_state_close(web_collection_info.id)
        collection_run_result_update(web_collection_info.id, 0)
        session.rollback()
        return respModel.error_resp(msg=f"执行出现错误：{e}")


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


def parse_allure_results(folder_path):
    """
    解析Allure result.json文件，提取用例执行结果
    返回：{"passed": [{case_id, case_name, principal}], "failed": [{case_id, case_name, principal}]}
    """
    passed_cases = []
    failed_cases = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith("-result.json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 获取执行状态
                    status = data.get("status", "unknown")
                    # 获取标签中的case_id、case_principal和case_name
                    labels = data.get("labels", [])
                    case_id = "未知"
                    case_principal = "无"
                    case_name = None  # 优先从label中获取
                    for label in labels:
                        if label.get("name") == "case_id":
                            case_id = label.get("value", "未知")
                        elif label.get("name") == "case_principal":
                            case_principal = label.get("value", "无")
                        elif label.get("name") == "case_name":
                            case_name = label.get("value")
                    
                    # 如果label中没有case_name，则从name字段获取（回退方案）
                    if not case_name:
                        case_name = data.get("name", "未知")
                    
                    case_info = {
                        "case_id": case_id,
                        "case_name": case_name,
                        "principal": case_principal
                    }
                    
                    # 质量大盘只分两类：通过和失败
                    if status == "passed":
                        passed_cases.append(case_info)
                    else:
                        # 除通过外，所有状态都算失败（包括：failed、broken、skipped等）
                        failed_cases.append(case_info)
                        print(f"[DEBUG] 失败用例: {case_name}, ID: {case_id}, 状态: {status}")
                        
                except Exception as e:
                    print(f"[ERROR] 解析文件 {file_path} 失败: {e}")
                    import traceback
                    traceback.print_exc()
    
    print(f"[DEBUG] parse_allure_results 完成 - 通过: {len(passed_cases)}, 失败: {len(failed_cases)}")
    return {"passed": passed_cases, "failed": failed_cases}


def excuteTest_run(collection_id,inform_value,task):
    # 保留所有with语句：该函数是定时任务调用（非请求场景），需手动创建上下文
    from app import application
    with application.app_context():
        print("执行了excuteTest_run")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        session = database.session
        # 获取配置中指定的 临时文件生成地址
        cases_dir = current_app.config['CASES_ROOT_WEB_DIR']
        cases_dir = os.path.join(current_dir, cases_dir)

        execute_uuid = uuid.uuid4().__str__()
        # 1.0 创建 该次执行对应的文件夹
        run_tmp_dir = os.path.join(cases_dir, execute_uuid)
        os.makedirs(run_tmp_dir, exist_ok=True)

        try:
            # 获取测试计划ID
            from app import application
            with application.app_context():
                # 1. 测试计划信息
                web_collection_info = module_model.query.filter_by(id=collection_id).first()

                # 2. 测试计划 执行对应的浏览器的数据
                browser_info = WebBrowser.query.filter_by(id=web_collection_info.browser_id).first()

                # 3. 数据库查询, 附带当前项目的数据库信息
                filter_list = []
                filter_list.append(WebDbBase.project_id == web_collection_info.project_id)  # 当前项目
                filter_list.append(WebDbBase.is_enabled == "1")  # 是启动的状态
                db_infos = WebDbBase.query.filter(*filter_list).all()

            # 第一步： 组装 context.yaml 对应的信息
            test_case_config = {"_browser":{}, "_database":{}}
            # 0. 环境变量， 如果存在，则添加到 context 中
            if web_collection_info.collection_env:
                for d in json.loads(web_collection_info.collection_env):
                    test_case_config.update({d["key"]: d["value"]})

            # 1. 加载项目数据库配置信息保存到 context.yaml
            for db_info in db_infos:
               test_case_config["_database"].update({db_info.ref_name: json.loads(db_info.db_info) })

            # 2. 加载浏览器配置信息 (待完善)
            test_case_config.update({"_browser": {
                                                  "grid_url": (browser_info.remote_url or "").strip(),
                                                  "driver_path": (browser_info.driver_path or "").strip(),
                                                  "capability": {"browserName": (browser_info.enName or "").strip()}
                                                  }
                                     })

            # 当该字段有数据则进行对应的转换，否则是一个空字典
            browser_debug_val = (browser_info.browser_debug or "").strip()
            if len(browser_debug_val) > 0:
                test_case_config["_browser"]["capability"].update(json.loads(browser_debug_val))

            # 生成context.yaml文件夹
            test_case_filename = f"context.yaml"
            test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
            with open(test_case_yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(test_case_config, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)

            # 第二步： 生成每一步的测试用例信息
            from app import application
            with application.app_context():
                # 数据库查询,用来接收当前 Collection关联的对应的测试用例
                case_infos = WebCollectionDetail.query.order_by(WebCollectionDetail.run_order.asc()).filter_by(collection_info_id=collection_id).all()

            # 2.1 遍历每一个用例，生成对应的 yaml文件
            for case_info in case_infos:
                # 测试用例信息
                case_file_name = uuid.uuid4()
                test_case_filename = f"{case_info.run_order}_{case_file_name}.yaml"
                test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)

                from app import application
                with application.app_context():
                    # 数据库查询 WebInfo
                    web_info = WebInfo.query.filter_by(id=case_info.web_info_id).first()
                    # 数据库查询,用来接收当前 WebInfo的测试步骤
                    web_steps = WebInfoStep.query.order_by(WebInfoStep.run_order.asc()).filter_by(
                        web_info_id=case_info.web_info_id).all()
                    
                    # 新增：查询前置用例列表
                    pre_cases = WebInfoPre.query.order_by(WebInfoPre.run_order.asc()).filter_by(
                        web_info_id=case_info.web_info_id).all()

                # 填充测试用例信息 - 基本格式
                test_case_data = {
                    "desc": web_info.case_name,
                    "steps": [],  # 测试步骤
                    "context": {
                        "_case_id": web_info.id,  # 传递用例ID
                        "_case_principal": web_info.principal if web_info.principal else "无"  # 传递负责人
                    }
                }

                # 2.1.0 DDT数据驱动信息
                ddt_datas = json.loads(case_info.ddt_param_data)
                if len(ddt_datas) > 0 : test_case_data["ddts"] = [] # 如果有数据则填充
                for ddt_data in ddt_datas:
                    d = {}
                    for data in ddt_data:
                        d.update({data["key"]: data["value"]})
                    test_case_data["ddts"].append(d)

                # 2.1.1 前后置脚本信息
                if web_info.pre_request:
                    test_case_data["pre_script"] = []
                    test_case_data["pre_script"].insert(0,web_info.pre_request)
                if web_info.post_request:
                    test_case_data["post_script"] = []
                    test_case_data["post_script"].insert(0,web_info.post_request)

                # 2.1.2 测试步骤
                all_case_steps = []
                
                # 新增：遍历添加前置用例的步骤（只添加 is_enabled=True 的步骤）
                print("\n" + "=" * 60)
                print(f"🔍 用例[{web_info.case_name}] 开始加载前置用例步骤，共 {len(pre_cases)} 个前置用例")
                print("=" * 60)
                for idx, pre_info_data in enumerate(pre_cases, 1):
                    print(f"\n📋 [{idx}/{len(pre_cases)}] 处理前置用例 ID: {pre_info_data.pre_info_id}, run_order: {pre_info_data.run_order}")
                    
                    from app import application
                    with application.app_context():
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
                
                # 优化后：只添加 is_enabled=True 的当前用例步骤
                print(f"🔍 用例[{web_info.case_name}] 开始加载当前用例步骤")
                filtered_steps = [step for step in web_steps if step.is_enabled]
                disabled_steps = [step for step in web_steps if not step.is_enabled]
                if disabled_steps:
                    disabled_info = "; ".join([f"步骤顺序[{step.run_order}]：{step.step_desc}" for step in disabled_steps])
                    print(f"==== 被过滤的未启用步骤：{disabled_info} ====")
                print(f"✅ 当前用例添加 {len(filtered_steps)} 个启用的步骤")
                all_case_steps.extend(filtered_steps)
                
                print(f"\n📊 用例[{web_info.case_name}] 执行步骤汇总：前置用例步骤 + 当前用例步骤 = {len(all_case_steps)} 个步骤\n")

                # 遍历测试步骤，生成 执行器需要的格式数据
                for web_step in all_case_steps:
                    from app import application
                    with application.app_context():
                        # 获取对应的数据进行拼接
                        keyWordData = WebKeyWord.query.filter_by(id=web_step.key_word_id).first()
                        stepData = {web_step.step_desc: {
                            "关键字": keyWordData.keyword_fun_name
                        }}
                        # 加载每个步骤中的参数配置，更新到步骤信息中
                        stepData[web_step.step_desc].update(json.loads(web_step.ref_variable))
                        test_case_data["steps"].append(stepData)

                # 生成用例yaml文件
                with open(test_case_yaml_file, 'w', encoding='utf-8') as test_case_yaml_file:
                    yaml.dump(test_case_data, test_case_yaml_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

            # 文件生成后生成完毕后，获取配置目录
            report_root_dir = application.config['WEB_REPORT_ROOT_DIR']  # 测试报告目录
            report_root_dir = os.path.join(current_dir, report_root_dir)

            key_words_dir = application.config['KEY_WORDS_DIR']  # 关键字目录
            key_words_dir = os.path.join(current_dir, key_words_dir)

            # 绝对文件位置-数据-报告
            os.makedirs(report_root_dir, exist_ok=True)
            report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data")  # 测试数据保存目录
            report_html_path = os.path.join(report_root_dir, execute_uuid)  # 测试html报告

            # 构建cli目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            WEB_CLI_DIR = application.config['WEB_CLI_DIR']
            cli_file_path = os.path.join(current_dir, WEB_CLI_DIR)

            # 设置给子进程的环境变量
            flask_env = os.getenv('FLASK_ENV', 'development')
            if flask_env == 'production':
                project_root = '/app'
            else:
                project_root = os.path.dirname(os.path.dirname(current_dir))
            os.environ["PYTHONPATH"] = f"{project_root}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
            env = os.environ
            remote_command = f'"{sys.executable}" "{cli_file_path}" --cases="{run_tmp_dir}" --keyDir="{key_words_dir}" -vv -rA --capture=tee-sys --alluredir="{report_data_path}" '
            command_output = subprocess.check_output(remote_command, shell=True, universal_newlines=True, env=env)
            history_desc = command_output.split("\n")[-2].replace("=", "") # 截取最后一段

            # 打印 AI 相关日志
            for line in command_output.split("\n"):
                if any(kw in line for kw in ["[AI配置]", "分解的步骤为", "豆包返回值", "豆包精准值", "模型未能获取成功", "模型返回滑动", "模型返回等待", "判断核心逻辑", "用户指令中提取", "拖拽操作返回", "ui-tars模型", "断言不通过", "每次的步骤是"]):
                    print(f"[AI-DEBUG] {line.strip()}")

            # 调用函数处理所有 JSON 文件
            decode_all_result_json_files(report_data_path)
            
            # 从Allure result.json中提取用例执行结果
            allure_results = parse_allure_results(report_data_path)
            print(f"[DEBUG] Allure解析结果 - 通过: {len(allure_results['passed'])} 个, 失败: {len(allure_results['failed'])} 个")
            
            print("remote_command值：",execute_uuid)
            print("command_output值：",command_output)
            print("history_desc值：",history_desc)

            # 匹配失败数量
            failed_match = re.search(r'(\d+)\s*failed', history_desc)
            failed_count = int(failed_match.group(1)) if failed_match else 0

            # 匹配通过数量
            passed_match = re.search(r'(\d+)\s*passed', history_desc)
            passed_count = int(passed_match.group(1)) if passed_match else 0

            # 总数
            num = int(failed_count+passed_count)

            # 项目名
            project_name = WebProject.query.get(web_collection_info.project_id).project_name

            # 通过率
            pass_rate = (passed_count / num) * 100
            pass_rate_str = f"{pass_rate:.2f}%"

            # 执行时长
            time_match = re.search(r'in\s*([\d.]+[smh]+)', history_desc)
            execution_time = time_match.group(1) if time_match else ""

            print(f"总数{num}")
            print(f"失败{failed_count}")
            print(f"通过{passed_count}")
            print(f"执行总时间: {execution_time}")
            print(f"通过率: {pass_rate_str}")
            if pass_rate_str == "100.00%":
                print("状态通过")
                state = "通过"
                color = "green"
            else:
                print("状态失败")
                state = "不通过"
                color = "red"

            # ========== 关键修改：从Allure结果中提取用例详情 ==========
            # 直接使用从 allure result.json 中解析的数据（包含准确的case_id）
            failed_cases_detail = []
            pass_cases_detail = []
            
            # 数据一致性检查
            if failed_count > 0 and not allure_results["failed"]:
                print(f"[WARNING] 数据不一致：pytest显示{failed_count}个失败，但Allure结果中没有失败用例！")
                print(f"[WARNING] 可能原因：用例状态为broken或Allure JSON文件解析失败")
            
            # 处理失败用例
            if failed_count > 0 and allure_results["failed"]:
                print("\n" + "=" * 50 + " 失败用例详情 " + "=" * 50)
                for idx, case_info in enumerate(allure_results["failed"], 1):
                    failed_cases_detail.append({
                        "case_name": case_info["case_name"],
                        "case_id": case_info["case_id"],
                        "principal": case_info["principal"]
                    })
                    print(f"\n{idx}. 用例名：{case_info['case_name']}")
                    print(f"   用例ID：{case_info['case_id']}")
                    print(f"   负责人：{case_info['principal']}")
                print("\n" + "=" * 106)
            
            # 处理通过用例
            if passed_count > 0 and allure_results["passed"]:
                print("\n" + "=" * 50 + " 通过用例详情 " + "=" * 50)
                for idx, case_info in enumerate(allure_results["passed"], 1):
                    pass_cases_detail.append({
                        "case_name": case_info["case_name"],
                        "case_id": case_info["case_id"],
                        "principal": case_info["principal"]
                    })
                    print(f"\n{idx}. 用例名：{case_info['case_name']}")
                    print(f"   用例ID：{case_info['case_id']}")
                    print(f"   负责人：{case_info['principal']}")
                print("\n" + "=" * 106)
            # ========== 用例详情提取结束 ==========

            # 组合返回
            history_desc = "总数:{},通过{},失败{}".format(num, passed_count, failed_count)

            # 2. 生成html测试报告
            WEB_ALLURE_DIR = application.config['WEB_ALLURE_DIR']  # 关键字目录
            allure_path = WEB_ALLURE_DIR  # 替换为你的实际路径

            command = f'allure generate "{report_data_path}" -c -o "{report_html_path}"'
            subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print("当前的报告路径", report_html_path + "/index.html")

            report_url = build_public_report_url(execute_uuid)

            # 删除本次测试数据
            shutil.rmtree(run_tmp_dir)
            print("删除了测试数据:", run_tmp_dir)

            # 删除测试报告
            folder_cleanup_main(folder_path=report_root_dir)

            # 调用飞书报告
            collection_feishu_time(
                project=project_name,
                collection=web_collection_info.collection_name,
                collection_id=web_collection_info.id,
                run_type="定时任务",
                run_num=num,
                run_pass=passed_count,
                run_fail=failed_count,
                run_rate=pass_rate_str,
                run_time=execution_time,
                report_url=report_url,
                color=color,
                state=state,
                principal=web_collection_info.principal,
                inform_value= inform_value,
                # 关键修改：传递统一的结构化失败用例信息列表（替代零散字段）
                failed_cases = failed_cases_detail,
                collection_env_type=web_collection_info.collection_env_type
            )

            # 记录结果
            with application.app_context():
                # 存储执行，id，集合id，简述，报告id，时间
                report = WebHistoryTimeModel(collection_info_id=collection_id, task_id=task.id,history_desc=history_desc,collection_env_type=web_collection_info.collection_env_type,
                                         history_detail=execute_uuid,collection_principal=web_collection_info.principal,failed_cases_detail=json.dumps(failed_cases_detail, ensure_ascii=False),
                                            pass_cases_detail=json.dumps(pass_cases_detail, ensure_ascii=False),
                                            run_time=execution_time,
                                                create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
                session.add(report)
                session.commit()
            if failed_count == 0:
                return respModel.ok_resp_text(data={"data": history_desc}, msg="执行结束，测试成功")
            else:
                return respModel.ok_resp_text(data={"data": history_desc}, msg="执行结束，测试失败")

        except Exception as e:
            print(e)
            return respModel.error_resp(msg=f"执行出现错误：{e}")


from webtest.model.WebExecutingState import WebExecutingState  # 导入对应的模型
from extensions import database


# 添加执行状态记录（state固定为1，无返回值）
def collection_state_add(collection_id):
    try:
        # 查找是否存在相同collection_id的记录
        existing_record = WebExecutingState.query.filter_by(collection_id=collection_id).first()

        if existing_record:
            # 存在则更新state为1
            existing_record.state = 1
        else:
            # 不存在则创建新记录，state设为1
            new_record = WebExecutingState(
                collection_id=collection_id,
                state=1
            )
            database.session.add(new_record)

        database.session.commit()  # 提交事务

    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(f"collection_state_add 写入失败: {e}")  # 仅打印错误日志


# 关闭执行状态记录（state固定为2，无返回值）
def collection_state_close(collection_id):
    try:
        # 查找是否存在相同collection_id的记录
        existing_record = WebExecutingState.query.filter_by(collection_id=collection_id).first()

        if existing_record:
            # 存在则更新state为2
            existing_record.state = 2
        else:
            # 不存在则创建新记录，state设为2
            new_record = WebExecutingState(
                collection_id=collection_id,
                state=2
            )
            database.session.add(new_record)

        database.session.commit()  # 提交事务

    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(f"collection_state_close 写入失败: {e}")  # 仅打印错误日志


# 更新执行结果（根据传入的result更新run_result，0=失败、1=通过、2=进行中）
def collection_run_result_update(collection_id, result):
    try:
        # 查找是否存在相同collection_id的记录
        existing_record = WebExecutingState.query.filter_by(collection_id=collection_id).first()

        if existing_record:
            # 存在则更新run_result为传入的result
            existing_record.run_result = result
        else:
            # 不存在则创建新记录，run_result设为传入的result
            new_record = WebExecutingState(
                collection_id=collection_id,
                run_result=result,
                # 若需要默认值，可补充state字段（例如默认0，根据业务场景调整）
                # state=0
            )
            database.session.add(new_record)

        database.session.commit()  # 提交事务

    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(f"collection_run_result_update 写入失败: {e}")  # 打印错误日志

# 正则处理中文
import re
def convert_unicode_by_re(text):
    """用正则直接替换 \\uXXXX 为中文，不涉及 JSON 解析"""  # 这里把\u改成\\u
    if not text:
        return text
    # 匹配所有 \uXXXX 格式的 Unicode 转义字符（注意这里也要用\\u）
    unicode_pattern = re.compile(r'\\u([0-9a-fA-F]{4})')
    # 替换为对应的中文字符
    text = unicode_pattern.sub(lambda m: chr(int(m.group(1), 16)), text)
    return text

# pytest信息打印处理
def get_failure_details(output):
    """
    从pytest输出中提取失败用例的详情（用例名 + 错误信息）
    修复：过滤PASSES区域，只处理FAILURES区域的失败用例
    :param output: 处理后的command_output字符串（已转换中文）
    :return: 列表，每个元素是字典：{'case_name': 用例名, 'error_msg': 错误信息}
    """
    failure_details = []
    lines = output.split('\n')
    current_case = None  # 记录当前失败的用例名
    current_error = []   # 记录当前用例的错误信息
    # 正则匹配用例名（匹配 TestRunner.test_case_execute[用例B-1] 中的「用例B-1」）
    case_pattern = re.compile(r'TestRunner\.test_case_execute\[(.+?)\]')
    # 标记是否进入失败详情区域（pytest的FAILURES部分）
    in_failure_section = False
    # 标记是否进入通过用例区域（需要跳过）
    in_pass_section = False

    for line in lines:
        line_stripped = line.strip()
        # 1. 进入失败详情区域
        if '=================== FAILURES ===================' in line:
            in_failure_section = True
            in_pass_section = False  # 重置通过区域标记
            continue
        # 2. 进入通过用例区域（需要跳过）
        if '==================== PASSES ====================' in line:
            in_pass_section = True
            in_failure_section = False  # 退出失败区域
            continue
        # 3. 离开所有详情区域（到short test summary info部分）
        if '=========================== short test summary info ============================' in line:
            break
        # 4. 跳过通过区域的内容
        if in_pass_section:
            continue
        # 5. 只处理失败区域的内容
        if not in_failure_section:
            continue

        # 6. 匹配到失败用例的名称
        case_match = case_pattern.search(line_stripped)
        if case_match:
            # 如果有上一个用例的错误信息，先保存
            if current_case and current_error:
                failure_details.append({
                    'case_name': current_case,
                    'error_msg': '\n'.join(current_error).strip()
                })
            # 更新当前用例名，重置错误信息
            current_case = case_match.group(1)
            current_error = []
            continue
        # 7. 收集失败用例的错误信息（仅当有当前用例且在失败区域时）
        if current_case and line_stripped:
            # 过滤掉无用的分隔行和无关信息
            if not (line_stripped.startswith('_____________________') or
                    line_stripped.startswith('-----------------------------') or
                    line_stripped.startswith('webtest/') and line_stripped.endswith('.py:') or
                    line_stripped.startswith('self = <') or  # 过滤掉对象信息行
                    line_stripped.startswith('caseinfo = {')):  # 过滤掉用例信息行
                current_error.append(line_stripped)
    # 处理最后一个失败用例的错误信息
    if current_case and current_error:
        failure_details.append({
            'case_name': current_case,
            'error_msg': '\n'.join(current_error).strip()
        })
    return failure_details

# 用例名提取
def get_pure_case_name(case_name_with_suffix):
    """
    提取纯用例名，过滤掉pytest添加的后缀数字
    支持三种格式：
    1. 带 "-数字" 后缀（DDT格式）：用例B-1 → 用例B
    2. 纯数字结尾（pytest自动添加）：测试平台-添加葱能-online-线上账号1 → 测试平台-添加葱能-online-线上账号
    3. 无后缀：直接返回
    
    :param case_name_with_suffix: 带后缀的用例名
    :return: 纯用例名（原始用例名）
    """
    if not case_name_with_suffix:
        return ""
    
    case_name = case_name_with_suffix.strip()
    
    # 策略1: 优先匹配 "-数字" 格式的后缀（DDT格式，最常见）
    match = re.match(r'^(.+)-\d+$', case_name)
    if match:
        return match.group(1).strip()
    
    # 策略2: 匹配末尾纯数字的情况（处理pytest自动添加的后缀）
    # 例如：测试平台-添加葱能-online-线上账号1 → 测试平台-添加葱能-online-线上账号
    # 由于前端已禁止用例名以数字结尾，这里匹配的一定是pytest自动添加的后缀
    match = re.match(r'^(.+?)(\d+)$', case_name)
    if match:
        pure_name = match.group(1).strip()
        if pure_name:  # 只要去除数字后不为空就返回
            return pure_name
    
    # 若没有匹配到任何后缀，直接返回原名称
    return case_name

import re

# pytest信息打印处理-正确
def get_pass_details(output):
    """
    从pytest输出中提取通过用例的详情（用例名）
    逻辑与失败用例提取一致，仅处理PASSES区域的通过用例
    :param output: 处理后的command_output字符串（已转换中文）
    :return: 列表，每个元素是字典：{'case_name': 用例名}
    """
    pass_details = []
    lines = output.split('\n')
    # 正则匹配用例名（和失败用例使用相同的匹配规则）
    case_pattern = re.compile(r'TestRunner\.test_case_execute\[(.+?)\]')
    # 标记是否进入通过详情区域（pytest的PASSES部分）
    in_pass_section = False
    # 标记是否进入失败详情区域（需要跳过）
    in_failure_section = False

    for line in lines:
        line_stripped = line.strip()
        # 1. 进入通过详情区域
        if '==================== PASSES ====================' in line:
            in_pass_section = True
            in_failure_section = False
            continue
        # 2. 进入失败详情区域（需要跳过）
        if '=================== FAILURES ===================' in line:
            in_failure_section = True
            in_pass_section = False
            continue
        # 3. 离开所有详情区域（到summary部分）
        if '=========================== short test summary info ============================' in line:
            break
        # 4. 跳过失败区域和非通过区域的内容
        if in_failure_section or not in_pass_section:
            continue

        # 5. 匹配到通过用例的名称
        case_match = case_pattern.search(line_stripped)
        if case_match:
            pass_details.append({
                'case_name': case_match.group(1)
            })
    return pass_details
