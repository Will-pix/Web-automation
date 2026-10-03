from extensions import database

class ApiModule(database.Model):
    __tablename__ = "t_api_module"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    # project_id = database.Column(database.Integer, nullable=False)
    project_id = database.Column(database.Integer, database.ForeignKey('t_api_project.id', ondelete='RESTRICT'), nullable=False)
    module_name = database.Column(database.String(255), default=None)
    module_desc = database.Column(database.String(255), default=None)
    create_time = database.Column(database.DateTime, default=None)
    # 反向引用，方便从模块访问其下的接口
    apis = database.relationship('ApiInfo', backref='module')
