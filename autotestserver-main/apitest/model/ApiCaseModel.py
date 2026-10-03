from extensions import database

class ApiCase(database.Model):
    __tablename__ = "t_api_case"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    # nullable不允许为空
    # api_info_id = database.Column(database.Integer, nullable=False, comment="关联接口ID")
    api_info_id = database.Column(database.Integer, database.ForeignKey('t_api_info.id', ondelete='CASCADE'), nullable=False, comment="关联接口ID")
    # collection_id = database.Column(database.Integer, nullable=False, comment="关联集合ID")
    collection_id = database.Column(database.Integer, database.ForeignKey('t_api_collection.id', ondelete='CASCADE'), nullable=False, comment="关联集合ID")
    param_data = database.Column(database.Text, comment="参数化运行")
    run_order = database.Column(database.Integer, nullable=False, comment="运行顺序")
    create_time = database.Column(database.DateTime, comment="创建时间")