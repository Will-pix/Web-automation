from flask import Blueprint, request, g
from core.resp_model import respModel
from extensions import database
from datetime import datetime
from webtest.model.WebTimeTaskModel import WebTimeTask

# 模块信息
module_name = "WebTimeTask"  # 模块名称
module_model = WebTimeTask  # 模型类
module_route = Blueprint(f"route_{module_name}", __name__)


# 查询分页数据
@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    try:
        print("新增传值为:", request.json)
        # 分页数据获取
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # 已删除多余的with语句（视图函数自带上下文）
        # 定义筛选条件
        filter_list = []
        # 任务名称模糊筛选
        task_name = request.json.get("task_name", "")
        if len(task_name) > 0:
            filter_list.append(module_model.task_name.like(f'%{task_name}%'))
        # 所属项目筛选
        project_id = request.json.get("project_id", 0)
        if type(project_id) is not str and project_id > 0:
            filter_list.append(module_model.project_id == project_id)
        # 集合ID筛选（数组）
        collection_id = request.json.get("collection_id", [])
        if len(collection_id) > 0:
            filter_list.append(module_model.collection_id.in_(collection_id))

        # 3. 新增条件1：按创建人ID查询（精确匹配，ID无需模糊）
        create_by = request.json.get("create_by")  # 前端传创建人ID，不传则不筛选
        if create_by:
            filter_list.append(module_model.create_by == create_by)

        # 4. 新增条件2：按修改人ID查询（精确匹配）
        update_by = request.json.get("update_by")  # 前端传修改人ID，不传则不筛选
        if update_by:
            filter_list.append(module_model.update_by == update_by)

        # 5. 新增条件3：按环境查询（精确匹配）
        collection_env_type = request.json.get("collection_env_type")  # 前端转环境，不传则不筛选
        if collection_env_type:
            filter_list.append(module_model.collection_env_type == collection_env_type)

        # 数据库查询
        print("筛选项为", filter_list)
        datas = module_model.query.filter(*filter_list).order_by(module_model.create_time.desc()).limit(page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


# 新增数据：手动填充创建人、修改人信息
@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    print("传值为:", request.json)
    try:
        # 1. 获取当前用户信息（从g变量中提取）
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "系统")
        current_user_name = user_payload.get("access_name", "系统")

        # 2. 处理请求数据
        data1 = request.json.copy()
        data1.pop('collection_name', None)
        data1["id"] = None

        # 3. 手动赋值通用字段（替代基类自动填充）
        now = datetime.now()
        data = module_model(
            **data1,
            create_time=now,  # 创建时间
            update_time=now,  # 新增时，更新时间与创建时间一致
            create_by=current_user_id,  # 创建人ID
            create_name=current_user_name,  # 创建人名称
            update_by=current_user_id,  # 新增时，修改人ID与创建人一致
            update_name=current_user_name  # 新增时，修改人名称与创建人一致
        )

        # 4. 提交数据
        database.session.add(data)
        database.session.flush()
        data_id = data.id
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        database.session.rollback()
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")



# 查询单条数据
@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        # 已删除多余的with语句
        data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


# 删除数据
@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        # 已删除多余的with语句
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


# 修改数据：手动更新修改人、修改时间信息
@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    print("修改传值为:", request.json)
    # 在 insert 或 update 接口的 try 块最开始添加
    # print("=== 打印 g 变量所有值 ===")
    # print(g.__dict__)  # __dict__ 会返回 g 中所有已设置的属性和对应值
    # print("=== g 变量打印结束 ===")
    try:
        # 1. 获取当前用户信息
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "系统")
        current_user_name = user_payload.get("access_name", "系统")

        # 2. 处理请求数据
        data1 = request.json.copy()
        data1.pop('collection_name', None)
        target_id = request.json["id"]

        # 3. 查询目标实例并更新
        target_data = module_model.query.filter_by(id=target_id).first()
        if target_data:
            # 更新业务字段
            for key, value in data1.items():
                if key != "id":
                    setattr(target_data, key, value)
            # 手动更新通用字段（替代基类自动填充）
            target_data.update_time = datetime.now()  # 更新时间
            target_data.update_by = current_user_id  # 修改人ID
            target_data.update_name = current_user_name  # 修改人名称

        # 4. 提交事务
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        database.session.rollback()
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")