from flask import Blueprint, request
from core.resp_model import respModel
from extensions import database
from apitest.model.ApiTimeTaskModel import ApiTimeTask  # 修改导入的模型类
from datetime import datetime

# 模块信息
module_name = "ApiTimeTask"  # 模块名称
module_model = ApiTimeTask  # 修改为相应的模型类
module_route = Blueprint(f"route_{module_name}", __name__)

# 查询所有数据
@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    try:
        print("新增传值为:",request.json)
        # 分页数据获取
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # 数据库上下文
        # 数据库上下文
        # with application.app_context():
        # 定义一个筛选条件并向内添加筛选项
        filter_list = []
        # 获取任务名称-模糊筛选-get可以查询不到的时候不抛错
        task_name = request.json.get("task_name","")
        # 如果有值就加进筛选项
        if len(task_name) > 0:
            filter_list.append(module_model.task_name.like(f'%{task_name}%'))
        # 获取所属项目的值
        project_id = request.json.get("project_id",0)
        if type(project_id) is not str and project_id > 0:
            filter_list.append(module_model.project_id==project_id)
        # 获取集合的id-注意是数组
        collection_id = request.json.get("collection_id",[])
        if len(collection_id)>0:
            filter_list.append(module_model.collection_id.in_(collection_id))
        # 数据库查询
        print("筛选项为",filter_list)
        datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# 新增数据
@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    print("传值为:", request.json)
    try:
        # with application.app_context():
        # request.json["id"] =None
        data1 = request.json.copy()
        # 弹出不需要的字段
        data1.pop('collection_name', None)
        data1["id"] = None
        data = module_model(**data1, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        database.session.add(data)
        database.session.flush()
        data_id = data.id
        database.session.commit()
        return respModel.ok_resp(msg="添加成功",dic_t={"id":data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# 查询一条数据
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


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    print("修改传值为:", request.json)
    """ 修改数据 """
    try:
        # with application.app_context():
        # 根据传来的id查询数据，并且更新了用户的数据
        data1 = request.json.copy()
        # 弹出不需要的字段
        data1.pop('collection_name', None)
        module_model.query.filter_by(id=request.json["id"]).update(data1)
        # 完成更新的事务请求
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")