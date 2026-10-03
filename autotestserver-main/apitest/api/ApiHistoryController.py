import os

from flask import Blueprint, request, current_app
from core.resp_model import respModel
from extensions import database
from datetime import datetime
from apitest.model.ApiHistoryModel import ApiHistoryModel
from flask import send_from_directory


# 模块信息
module_name = "ApiHistory"  # 模块名称
module_model = ApiHistoryModel  # 请根据您的模型类进行调整
module_route = Blueprint(f"route_{module_name}", __name__)

# 返回报告
@module_route.route('/ApiHistory/<path:dir>/<filename>',methods=["GET"])
def uploaded_file(dir, filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    report_root_dir = current_app.config['REPORT_ROOT_DIR']
    report_root_dir = os.path.join(current_dir, report_root_dir)

    return send_from_directory(f"{report_root_dir}/{dir}/", filename)

# 查询数据
@module_route.route(f"/ApiHistory/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索)-倒叙 """
    pass
    try:
        # 分页数据
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # 数据库上下文
        # 数据库上下文
        # with application.app_context():
            # 组装查询条件
        filter_list = []
        # 获取传入的集合id
        collection_id = request.json.get("collection_id", 0)
        # 如果集合id不是字符串并且大于0
        if type(collection_id) is not str and collection_id >0:
            # 添加进查询条件-向数据库查询集合id与传递的集合id是一一致的（比较表达式生成波尔值）
            filter_list.append(module_model.collection_id==collection_id)
        # 数据库查询-如果*filter_list不成立就查询所有记录，成立就查询指定测试集的记录
        datas = module_model.query.filter(*filter_list).order_by(module_model.create_time.desc()).limit(page_size).offset((page -1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        if datas:
            return respModel().ok_resp_list(lst=datas, total=total)
        else:
            # return respModel.ok_resp(msg="查询成功，但是没有数据")
            return respModel.ok_resp_list(msg="查询成功，但是没有数据")

    except Exception as e:
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
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
        data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        # with application.app_context():
        database.session.add(data)
        database.session.commit()
        return respModel.ok_resp(msg="添加成功")
    except Exception as e:
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
    """ 删除数据 """
    try:
        # with application.app_context():
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")