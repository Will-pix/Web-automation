

from extensions import database
from .BaseModel import BaseModel

class WebProject(BaseModel):
    __tablename__ = "t_web_project"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    project_name = database.Column(database.String(255), comment="项目名称")
    project_desc = database.Column(database.String(255), comment="项目描述")
    # create_time = database.Column(database.DateTime, comment="创建时间")
    # update_time = database.Column(database.DateTime, comment="修改时间")
    # create_by = database.Column(database.String(255), comment="创建人ID")
    # update_by = database.Column(database.String(255), comment="修改人ID")
    # create_name = database.Column(database.String(255), comment="创建人name")
    # update_name = database.Column(database.String(255), comment="修改人name")