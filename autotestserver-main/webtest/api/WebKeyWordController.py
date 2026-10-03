import os
from flask import Blueprint, request, current_app
from core.resp_model import respModel
from extensions import database
from webtest.model.WebKeyWordModel import WebKeyWord  # 请替换为你的ApiModule模型类
from datetime import datetime

# 模块信息
module_name = "WebKeyWord"  # 模块名称
module_model = WebKeyWord
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    # 已删除多余的with语句
    datas = module_model.query.all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # 已删除多余的with语句
        filter_list = []
        # 添加关键字描述搜索条件
        name = request.json.get("name", "")
        if len(name) > 0:
            filter_list.append(module_model.name.like(f'%{name}%'))
        # 添加操作类型进行查询
        operation_type_id = request.json.get("operation_type_id", 0)
        if type(operation_type_id) is not str and operation_type_id > 0:
            filter_list.append(module_model.operation_type_id == operation_type_id)

        # 添加页面筛选条件
        page_id = request.json.get("page_id", 0)
        if type(page_id) is not str and page_id > 0:
            filter_list.append(module_model.page_id == page_id)

        # 4. 新增条件1：按创建人ID筛选（精确匹配，前端传值才加）
        create_by = request.json.get("create_by")
        if create_by:
            filter_list.append(module_model.create_by == create_by)
        #
        # # 5. 新增条件2：按修改人ID筛选（精确匹配，前端传值才加）
        update_by = request.json.get("update_by")  # 前端传修改人ID，不传则不筛选
        if update_by:
            filter_list.append(module_model.update_by == update_by)

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


# @module_route.route(f"/{module_name}/insert", methods=["POST"])
# def insert():
#     """ 新增数据 """
#     try:
#         request.json["id"] = None  # ID自增长
#         data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
#         database.session.add(data)
#         # 获取新增后的ID并返回
#         database.session.flush()
#         data_id = data.id
#         database.session.commit()
#         return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
#     except Exception as e:
#         print(e)
#         return respModel.error_resp(msg=f"添加失败:{e}")


# @module_route.route(f"/{module_name}/update", methods=["PUT"])
# def update():
#     """ 修改数据 """
#     try:
#         module_model.query.filter_by(id=request.json["id"]).update(request.json)
#         database.session.commit()
#         return respModel.ok_resp(msg="修改成功")
#     except Exception as e:
#         print(e)
#         return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        # 已删除多余的with语句
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


#  -------------扩展或者修改接口-------------------

#  修改新增接口，当keyword_fun_name 在数据库存在则不能添加
@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        # 已删除多余据的with语句
        # 确定关键字唯一
        request.json["id"] = None  # ID自增长
        keyword_fun_name = request.json["keyword_fun_name"]  # 关键字名获取

        # 进行查询确定是否有关键字数据
        data = module_model.query.filter_by(keyword_fun_name=keyword_fun_name).first()

        if data:
            # 如果有数据则提示用户：关键字重复
            return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入。")
        else:
            data = module_model(** request.json,
                                create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            database.session.commit()
            return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")


#  更新接口，当keyword_fun_name 在数据库存在则不能修改为它
@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        # 已删除多余的with语句
        keyword_fun_name = request.json["keyword_fun_name"]  # 关键字名获取
        keyword_id = request.json["id"]  # id获取,更新的是当前的数据、查询的也是这个数据，则过滤
        # 进行查询确定是否有关键字数据
        data = module_model.query.filter_by(keyword_fun_name=keyword_fun_name).first()

        if data and (data.id != keyword_id):
            # 如果有数据则提示用户：关键字重复
            return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入。")
        else:
            # 修正更新方式：先查实例再赋值，确保触发基类before_update
            update_data = request.json
            target_data = module_model.query.filter_by(id=update_data["id"]).first()
            if target_data:
                for key, value in update_data.items():
                    if key != "id":  # 排除主键
                        setattr(target_data, key, value)
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


# 生成关键字文件
@module_route.route(f"/{module_name}/keywordFile", methods=["POST"])
def keywordFile():
    try:
        # 已删除多余的with语句
        file_name = request.json["keyword_fun_name"]  # 方法名
        keyword_value = request.json["keyword_value"]  # 方法体

        current_dir = os.path.dirname(os.path.abspath(__file__))
        key_words_dir = current_app.config['KEY_WORDS_DIR']  # 关键字目录
        key_words_dir = os.path.join(current_dir, key_words_dir)
        print(key_words_dir)
        os.makedirs(key_words_dir, exist_ok=True)  # 如果没有则创建
        with open(f'{key_words_dir}/{file_name}.py', 'w', encoding="utf-8") as f:
            f.write(keyword_value)
        # 执行git推送-如果是服务才推动
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            print("不调用")
            # from config.commit_code import auto_commit_py_files
            # auto_commit_py_files()
        return respModel.ok_resp(msg="生成文件成功", dic_t={"id": file_name})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")


# 返回树状的数据格式
from webtest.model.WebOperationTypeModel import OperationType
@module_route.route(f"/{module_name}/queryAllKeyWordList", methods=["GET"])
def queryAllKeyWordList():
    all_datas = []
    # 记录已被分类的 operation_type_id
    covered_type_ids = set()

    # 1. 先按 OperationType 表构建父级分组
    allOperationType = OperationType.query.all()
    for op_type in allOperationType:
        covered_type_ids.add(op_type.id)
        keydata = {
            "id": op_type.id,
            "value": op_type.id,
            "label": op_type.operation_type_name,
            "children": []
        }
        keyworddata = module_model.query.filter(module_model.operation_type_id == op_type.id).all()
        for kw in keyworddata:
            keydata["children"].append({
                "id": kw.id,
                "value": kw.id,
                "label": kw.name,
                "keyword_desc": kw.keyword_desc,
            })
        all_datas.append(keydata)

    # 2. 查找未被任何 OperationType 覆盖的关键字（孤儿关键字）
    all_keywords = module_model.query.all()
    orphan_groups = {}  # operation_type_id -> list of keywords
    for kw in all_keywords:
        ot_id = kw.operation_type_id
        if ot_id not in covered_type_ids:
            if ot_id not in orphan_groups:
                orphan_groups[ot_id] = []
            orphan_groups[ot_id].append(kw)

    # 3. 为孤儿关键字创建补充分组
    for ot_id, keywords in orphan_groups.items():
        fallback_label = f"操作类型 {ot_id}" if ot_id else "未分类"
        fallback_value = ot_id if ot_id else -1
        keydata = {
            "id": fallback_value,
            "value": fallback_value,
            "label": fallback_label,
            "children": []
        }
        for kw in keywords:
            keydata["children"].append({
                "id": kw.id,
                "value": kw.id,
                "label": kw.name,
                "keyword_desc": kw.keyword_desc,
            })
        all_datas.append(keydata)

    return respModel.ok_resp_simple(lst=all_datas, msg="查询成功")