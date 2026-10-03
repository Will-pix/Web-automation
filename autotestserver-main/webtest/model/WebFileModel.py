from extensions import database
from .BaseModel import BaseModel


# 表：浏览器管理，管理Web自动化的浏览器及对应的数据配置
class WebFile(BaseModel):
    __tablename__ = "t_web_file"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    file_name = database.Column(database.String(255), comment='文件名称')
    file_desc = database.Column(database.String(255), comment='文件描述')
