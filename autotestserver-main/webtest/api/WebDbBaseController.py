from flask import Blueprint, request
from core.resp_model import respModel
from extensions import database
from webtest.model.WebDbBaseModel import WebDbBase  # 修改导入的模型类
from datetime import datetime

# 模块信息
module_name = "WebDbBase"  # 模块名称
module_model = WebDbBase  # 修改为相应的模型类
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
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

@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
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
        # 为了获取数据库的上下文
        # 为了防止前端带有id参数，先清空
        request.json["id"] = None # ID自增长
        # 如果当前的ref_name已存在，不能添加数据
        ref_name = request.json["ref_name"]
        data_refname = module_model.query.filter_by(ref_name=ref_name).first()
        if data_refname:
            return respModel.error_resp(msg=f"添加失败:已存在引用变量名")
        # 将前端传来的数据与新增的时间放入data
        data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        # 将data交给database管理
        database.session.add(data)
        # 实际向数据库进行了交互，插入了数据并生成了id，此时data已经有了id，但是事务没有完成等待确认
        database.session.flush()
        # data已经存在了id，提取出来准备返回给前端
        data_id = data.id
        # 最终确认数据库事务，完成了插入动作
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        # 根据传来的id查询数据，并且更新了用户的数据
        module_model.query.filter_by(id=request.json["id"]).update(request.json)
        # 完成更新的事务请求
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
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