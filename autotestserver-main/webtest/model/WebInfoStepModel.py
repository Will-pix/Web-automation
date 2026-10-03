from extensions import database


# 表：单个测试用例-操作步骤表
class WebInfoStep(database.Model):
    __tablename__ = "t_web_info_step"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    # web_info_id = database.Column(database.Integer, comment='用例的ID')
    web_info_id = database.Column(database.Integer, database.ForeignKey('t_web_info.id', ondelete='CASCADE'),nullable=False,comment="用例的ID")
    # key_word_id = database.Column(database.Integer, comment='关键字方法ID')
    key_word_id = database.Column(database.Integer,database.ForeignKey('t_web_keyword.id',ondelete='RESTRICT'), nullable=False,comment='关键字方法ID')
    step_desc = database.Column(database.String(255), comment='步骤描述')
    ref_variable = database.Column(database.Text, comment='引用变量')
    run_order = database.Column(database.Integer, comment='步骤的顺序')
    create_time = database.Column(database.DateTime, comment='创建时间')
    is_enabled = database.Column(database.Boolean, default=True, nullable=False, comment="开关状态：True启用，False禁用")

