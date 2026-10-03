from extensions import database


class ApiHistoryModel(database.Model):
    __tablename__ = "t_api_history"

    id = database.Column(database.Integer, primary_key=True, comment='记录编号')
    collection_id = database.Column(database.Integer, comment='关联t_api_collection表主键id')
    history_desc = database.Column(database.String(255), comment='运行记录简述')
    history_detail = database.Column(database.String(255), comment='运行详细记录')
    create_time = database.Column(database.DateTime, comment='创建时间')
