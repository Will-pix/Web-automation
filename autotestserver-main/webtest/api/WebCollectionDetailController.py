from extensions import database
from flask import Blueprint, request, g
from webtest.model.WebCollectionDetailModel import WebCollectionDetail  # 子表模型
from webtest.model.WebCollectionInfoModel import WebCollectionInfo  # 父表模型（新增导入）
from datetime import datetime
from core.resp_model import respModel
import traceback

# 模块信息
module_name = "WebCollectionDetail"  # 模块名称
module_model = WebCollectionDetail
module_route = Blueprint(f"route_{module_name}", __name__)

# 其它模块
from webtest.model.WebInfoModel import WebInfo


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        # 已删除多余的with语句
        filter_list = []
        # 增加可以通过collection_info_id进行筛选的条件
        collection_info_id = request.json.get("collection_info_id", 0)
        if type(collection_info_id) is not str and collection_info_id > 0:
            filter_list.append(module_model.collection_info_id == collection_info_id)

        # 数据库查询- 按run_order升序
        datas = module_model.query.order_by(module_model.run_order.asc()).filter(*filter_list).limit(
            page_size).offset((page - 1) * page_size).all()
        total = module_model.query.filter(*filter_list).count()

        results = []
        # 遍历所有的关联的测试用例
        for data in datas:
            # 1. 通过用例的编号查询到具体的信息
            web_info_data = WebInfo.query.filter_by(id=data.web_info_id).first()
            # 2. 合并子表和关联用例信息
            result = respModel().get_custom_attributes(web_info_data)
            result.update(respModel().get_custom_attributes(data))
            results.append(result)

        return respModel().ok_resp_simple_list(lst=results, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


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


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据：同时更新父级WebCollectionInfo的修改人/时间 """
    try:
        # 1. 获取当前用户信息
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "未知")
        current_user_name = user_payload.get("access_name", "未知用户")

        # 2. 新增子表记录
        request.json["id"] = None  # ID自增长
        data = module_model(** request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        database.session.add(data)
        database.session.flush()  # 刷新获取collection_info_id
        data_id = data.id

        # 3. 更新父级WebCollectionInfo
        collection_info_id = data.collection_info_id  # 从子表获取父级ID
        parent_data = WebCollectionInfo.query.filter_by(id=collection_info_id).first()
        if parent_data:
            parent_data.update_time = datetime.now()
            parent_data.update_by = current_user_id
            parent_data.update_name = current_user_name

        # 4. 提交事务
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        database.session.rollback()  # 出错回滚
        traceback.print_exc()
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据：同时更新父级WebCollectionInfo的修改人/时间 """
    try:
        # 1. 获取当前用户信息
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "未知")
        current_user_name = user_payload.get("access_name", "未知用户")

        # 2. 更新子表记录（实例化更新，触发基类事件）
        update_data = request.json
        target_data = module_model.query.filter_by(id=update_data["id"]).first()
        if target_data:
            for key, value in update_data.items():
                if key != "id":  # 排除主键
                    setattr(target_data, key, value)

        # 3. 更新父级WebCollectionInfo
        collection_info_id = target_data.collection_info_id  # 从子表实例获取父级ID
        parent_data = WebCollectionInfo.query.filter_by(id=collection_info_id).first()
        if parent_data:
            parent_data.update_time = datetime.now()
            parent_data.update_by = current_user_id
            parent_data.update_name = current_user_name

        # 4. 提交事务
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据：同时更新父级WebCollectionInfo的修改人/时间 """
    try:
        # 1. 获取当前用户信息
        user_payload = g.get("user_payload", {})
        current_user_id = user_payload.get("access_user_id", "未知")
        current_user_name = user_payload.get("access_name", "未知用户")

        # 2. 获取子表记录，提取父级ID
        data_id = request.args.get("id")
        target_data = module_model.query.filter_by(id=data_id).first()
        if not target_data:
            return respModel.error_resp(msg="子记录不存在")
        collection_info_id = target_data.collection_info_id  # 父级ID

        # 3. 更新父级WebCollectionInfo
        parent_data = WebCollectionInfo.query.filter_by(id=collection_info_id).first()
        if parent_data:
            parent_data.update_time = datetime.now()
            parent_data.update_by = current_user_id
            parent_data.update_name = current_user_name

        # 4. 删除子表记录
        database.session.delete(target_data)
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        database.session.rollback()  # 出错回滚
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")