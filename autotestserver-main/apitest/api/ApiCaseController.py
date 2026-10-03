from flask import Blueprint, request
from extensions import database
from apitest.model.ApiInfoModel import ApiInfo
from apitest.model.ApiCaseModel import ApiCase  # 请根据您的模型路径进行调整
from core.resp_model import respModel
from datetime import datetime
module_name = "ApiCase"  # 模块名称，根据实际情况修改
module_model = ApiCase
module_route = Blueprint(f"route_{module_name}", __name__)


# 查询数据-根据分页，测试集id，查询所属的接口信息
@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    try:
        # 先获取分页数据
        page = int(request.json["page"])
        page_size = int(request.json["PageSize"])
        # 设置上下文
        # 设置上下文
        # with application.app_context():
        # 设置一个筛选参数
        filter_list = []
        # 获取传进来的测试集id
        collection_id = int(request.json["collection_id"])
        # 构建测试集参数数据并加入到筛选参数
        filter_list.append(module_model.collection_id==collection_id)
        # 根据筛选条件，筛选出对应测试集id的数据并加入分页数据，filter可以传表达式
        cases = module_model.query.filter(*filter_list).limit(page_size).offset((page-1) * page_size).all()
        # 数据的总条数
        total = module_model.query.filter(*filter_list).count()
        # 设置一个返回结果的空数组
        results = []
        # 遍历cases总数据
        for case in cases:
            # 根据case里的api_info_id接口id，获取接口数据表的接口数据，filter_by传简单数据，first()是取出一条数据
            api_info = ApiInfo.query.filter_by(id=case.api_info_id).first()
            # 将获取的模型数据实例（接口数据）转换为字典
            result = respModel().get_custom_attributes(api_info)
            # 将中间表数据，更新/追加到接口数据上
            result.update(respModel().get_custom_attributes(case))
            # 将数据添加进总返回列表
            results.append(result)
            return respModel().ok_resp_simple_list(lst=results,total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误，请联系管理员:{e}")


# 查询数据-根据中间表id查询一条数据
@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        # 从请求的查询参数中获取 id 并转换为整数类型
        data_id = int(request.args.get("id"))
        # with application.app_context():
        # 使用 filter_by 方法根据 id 进行筛选，并获取第一条记录
        data = module_model.query.filter_by(id=data_id).first()
        if data:
            # 如果找到记录，以成功响应返回该记录
            return respModel().ok_resp(obj=data)
        else:
            # 如果未找到记录，返回查询成功但无数据的提示
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        # 若出现异常，打印异常信息并返回服务器错误响应
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# 插入数据
@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    print(request.json)
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

