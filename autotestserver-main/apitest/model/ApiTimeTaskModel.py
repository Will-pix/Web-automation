from extensions import database

class ApiTimeTask(database.Model):
    __tablename__ = "t_time_task"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    task_name = database.Column(database.String(255), default=None,comment="定时任务名称")
    # nullable不允许为空
    # collection_id = database.Column(database.Integer, nullable=False, comment="关联集合ID")
    collection_id = database.Column(database.Integer, database.ForeignKey('t_api_collection.id', ondelete='RESTRICT'),nullable=False,comment="关联集合ID")
    # project_id = database.Column(database.Integer, comment='项目ID')
    project_id = database.Column(database.Integer, database.ForeignKey('t_api_project.id', ondelete='RESTRICT'), nullable=False,comment='项目ID')
    last_time =  database.Column(database.DateTime, comment="最近一次执行时间")
    # 允许为空，默认值为空
    is_state = database.Column(database.Boolean, nullable=True, default=None,comment="最近一次是否通过")
    task_num = database.Column(database.Integer, nullable=True,default=0, comment="执行总次数")
    task_type = database.Column(database.String(255), default=None,comment="执行类型")
    interval_time = database.Column(database.String(255), default=None,comment="间隔执行时间")
    fixed_time = database.Column(database.String(255), default=None,comment="定制执行时间")
    create_time = database.Column(database.DateTime, comment="创建时间")