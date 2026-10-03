
from extensions import database
from .BaseModel import BaseModel

# 表：测试集，根据对应的测试用例去组装成对应的测试用例集
class WebCollectionInfo(BaseModel):
    __tablename__ = "t_web_collection_info"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    project_id = database.Column(database.Integer, database.ForeignKey('t_web_project.id', ondelete='RESTRICT'), nullable=False, comment='项目ID')
    collection_name = database.Column(database.String(255), default=None,comment='测试集合名称' )
    collection_desc = database.Column(database.String(255), default=None,comment='测试集合描述')
    collection_env = database.Column(database.String(255), default=None,comment='测试集合全局变量')
    browser_id = database.Column(database.Integer, database.ForeignKey('t_web_browser.id', ondelete='RESTRICT'), nullable=False, comment='浏览器ID')
    # create_time = database.Column(database.DateTime, default=None)
    principal = database.Column(database.String(255), comment="负责人")
    collection_env_type = database.Column(database.String(255), default="common",comment='集合环境类型，可选值：common、test、stage、online')


