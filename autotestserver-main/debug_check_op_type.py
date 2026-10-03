from app import application
from webtest.model.WebOperationTypeModel import OperationType
from extensions import database

with application.app_context():
    ops = OperationType.query.all()
    found = False
    for op in ops:
        print(f"ID: {op.id}, Name: {op.operation_type_name}")
        if "告警" in op.operation_type_name:
            found = True
    if not found:
        print("Operation Type '告警' not found.")
