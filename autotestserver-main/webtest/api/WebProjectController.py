from flask import Blueprint, request
from core.resp_model import respModel
from extensions import database
from sysmanage.model.user import User
from webtest.model.WebProjectModel import WebProject  # 修改导入的模型类

# 模块信息
module_name = "WebProject"  # 模块名称
module_model = WebProject  # 修改为相应的模型类
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        filter_list = []
        # 2. 原有条件：项目名称模糊查询（保留）
        project_name = request.json.get("project_name", "")
        if project_name:  # 有值才加过滤条件
            filter_list.append(module_model.project_name.like(f'%{project_name}%'))

        # 3. 新增条件1：按创建人ID查询（精确匹配，ID无需模糊）
        create_by = request.json.get("create_by")  # 前端传创建人ID，不传则不筛选
        if create_by:
            filter_list.append(module_model.create_by == create_by)

        # 4. 新增条件2：按修改人ID查询（精确匹配）
        update_by = request.json.get("update_by")  # 前端传修改人ID，不传则不筛选
        if update_by:
            filter_list.append(module_model.update_by == update_by)

        # 5. 执行查询（原有逻辑不变，filter_list自动包含所有筛选条件）
        datas = module_model.query.filter(*filter_list).order_by(module_model.create_time.desc()).limit(
            page_size).offset((page - 1) * page_size).all()
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
    """ 新增数据：完全不用管通用字段，基类自动处理 """
    try:
        request.json["id"] = None  # 仅保留ID置空（自增长）
        # 👇 只传业务字段（project_name/project_desc），其他全靠基类
        data = module_model(**request.json)
        database.session.add(data)
        database.session.flush()
        data_id = data.id
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(f"添加失败:{e}")

@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据：仅传业务字段+ID即可 """
    try:
        update_data = request.json  # 只包含project_name/project_desc/id
        # 正确的更新方式（实例化更新）
        data = module_model.query.filter_by(id=update_data["id"]).first()  # 先查实例
        if data:
            # 逐个修改属性（或用setattr批量赋值）
            for key, value in update_data.items():
                if key != "id":  # 排除id（主键通常不修改）
                    setattr(data, key, value)
        # module_model.query.filter_by(id=update_data["id"]).update(update_data)
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"修改失败，请联系管理员:{e}")

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
@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    datas = module_model.query.all()
    print(datas)
    return respModel.ok_resp_list(lst=datas,msg="查询成功")


# @module_route.route(f"/{module_name}/queryAllCreateBy", methods=["GET"])
# def queryAllCreateBy():
#     datas = (
#         module_model.query
#         # .with_entities(module_model.create_by, module_model.create_name)  # 只保留这两个字段
#         .filter(module_model.create_by.isnot(None))  # 过滤空值
#         .distinct(module_model.create_by)  # 按 create_by 去重
#         .all()
#     )
#     # 1. 先创建一个空列表
#     result = []
#     # 2. 再循环遍历datas里的每个元素（item就是每次循环拿到的WebProject实例）
#     for item in datas:
#         # 3. 每次循环，创建一个字典（装create_by和create_name）
#         temp_dict = {
#             "create_by": item.create_by,  # 从实例取create_by
#             "create_name": item.create_name  # 从实例取create_name
#         }
#         # 4. 把字典加到空列表里
#         result.append(temp_dict)
#     return respModel.ok_resp_simple(lst=result,msg="查询成功")
#
#
# @module_route.route(f"/{module_name}/queryAllUpdateBy", methods=["GET"])
# def queryAllUpdateBy():
#     datas = (
#         module_model.query
#         .filter(module_model.update_by.isnot(None))  # 过滤空值
#         .distinct(module_model.update_by)  # 按 create_by 去重
#         .all()
#     )
#     # 1. 先创建一个空列表
#     result = []
#     # 2. 再循环遍历datas里的每个元素（item就是每次循环拿到的WebProject实例）
#     for item in datas:
#         # 3. 每次循环，创建一个字典（装create_by和create_name）
#         temp_dict = {
#             "update_by": item.update_by,  # 从实例取create_by
#             "update_name": item.update_name  # 从实例取create_name
#         }
#         # 4. 把字典加到空列表里
#         result.append(temp_dict)
#     return respModel.ok_resp_simple(lst=result, msg="查询成功")