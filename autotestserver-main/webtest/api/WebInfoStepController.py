import json

from flask import Blueprint, request, g  # 导入g获取当前用户信息
from core.resp_model import respModel
from extensions import database
from webtest.model.WebInfoStepModel import WebInfoStep  # 子表模型
from webtest.model.WebInfoModel import WebInfo  # 父表模型（新增导入）
from datetime import datetime

# 扩展模块
from webtest.model.WebOperationTypeModel import OperationType
from webtest.model.WebKeyWordModel import WebKeyWord

# 模块信息
module_name = "WebInfoStep"  # 模块名称
module_model = WebInfoStep  # 子表模型
module_route = Blueprint(f"route_{module_name}", __name__)


# 查询完整下拉列表
@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    datas = module_model.query.all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        filter_list = []
        web_info_id = request.json.get("web_info_id", 0)
        if type(web_info_id) is not str and web_info_id > 0:
            filter_list.append(module_model.web_info_id == web_info_id)
        datas = module_model.query.order_by(module_model.run_order.asc()).filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
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
    """ 新增数据：同时更新父级WebInfo的修改人/时间 """
    try:
        # 1. 获取当前用户信息（从g变量中提取）
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "未知")
        current_user_name = user_payload.get("access_name", "未知用户")

        # 2. 新增子表WebInfoStep
        request.json["id"] = None  # ID自增长
        step_data = module_model(** request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        database.session.add(step_data)
        database.session.flush()  # 刷新获取step_data的web_info_id
        data_id = step_data.id

        # 3. 更新父级WebInfo的修改人/时间
        web_info_id = step_data.web_info_id  # 从子表数据中获取父级ID
        web_info = WebInfo.query.filter_by(id=web_info_id).first()
        if web_info:
            web_info.update_time = datetime.now()
            web_info.update_by = current_user_id
            web_info.update_name = current_user_name

        # 4. 提交事务
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据：同时更新父级WebInfo的修改人/时间 """
    try:
        # 1. 获取当前用户信息
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "未知")
        current_user_name = user_payload.get("access_name", "未知用户")

        # 2. 更新子表WebInfoStep
        update_data = request.json
        target_data = module_model.query.filter_by(id=update_data["id"]).first()
        if target_data:
            for key, value in update_data.items():
                if key != "id":
                    setattr(target_data, key, value)

        # 3. 更新父级WebInfo的修改人/时间
        web_info_id = target_data.web_info_id  # 从子表实例中获取父级ID
        web_info = WebInfo.query.filter_by(id=web_info_id).first()
        if web_info:
            web_info.update_time = datetime.now()
            web_info.update_by = current_user_id
            web_info.update_name = current_user_name

        # 4. 提交事务
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        database.session.rollback()
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据：同时更新父级WebInfo的修改人/时间 """
    try:
        # 1. 获取当前用户信息
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "未知")
        current_user_name = user_payload.get("access_name", "未知用户")

        # 2. 获取要删除的子表数据，提取父级ID
        step_id = request.args.get("id")
        step_data = module_model.query.filter_by(id=step_id).first()
        if not step_data:
            return respModel.error_resp(msg="子步骤数据不存在")
        web_info_id = step_data.web_info_id  # 父级ID

        # 3. 删除子表数据
        database.session.delete(step_data)

        # 4. 更新父级WebInfo的修改人/时间
        web_info = WebInfo.query.filter_by(id=web_info_id).first()
        if web_info:
            web_info.update_time = datetime.now()
            web_info.update_by = current_user_id
            web_info.update_name = current_user_name

        # 5. 提交事务
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        database.session.rollback()
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")