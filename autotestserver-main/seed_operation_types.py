# -*- coding: UTF-8 -*-
"""插入web自动化常用的操作类型种子数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import database
from webtest.model.WebOperationTypeModel import OperationType
from datetime import datetime
from app import application

# 常见的web自动化操作类型
seed_data = [
    {"operation_type_name": "浏览器操作", "ex_fun_name": "browser_operation"},
    {"operation_type_name": "元素操作", "ex_fun_name": "element_operation"},
    {"operation_type_name": "AI视觉操作", "ex_fun_name": "ai_vision_operation"},
    {"operation_type_name": "坐标操作", "ex_fun_name": "coordinate_operation"},
    {"operation_type_name": "滑动操作", "ex_fun_name": "scroll_operation"},
    {"operation_type_name": "API请求操作", "ex_fun_name": "api_request_operation"},
    {"operation_type_name": "断言操作", "ex_fun_name": "assert_operation"},
    {"operation_type_name": "文件操作", "ex_fun_name": "file_operation"},
    {"operation_type_name": "拖拽操作", "ex_fun_name": "drag_operation"},
    {"operation_type_name": "登录操作", "ex_fun_name": "login_operation"},
    {"operation_type_name": "等待操作", "ex_fun_name": "wait_operation"},
]

with application.app_context():
    existing = OperationType.query.all()
    existing_names = {ot.operation_type_name for ot in existing}

    inserted = 0
    for item in seed_data:
        if item["operation_type_name"] not in existing_names:
            ot = OperationType(
                operation_type_name=item["operation_type_name"],
                ex_fun_name=item["ex_fun_name"],
                create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            )
            database.session.add(ot)
            inserted += 1
            print(f"  [INSERT] {item['operation_type_name']}")
        else:
            print(f"  [SKIP] {item['operation_type_name']} (已存在)")

    if inserted > 0:
        database.session.commit()
        print(f"\n成功插入 {inserted} 条操作类型记录")
    else:
        print("\n所有操作类型已存在，无需插入")

    # 显示当前所有操作类型
    print("\n当前操作类型列表：")
    all_types = OperationType.query.all()
    for ot in all_types:
        print(f"  ID:{ot.id}  {ot.operation_type_name}")
