from extensions import database
from datetime import datetime
from flask import g  # 导入g变量


class BaseModel(database.Model):
    __abstract__ = True  # 抽象类，不生成独立表

    # 字段定义保持不变
    create_time = database.Column(database.DateTime, comment="创建时间")
    update_time = database.Column(database.DateTime, comment="修改时间")
    create_by = database.Column(database.String(255), comment="创建人ID")
    update_by = database.Column(database.String(255), comment="修改人ID")
    create_name = database.Column(database.String(255), comment="创建人name")
    update_name = database.Column(database.String(255), comment="修改人name")


@database.event.listens_for(BaseModel, "before_insert", propagate=True)
def auto_fill_insert_fields(mapper, connection, target):
    # 打印g变量内容（确认结构）
    print("\n【before_insert】当前g变量所有内容：", g.__dict__)

    # 1. 先从g中获取user_payload子字典（你的数据存在这里）
    user_payload = g.get("user_payload", {})  # 没有则返回空字典

    # 2. 从user_payload中提取用户ID和名称（键名和日志一致）
    current_user_id = user_payload.get("access_user_id", "未知")
    current_user_name = user_payload.get("access_name", "未知用户")

    # 打印提取结果（调试用）
    print("【before_insert】提取的用户ID：", current_user_id)
    print("【before_insert】提取的用户名称：", current_user_name)

    # 3. 赋值给模型字段
    target.create_time = datetime.now()
    target.update_time = datetime.now()
    target.create_by = current_user_id
    target.update_by = current_user_id
    target.create_name = current_user_name
    target.update_name = current_user_name


@database.event.listens_for(BaseModel, "before_update", propagate=True)
def auto_fill_update_fields(mapper, connection, target):
    # 修正打印信息（之前写成before_insert了）
    print("\n【before_update】当前g变量所有内容：", g.__dict__)

    # 同样从user_payload中提取
    user_payload = g.get("user_payload", {})
    current_user_id = user_payload.get("access_user_id", "未知")
    current_user_name = user_payload.get("access_name", "未知用户")

    # 打印提取结果（调试用）
    print("【before_update】提取的用户ID：", current_user_id)
    print("【before_update】提取的用户名称：", current_user_name)

    # 赋值给模型字段（只更新修改相关字段）
    target.update_time = datetime.now()
    target.update_by = current_user_id
    target.update_name = current_user_name
