

from extensions import database

class WebDbBase(database.Model):
    __tablename__ = "t_web_database"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    # project_id = database.Column(database.Integer, nullable=False,comment="关联项目id")
    project_id = database.Column(database.Integer, database.ForeignKey('t_web_project.id', ondelete='CASCADE'), nullable=False,comment="关联项目id")
    name = database.Column(database.String(255), comment="连接名")
    ref_name = database.Column(database.String(255), comment="引用变量名")
    db_type = database.Column(database.String(255), comment="数据库类型")
    db_info = database.Column(database.String(255), comment="数据库连接信息")
    is_enabled = database.Column(database.String(255), comment="是否启用")
    create_time = database.Column(database.DateTime, comment="创建时间")