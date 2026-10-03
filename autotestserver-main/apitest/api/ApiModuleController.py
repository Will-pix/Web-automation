from flask import Blueprint, request
from core.resp_model import respModel
from extensions import database
from apitest.model.ApiModuleModel import ApiModule
from datetime import datetime

# 模块信息
module_name = "ApiModule"  # 模块名称
module_model = ApiModule
module_route = Blueprint(f"route_{module_name}", __name__)

# 根据条件查询数据，如果没有条件查询全部
@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        # 前段传递的分页参数
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # with application.app_context():
        filter_list = []
        # 添加 项目筛选条件
        # 传递的项目id
        project_id = request.json.get("project_id", 0)
        # 如果项目id不是字符串且大于0时执行
        # project_id = int(project_id)
        if type(project_id) is not str and project_id > 0:
            # 列表追加传递进来的项目id
            filter_list.append(module_model.project_id==project_id)
        # 添加模块名称模糊搜索条件
        module_name = request.json.get("module_name", "")
        # 如果存在搜索值
        if len(module_name) > 0 :
            # 列表追加模块名
            filter_list.append(module_model.module_name.like(f'%{module_name}%'))
        # 数据库查询
        # 此时filter_list是，项目id+模块名称
        datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# 根据id查询数据
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

# 新增一条数据
@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
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
        error_msg = str(e)
        if "1366" in error_msg:
            return respModel.error_resp(msg="新增失败：需要选择项目")
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")

# 修改数据
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

# 删除数据
@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        # with application.app_context():
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
