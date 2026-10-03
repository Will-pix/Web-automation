

from extensions import database

class ApiProject(database.Model):
    __tablename__ = "t_api_project"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    project_name = database.Column(database.String(255))
    project_desc = database.Column(database.String(255))
    create_time = database.Column(database.DateTime)
    # 反向引用，方便从项目访问其下的模块
    modules = database.relationship('ApiModule', backref='project')