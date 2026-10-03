from flask import Blueprint, request

from core.auth_decocator import admin_required, jwt_required
from core.resp_model import respModel
from extensions import database
from sysmanage.model.user import User
from datetime import datetime

# 模块信息
module_name = "user"  # 模块名称
module_model = User
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
@admin_required
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        print("查看传入的类型====================")
        print(type(request.json))
        print("查看传入的类型====================")
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        
        filter_list = []
        datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
@admin_required
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        # 数据库查询
        data = module_model.query.filter_by(id = data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
@admin_required
def insert():
    """ 新增数据 """
    try:
        request.json["id"] = None # ID自增长
        # 自动设置 access_user_id 和 access_name
        if not request.json.get("access_user_id"):
            request.json["access_user_id"] = request.json.get("username", "")
        if not request.json.get("access_name"):
            request.json["access_name"] = request.json.get("username", "")
        data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        database.session.add(data)
        # 获取新增后的ID并返回
        database.session.flush()
        data_id = data.id
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
@admin_required
def update():
    """ 修改数据 """
    try:
        module_model.query.filter_by(id=request.json["id"]).update(request.json)
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
@admin_required
def delete():
    """ 删除数据 """
    try:
        from flask import g
        from sysmanage.model.user import User
        # 从 g.user_payload 获取访问的用户 access_user_id
        # jwt_payload 包含 access_user_id
        payload = getattr(g, 'user_payload', {})
        access_user_id = payload.get('access_user_id')
        
        current_user = User.query.filter_by(access_user_id=access_user_id).first()
        if not current_user or current_user.role != 'admin':
            return respModel.error_resp(msg="权限不足，仅管理员可删除用户")

        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.route(f"/{module_name}/queryAllCreateBy", methods=["GET"])
@jwt_required
def queryAllCreateBy():
    """查询所有用户列表，供负责人/创建人下拉使用"""
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "create_by": user.access_user_id or str(user.id),
            "create_name": user.access_name or user.username or f"用户{user.id}"
        })
    return respModel.ok_resp_simple(lst=result, msg="查询成功")
