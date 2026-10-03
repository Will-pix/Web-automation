from extensions import database

class ApiCollection(database.Model):
    __tablename__ = "t_api_collection"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    # project_id = database.Column(database.Integer, default=None)
    project_id = database.Column(database.Integer, database.ForeignKey('t_api_project.id', ondelete='RESTRICT'),nullable=False, default=None)
    collection_name = database.Column(database.String(255), default=None)
    collection_desc = database.Column(database.String(255), default=None)
    collection_env = database.Column(database.String(255), default=None)
    collection_params = database.Column(database.String(255), default=None)
    create_time = database.Column(database.DateTime, default=None)
    # 反向引用，方便从测试集访问其下的用例
    cases = database.relationship('ApiCase', backref='collection')