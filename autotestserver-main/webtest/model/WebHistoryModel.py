from extensions import database


class WebHistoryModel(database.Model):
    __tablename__ = "t_web_history"

    id = database.Column(database.Integer, primary_key=True, comment='记录编号')
    collection_info_id = database.Column(database.Integer, comment='关联t_web_collection_info表主键id')
    history_desc = database.Column(database.String(255), comment='运行记录简述')
    history_detail = database.Column(database.String(255), comment='运行详细记录')
    create_time = database.Column(database.DateTime, comment='创建时间')
    collection_principal = database.Column(database.String(255), comment='当前记录集合负责人')
    failed_cases_detail = database.Column(database.Text, comment='当前记录错误详情')
    pass_cases_detail = database.Column(database.Text, comment='当前记录通过详情')
    collection_env_type = database.Column(database.String(255), default="common",comment='集合环境类型，可选值：common、test、stage、online')
    run_time = database.Column(database.String(50), comment='执行耗时，如 12.34s')
