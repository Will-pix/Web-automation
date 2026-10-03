from extensions import database
from .BaseModel import BaseModel
from datetime import datetime

class WebTimeTask(database.Model):
    __tablename__ = "t_web_time_task"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    task_name = database.Column(database.String(255), default=None,comment="定时任务名称")
    # nullable不允许为空
    collection_id = database.Column(database.Integer, database.ForeignKey('t_web_collection_info.id', ondelete='RESTRICT'),nullable=False,comment="关联集合ID")
    project_id = database.Column(database.Integer, database.ForeignKey('t_web_project.id', ondelete='RESTRICT'), nullable=False,comment='项目ID')
    last_time =  database.Column(database.DateTime, comment="最近一次执行时间")
    # 允许为空，默认值为空
    is_state = database.Column(database.Boolean, nullable=True, default=None,comment="最近一次是否通过")
    task_num = database.Column(database.Integer, nullable=True,default=0, comment="执行总次数")
    task_type = database.Column(database.String(255), default=None,comment="执行类型")
    interval_time = database.Column(database.String(255), default=None,comment="间隔执行时间")
    fixed_time = database.Column(database.String(255), default=None,comment="定制执行时间")
    cron_time = database.Column(database.String(255), default=None,comment="自定义执行时间")
    # create_time = database.Column(database.DateTime, comment="创建时间")

    # 通用字段（手动控制，不依赖基类自动填充）
    create_time = database.Column(database.DateTime, default=datetime.now, comment="创建时间")
    update_time = database.Column(database.DateTime, default=datetime.now, comment="修改时间")
    create_by = database.Column(database.String(255), comment="创建人ID")
    update_by = database.Column(database.String(255), comment="修改人ID")
    create_name = database.Column(database.String(255), comment="创建人名称")
    update_name = database.Column(database.String(255), comment="修改人名称")
    inform = database.Column(database.Boolean, default=False, comment="免打扰：True启用，False关闭")

    collection_env_type = database.Column(database.String(255), default="common",comment='集合环境类型，可选值：common、test、stage、online')

