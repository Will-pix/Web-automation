

from extensions import database
from .BaseModel import BaseModel


class WebExecutingState(BaseModel):
    __tablename__ = "t_web_executing_state"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    collection_id = database.Column(database.Integer, comment='关联的集合ID（整数）')
    state = database.Column(database.Integer, comment='状态标识（整数，执行中1、未执行2）')
    run_result = database.Column(database.Integer, comment='状态标识（整数，失败0、通过1、进行中2）')

