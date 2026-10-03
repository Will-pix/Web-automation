from extensions import database
from .BaseModel import BaseModel


# 表：浏览器管理，管理Web自动化的浏览器及对应的数据配置
class WebBrowser(BaseModel):
    __tablename__ = "t_web_browser"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(255), comment='浏览器名称')
    enName = database.Column(database.String(255), comment='浏览器英文名')
    project_id = database.Column(database.Integer, database.ForeignKey('t_web_project.id', ondelete='RESTRICT'), nullable=False,comment='项目id')
    # project_id = database.Column(database.Integer, comment='项目id')
    remote_url = database.Column(database.String(255), comment='Grid地址')
    driver_path = database.Column(database.String(255), comment='驱动地址')
    browser_img = database.Column(database.String(255), comment='浏览器图片')
    browser_version = database.Column(database.String(255), comment='浏览器版本')
    browser_debug = database.Column(database.Text, comment='浏览器调试参数')
    # browser_debug = database.Column(database.String(255), comment='浏览器调试参数')
    is_enabled = database.Column(database.String(255), comment='是否启用')
    # create_time = database.Column(database.DateTime)