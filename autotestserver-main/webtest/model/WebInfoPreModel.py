from extensions import database
from .BaseModel import BaseModel

# 用例与前置条件关联表
class WebInfoPre(BaseModel):
    __tablename__ = 't_web_info_pre'
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    web_info_id = database.Column(database.Integer, database.ForeignKey('t_web_info.id', ondelete='CASCADE'),nullable=False,comment= "用例id")
    pre_info_id = database.Column(database.Integer, database.ForeignKey('t_web_info.id', ondelete='RESTRICT'),nullable=False,comment= "前置的用例id")
    run_order = database.Column(database.Integer, comment='执行顺序')
