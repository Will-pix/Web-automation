import os
import uuid

from flask import Blueprint, request, current_app
from core.resp_model import respModel
from extensions import database
from webtest.model.WebFileModel import WebFile
from datetime import datetime
import re
# 模块信息
module_name = "WebFile"  # 模块名称
module_model = WebFile
module_route = Blueprint(f"route_{module_name}", __name__)


# @module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
# def queryByPage():
#     """ 查询数据(支持模糊搜索) """
#     try:
#         # 分页查询
#         page = int(request.json["page"])
#         page_size = int(request.json["pageSize"])
#         # 已删除多余的with语句
#         filter_list = []
#         # 添加关键字描述搜索条件
#         file_name = request.json.get("file_name", "")
#         if len(file_name) > 0:
#             filter_list.append(module_model.file_name.like(f'%{file_name}%'))
#
#         # 数据库查询
#         datas = module_model.query.filter(*filter_list).order_by(module_model.create_time.desc()).limit(page_size).offset((page - 1) * page_size).all()
#         total = module_model.query.filter(*filter_list).count()
#         return respModel().ok_resp_list(lst=datas, total=total)
#     except Exception as e:
#         print(e)
#         return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 触发时同步目录文件到数据库（清空旧数据→插入新数据），再从数据库查询返回 """
    try:
        # --------------------------
        # 1. 同步目录文件到数据库（核心逻辑）
        # --------------------------
        # 1.1 目标目录路径（与upload接口一致）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_folder_from_config = current_app.config['UPLOAD_FOLDER']
        target_dir = os.path.join(current_dir, upload_folder_from_config)

        # target_dir = os.path.join(current_dir, "../tool")

        # 1.2 验证目录存在
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            return respModel.error_resp(f"目录不存在或不是有效目录：{target_dir}")

        # 1.3 读取目录下所有文件（仅文件，排除子目录）
        file_list = []
        for entry in os.scandir(target_dir):
            if entry.is_file():  # 只处理文件
                file_list.append({
                    "file_name": entry.name,  # 文件名
                    "create_time": datetime.fromtimestamp(entry.stat().st_ctime),  # 文件创建时间
                    "file_size": entry.stat().st_size  # 文件大小（字节，可选）
                })

        # 1.4 清空数据库现有数据
        module_model.query.delete()
        database.session.commit()  # 提交删除

        # 1.5 批量插入新文件数据到数据库
        for file_info in file_list:
            new_file = module_model(
                file_name=file_info["file_name"]
            )
            database.session.add(new_file)
        database.session.commit()  # 提交插入

        # --------------------------
        # 2. 从数据库查询并返回（复用原分页+模糊搜索逻辑）
        # --------------------------
        page = int(request.json.get("page", 1))
        page_size = int(request.json.get("pageSize", 10))
        filter_list = []

        # 模糊搜索（按文件名）
        file_name = request.json.get("file_name", "")
        if file_name:
            filter_list.append(module_model.file_name.like(f'%{file_name}%'))

        # 分页查询
        datas = module_model.query.filter(*filter_list) \
            .order_by(module_model.create_time.desc()) \
            .limit(page_size) \
            .offset((page - 1) * page_size) \
            .all()
        total = module_model.query.filter(*filter_list).count()

        return respModel().ok_resp_list(lst=datas, total=total)

    except Exception as e:
        database.session.rollback()  # 异常时回滚
        print(f"同步/查询失败：{str(e)}")
        return respModel.error_resp(f"服务器错误：{str(e)}")

@module_route.route(f"/{module_name}/upload", methods=["POST"])
def upload():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("当前接口文件目录：", current_dir)

    # 从配置中获取 UPLOAD_FOLDER（你的核心需求）
    upload_folder_from_config = current_app.config['UPLOAD_FOLDER']
    print("配置中的 UPLOAD_FOLDER：", upload_folder_from_config)

    # 拼接最终目录：current_dir + 配置的 UPLOAD_FOLDER
    file_dir = os.path.join(current_dir, upload_folder_from_config)
    print("最终文件存储目录：", file_dir)

    # 1. 接收并验证前端上传的文件
    if 'file' not in request.files:
        return respModel.error_resp(msg="未上传文件，请选择文件后重试")

    # 获取上传的文件（如果前端允许多文件，用request.files.getlist('file')）
    files = request.files.getlist('file')  # 支持多文件上传
    if not files or all(file.filename == '' for file in files):
        return respModel.error_resp(msg="文件名称为空，请重新选择文件")
        # 3. 处理每个文件（按你的需求：保留原始文件名+校验数据库重复）
    for file in files:
        original_filename = file.filename  # 原始文件名（不拼接，直接使用）

        # 3.1 校验数据库是否已存在相同文件名（与insert接口逻辑一致）
        existing_file = module_model.query.filter_by(file_name=original_filename).first()
        if existing_file:
            # 若存在，回滚事务并返回错误（多文件上传时，一个失败则全部失败）
            database.session.rollback()
            return respModel.error_resp(msg=f"数据库已存在相同文件：{original_filename}，请重新上传")

        # 3.2 校验服务器目录是否已存在同名文件（可选：避免文件覆盖）
        save_path = os.path.join(file_dir, original_filename)
        if os.path.exists(save_path):
            database.session.rollback()
            return respModel.error_resp(msg=f"服务器已存在同名文件：{original_filename}，请修改文件名后重试")

        # 3.3 保存文件到服务器目录（使用原始文件名）
        file.save(save_path)
        print(f"文件 {original_filename} 已保存至：{save_path}")

        # 3.4 记录到数据库（与insert接口风格统一）
        new_file = module_model(
            file_name=original_filename,  # 原始文件名（与数据库校验字段一致）
            file_desc=request.form.get('file_desc', ''),  # 接收文件描述
            # 若有创建人/更新人字段，可在此补充（与其他接口一致）
            # create_by=current_user.id,
            # update_by=current_user.id
        )
        database.session.add(new_file)

    # 4. 提交事务（批量处理多文件，全部验证通过后再提交）
    database.session.commit()

    # 5. 返回成功响应
    return respModel.ok_resp(
        msg=f"成功上传 {len(files)} 个文件",
        dic_t={"count": len(files), "storage_dir": file_dir}
    )




@module_route.route(f"/{module_name}/get_regular_expression", methods=["POST"])
def get_regular_expression():
    try:
        req_data = request.json
        file_name = req_data.get("file_name", "").strip()
        if not file_name:
            return respModel.error_resp(msg="请传入有效的文件名")

        # 1. 分离文件名和扩展名（处理多后缀情况，如“a.b.pdf”取“pdf”）
        name_parts = file_name.split('.')
        if len(name_parts) < 2:
            return respModel.error_resp(msg="文件名缺少扩展名（如 .pdf、.txt）")
        ext = name_parts[-1]  # 扩展名（如 pdf）
        name_without_ext = '.'.join(name_parts[:-1])  # 去掉扩展名的部分

        # 2. 提取文件名中的“连续文字片段”（字母、中文组成的连续字符串）
        # 正则匹配：字母（a-zA-Z）、中文（\u4e00-\u9fa5）组成的连续序列
        text_pattern = re.compile(r'[a-zA-Z\u4e00-\u9fa5]+')
        text_fragments = text_pattern.findall(name_without_ext)

        if not text_fragments:
            return respModel.error_resp(msg="文件名中未找到有效的文字片段（字母或中文）")

        # 取最长的文字片段作为核心标识（确保匹配最关键的固定部分）
        core_text = max(text_fragments, key=len)

        # 3. 生成最终正则表达式（转义核心文字中的特殊字符，避免冲突）
        escaped_core = re.escape(core_text)  # 转义核心文字中的正则特殊字符
        regex_pattern = f".*{escaped_core}.*\\.{ext}$"  # .*匹配任意字符，确保包含核心文字和扩展名

        return respModel.ok_resp(
            msg="正则表达式生成成功",
            dic_t={
                "original_file_name": file_name,
                "core_text": core_text,  # 提取的核心文字片段（可选返回）
                "regex_pattern": regex_pattern
            }
        )

    except Exception as e:
        return respModel.error_resp(msg=f"生成失败：{str(e)}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 根据数据库ID删除：先查文件系统，存在则删文件+删数据，不存在则不操作 """
    try:
        # 1. 获取前端传入的数据库ID
        data_id = request.args.get("id")
        if not data_id or not data_id.isdigit():
            return respModel.error_resp(msg="请传入有效的ID（数字）")
        data_id = int(data_id)  # 转换为整数

        # 2. 根据ID查询数据库记录
        file_data = module_model.query.filter_by(id=data_id).first()
        if not file_data:
            return respModel.error_resp(msg=f"数据库中不存在ID为 {data_id} 的记录")
        file_name = file_data.file_name  # 获取文件名

        # 3. 构建文件路径（与queryByPage接口保持一致的目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_folder_from_config = current_app.config['UPLOAD_FOLDER']
        target_dir = os.path.join(current_dir, upload_folder_from_config)

        # target_dir = os.path.join(current_dir, "../tool")
        file_path = os.path.join(target_dir, file_name)  # 完整文件路径

        # 4. 检查文件是否存在
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # 4.1 存在则删除文件
            os.remove(file_path)
            print(f"文件 {file_path} 已删除")

            # 4.2 删除数据库记录
            module_model.query.filter_by(id=data_id).delete()
            database.session.commit()
            return respModel.ok_resp(msg=f"文件 {file_name} 及数据库记录已删除")
        else:
            # 5. 不存在则不操作，返回提示
            return respModel.ok_resp(msg=f"文件系统中未找到 {file_name}，不执行删除操作")

    except Exception as e:
        database.session.rollback()  # 异常时回滚事务
        print(f"删除失败：{str(e)}")
        return respModel.error_resp(msg=f"删除失败：{str(e)}")