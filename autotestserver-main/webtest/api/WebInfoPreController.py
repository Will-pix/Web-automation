from flask import Blueprint, request
from sqlalchemy import func
import json

from core.resp_model import respModel
from extensions import database
from webtest.model.WebInfoPreModel import WebInfoPre  # 修改导入的模型类
from datetime import datetime
# 其它模块
from webtest.model.WebInfoModel import WebInfo

# 模块信息
module_name = "WebInfoPre"  # 模块名称
module_model = WebInfoPre  # 修改为相应的模型类
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        project_id = request.json.get("project_id")

        filter_list = []
        # 添加模块名称模糊搜索条件
        # data_id = int(request.args.get("project_id"))
        # # 如果存在搜索值
        if project_id:
        #     # 列表追加模块名
            filter_list.append(module_model.project_id == project_id)
        #     filter_list.append(module_model.project_name.like(f'%{project_name}%'))
        datas = module_model.query.filter(*filter_list).order_by(module_model.create_time.desc()).limit(page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# 查询所有用例
@module_route.route(f"/{module_name}/queryByPagePre", methods=["POST"])
def queryByPagePre():
    """ 查询数据(支持模糊搜索) """
    try:
        filter_list = []
        # 增加可以通过collection_info_id进行筛选的条件
        web_info_id = request.json.get("webinfo_id", 0)
        if type(web_info_id) is not str and web_info_id > 0:
            filter_list.append(module_model.web_info_id == web_info_id)
        # 数据库查询- 按run_order升序
        datas = module_model.query.order_by(module_model.run_order.asc()).filter(*filter_list)
        results = []
        # 遍历所有的关联的测试用例
        for data in datas:
            # 1. 通过用例的编号查询到具体的信息
            pre_web_info_data = WebInfo.query.filter_by(id=data.pre_info_id).first()

            # 2. 合并子表和关联用例信息
            result = {}
            if pre_web_info_data:
                # 提取前置用例的字段，加pre_前缀，避免和当前用例/关联表字段冲突
                pre_info = respModel().get_custom_attributes(pre_web_info_data)
                for key, value in pre_info.items():
                    result[f"pre_{key}"] = value  # 如pre_case_name、pre_case_desc

                # 2. 合并关联表（WebInfoPre）的信息（保留原字段，不加前缀）
            web_info_pre_info = respModel().get_custom_attributes(data)
            result.update(web_info_pre_info)  # 保留web_info_id、pre_info_id、run_order等

            results.append(result)
        return respModel().ok_resp_simple_list(lst=results)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")



@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        # 数据库查询-修改为查询所属用例的id
        data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


# 新增
@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据：自动生成run_order（首次为1，后续取最大值+5） """
    try:
        # ========== 新增逻辑1：参数校验（必须传web_info_id） ==========
        # 1. 检查web_info_id是否传入
        if "web_info_id" not in request.json:
            return respModel.error_resp(msg="缺少必填参数：web_info_id")
        # 2. 校验web_info_id是否为有效整数
        try:
            web_info_id = int(request.json["web_info_id"])
            if web_info_id <= 0:
                return respModel.error_resp(msg="web_info_id必须为正整数")
        except ValueError:
            return respModel.error_resp(msg="web_info_id必须为整数类型")

        # ========== 新增逻辑2：自动计算run_order ==========
        # 1. 查询当前web_info_id对应的最大run_order（SQLAlchemy查询最大值）
        max_run_order = database.session.query(func.max(WebInfoPre.run_order)). \
            filter(WebInfoPre.web_info_id == web_info_id).scalar()
        # 2. 计算新的run_order：无数据则为1，有数据则最大值+5
        if max_run_order is None:  # 首次插入该web_info_id的数据
            new_run_order = 1
        else:
            new_run_order = max_run_order + 5

        # ========== 原有逻辑：构造数据（覆盖run_order） ==========
        request.json["id"] = None  # ID自增长
        # 覆盖前端传入的run_order（即使传了也不用，强制用后端计算的值）
        request.json["run_order"] = new_run_order
        # 构造模型实例（自动包含计算后的run_order）
        data = module_model(**request.json)

        # ========== 原有逻辑：提交事务 ==========
        database.session.add(data)
        database.session.flush()  # 刷新获取自增ID
        data_id = data.id

        database.session.commit()

        # ========== 新增逻辑：同步前置用例的 param_data 到当前用例 ==========
        print("\n" + "=" * 60)
        print("🔄 开始同步前置用例的 param_data (调试变量)")
        print("=" * 60)
        print(f"📦 完整请求参数: {request.json}")
        try:
            # 1. 检查前端是否传递了 pre_info_id
            pre_info_id = request.json.get("pre_info_id")
            print(f"📥 接收到的 pre_info_id: {pre_info_id} (类型: {type(pre_info_id)})")
            print(f"📥 接收到的 web_info_id: {web_info_id} (类型: {type(web_info_id)})")
            
            if pre_info_id:
                print(f"✅ pre_info_id 存在，开始查询前置用例...")
                
                # 2. 查询前置用例的 param_data
                pre_web_info = WebInfo.query.filter_by(id=pre_info_id).first()
                print(f"🔍 查询前置用例结果: {'找到' if pre_web_info else '未找到'}")
                
                if pre_web_info:
                    print(f"📄 前置用例信息 - ID: {pre_web_info.id}, 名称: {pre_web_info.case_name}")
                    print(f"📋 前置用例的 param_data: {pre_web_info.param_data}")
                    
                    if pre_web_info.param_data:
                        print(f"✅ 前置用例有 param_data，开始查询当前用例...")
                        
                        # 3. 查询当前用例
                        current_web_info = WebInfo.query.filter_by(id=web_info_id).first()
                        print(f"🔍 查询当前用例结果: {'找到' if current_web_info else '未找到'}")
                        
                        if current_web_info:
                            print(f"📄 当前用例信息 - ID: {current_web_info.id}, 名称: {current_web_info.case_name}")
                            print(f"📋 当前用例原 param_data: {current_web_info.param_data}")
                            
                            # 4. 将前置用例的 param_data 合并到当前用例（相同key覆盖，新key追加）
                            # 解析前置用例的 param_data
                            pre_params = json.loads(pre_web_info.param_data) if pre_web_info.param_data else []
                            print(f"🔍 解析前置用例参数: {pre_params}")
                            
                            # 解析当前用例的 param_data
                            current_params = json.loads(current_web_info.param_data) if current_web_info.param_data else []
                            print(f"🔍 解析当前用例参数: {current_params}")
                            
                            # 构建当前参数的 key->index 映射，用于快速查找和更新
                            current_key_index = {param.get("key"): idx for idx, param in enumerate(current_params)}
                            print(f"🔑 当前用例已有的 key: {set(current_key_index.keys())}")
                            
                            # 合并前置用例的参数
                            added_count = 0
                            updated_count = 0
                            for pre_param in pre_params:
                                pre_key = pre_param.get("key")
                                if pre_key in current_key_index:
                                    # key 已存在，更新值
                                    idx = current_key_index[pre_key]
                                    old_value = current_params[idx].get("value")
                                    current_params[idx] = pre_param
                                    updated_count += 1
                                    print(f"🔄 更新参数 [{pre_key}]: {old_value} → {pre_param.get('value')}")
                                else:
                                    # key 不存在，追加新参数
                                    current_params.append(pre_param)
                                    added_count += 1
                                    print(f"➕ 追加参数: {pre_param}")
                            
                            # 转回 JSON 字符串
                            current_web_info.param_data = json.dumps(current_params, ensure_ascii=False)
                            print(f"💾 合并后的 param_data: {current_web_info.param_data}")
                            print(f"📊 本次更新了 {updated_count} 个参数，追加了 {added_count} 个参数")
                            
                            database.session.commit()
                            print(f"✅ 同步成功！已将前置用例[{pre_info_id}]的调试变量追加到当前用例[{web_info_id}]")
                        else:
                            print(f"❌ 警告：未找到当前用例[{web_info_id}]")
                    else:
                        print(f"⚠️ 前置用例[{pre_info_id}]的 param_data 为空")
                else:
                    print(f"❌ 前置用例[{pre_info_id}]不存在")
            else:
                print(f"⏭️ 跳过同步：未传递 pre_info_id")
                
        except Exception as sync_error:
            # 同步失败不影响主流程，仅记录日志
            print(f"❌ 同步调试变量失败（不影响关联关系添加）：{sync_error}")
            import traceback
            print(f"📜 详细错误堆栈：\n{traceback.format_exc()}")
        finally:
            print("=" * 60)
            print("🔄 同步逻辑执行完毕\n")

        # ========== 恢复原有自动返回结构（仅返回id） ==========
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})

    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据：更新顺序和重新同步 param_data """
    try:
        # ========== 参数获取 ==========
        pre_id = request.json.get("pre_id")  # 前置依赖关联表的ID
        run_order = request.json.get("run_order")
        
        print("\n" + "=" * 60)
        print("🔄 WebInfoPre 更新接口")
        print("=" * 60)
        print(f"📦 接收参数: pre_id={pre_id}, run_order={run_order}")
        
        # ========== 参数校验 ==========
        if not pre_id:
            return respModel.error_resp(msg="缺少必填参数：id")
        if run_order is None:
            return respModel.error_resp(msg="缺少必填参数：run_order")
        
        # ========== 查询并更新关联记录 ==========
        pre_relation = module_model.query.filter_by(id=pre_id).first()
        if not pre_relation:
            return respModel.error_resp(msg=f"未找到前置依赖关系记录，ID: {pre_id}")
        
        print(f"✅ 找到前置依赖关系: ID={pre_relation.id}, web_info_id={pre_relation.web_info_id}, pre_info_id={pre_relation.pre_info_id}")
        
        # 只更新 run_order（依赖关系不变）
        old_run_order = pre_relation.run_order
        pre_relation.run_order = run_order
        print(f"🔄 更新 run_order: {old_run_order} → {run_order}")
        
        database.session.commit()
        print(f"💾 run_order 已更新")
        
        # ========== 复用创建逻辑：重新同步 param_data ==========
        print("\n" + "=" * 60)
        print("🔄 开始重新同步前置用例的 param_data (调试变量)")
        print("=" * 60)
        
        try:
            # 使用更新后的 pre_info_id 和 web_info_id
            current_pre_info_id = pre_relation.pre_info_id
            current_web_info_id = pre_relation.web_info_id
            
            print(f"📥 当前 pre_info_id: {current_pre_info_id}")
            print(f"📥 当前 web_info_id: {current_web_info_id}")
            
            if current_pre_info_id:
                print(f"✅ pre_info_id 存在，开始查询前置用例...")
                
                # 查询前置用例
                pre_web_info = WebInfo.query.filter_by(id=current_pre_info_id).first()
                print(f"🔍 查询前置用例结果: {'找到' if pre_web_info else '未找到'}")
                
                if pre_web_info:
                    print(f"📄 前置用例信息 - ID: {pre_web_info.id}, 名称: {pre_web_info.case_name}")
                    print(f"📋 前置用例的 param_data: {pre_web_info.param_data}")
                    
                    if pre_web_info.param_data:
                        print(f"✅ 前置用例有 param_data，开始查询当前用例...")
                        
                        # 查询当前用例
                        current_web_info = WebInfo.query.filter_by(id=current_web_info_id).first()
                        print(f"🔍 查询当前用例结果: {'找到' if current_web_info else '未找到'}")
                        
                        if current_web_info:
                            print(f"📄 当前用例信息 - ID: {current_web_info.id}, 名称: {current_web_info.case_name}")
                            print(f"📋 当前用例原 param_data: {current_web_info.param_data}")
                            
                            # 合并逻辑（相同key覆盖，新key追加）
                            pre_params = json.loads(pre_web_info.param_data) if pre_web_info.param_data else []
                            print(f"🔍 解析前置用例参数: {pre_params}")
                            
                            current_params = json.loads(current_web_info.param_data) if current_web_info.param_data else []
                            print(f"🔍 解析当前用例参数: {current_params}")
                            
                            current_key_index = {param.get("key"): idx for idx, param in enumerate(current_params)}
                            print(f"🔑 当前用例已有的 key: {set(current_key_index.keys())}")
                            
                            added_count = 0
                            updated_count = 0
                            for pre_param in pre_params:
                                pre_key = pre_param.get("key")
                                if pre_key in current_key_index:
                                    idx = current_key_index[pre_key]
                                    old_value = current_params[idx].get("value")
                                    current_params[idx] = pre_param
                                    updated_count += 1
                                    print(f"🔄 更新参数 [{pre_key}]: {old_value} → {pre_param.get('value')}")
                                else:
                                    current_params.append(pre_param)
                                    added_count += 1
                                    print(f"➕ 追加参数: {pre_param}")
                            
                            current_web_info.param_data = json.dumps(current_params, ensure_ascii=False)
                            print(f"💾 合并后的 param_data: {current_web_info.param_data}")
                            print(f"📊 本次更新了 {updated_count} 个参数，追加了 {added_count} 个参数")
                            
                            database.session.commit()
                            print(f"✅ 同步成功！已将前置用例[{current_pre_info_id}]的调试变量重新同步到当前用例[{current_web_info_id}]")
                        else:
                            print(f"❌ 警告：未找到当前用例[{current_web_info_id}]")
                    else:
                        print(f"⚠️ 前置用例[{current_pre_info_id}]的 param_data 为空")
                else:
                    print(f"❌ 前置用例[{current_pre_info_id}]不存在")
            else:
                print(f"⏭️ 跳过同步：pre_info_id 为空")
                
        except Exception as sync_error:
            print(f"❌ 重新同步调试变量失败（不影响顺序更新）：{sync_error}")
            import traceback
            print(f"📜 详细错误堆栈：\n{traceback.format_exc()}")
        finally:
            print("=" * 60)
            print("🔄 同步逻辑执行完毕\n")
        
        return respModel.ok_resp(msg="更新成功")
    except Exception as e:
        database.session.rollback()
        print(f"❌ 更新失败：{e}")
        import traceback
        print(f"📜 详细错误堆栈：\n{traceback.format_exc()}")
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        # with application.app_context():
            # 根据传来的id查询数据，并执行删除
        module_model.query.filter_by(id=request.args.get("id")).delete()
            # 确认数据库操作
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

# 新增代码内容：获取全部项目列表
# @module_route.route(f"/{module_name}/queryAll", methods=["GET"])
# def queryAll():
#     with application.app_context():
#         datas = module_model.query.all()
#         return respModel.ok_resp_list(lst=datas,msg="查询成功")