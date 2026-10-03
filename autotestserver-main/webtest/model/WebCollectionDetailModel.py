from extensions import database


# 表：单个测试用例表
class WebCollectionDetail(database.Model):
    __tablename__ = "t_web_collection_detail"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    collection_info_id = database.Column(database.Integer, database.ForeignKey('t_web_collection_info.id', ondelete='CASCADE'), nullable=False, comment='测试集合ID')
    web_info_id = database.Column(database.Integer, database.ForeignKey('t_web_info.id', ondelete='RESTRICT'), nullable=False, comment='测试用例ID')
    # ddt_param_data = database.Column(database.String(255), comment='测试用例DDT数据')
    ddt_param_data = database.Column(database.Text, comment='测试用例DDT数据')

    run_order = database.Column(database.Integer, comment='执行顺序')
    create_time = database.Column(database.DateTime)
