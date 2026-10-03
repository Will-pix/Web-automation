# 从 app 模块中导入 database 对象，这个对象通常是 SQLAlchemy 实例，用于与数据库交互
from extensions import database

# 定义一个名为 ApiInfo 的类，它继承自 database.Model，意味着这是一个 SQLAlchemy 的模型类，用于表示数据库中的一张表
class ApiInfo(database.Model):
    # 指定该模型类对应的数据库表名
    __tablename__ = "t_api_info"
    # 定义一个名为 id 的列，数据类型为整数，将其设置为主键，用于唯一标识每一条记录。
    # comment 参数用于给该列添加注释，方便后续理解表结构，autoincrement 设为 True 表示该列的值会自动递增
    id = database.Column(database.Integer, primary_key=True, comment='接口用例编号', autoincrement=True)
    # 定义一个名为 project_id 的列，数据类型为整数，用于存储项目的 ID，comment 参数为该列添加注释
    # project_id = database.Column(database.Integer, comment='项目ID')
    project_id = database.Column(database.Integer, database.ForeignKey('t_api_project.id', ondelete='RESTRICT'),nullable=False)

    # 定义一个名为 module_id 的列，数据类型为整数，用于存储模块的 ID，comment 参数为该列添加注释
    # module_id = database.Column(database.Integer, comment='模块ID')
    module_id = database.Column(database.Integer, database.ForeignKey('t_api_module.id', ondelete='RESTRICT'),nullable=False)

    # 定义一个名为 api_name 的列，数据类型为字符串，最大长度为 255 个字符，用于存储接口的名称，comment 参数为该列添加注释
    api_name = database.Column(database.String(255), comment='接口名称')
    # 定义一个名为 request_method 的列，数据类型为字符串，最大长度为 255 个字符，用于存储请求的方法（如 GET、POST 等），comment 参数为该列添加注释
    request_method = database.Column(database.String(255), comment='请求方法')
    # 定义一个名为 request_url 的列，数据类型为字符串，最大长度为 255 个字符，用于存储请求的地址，comment 参数为该列添加注释
    request_url = database.Column(database.String(255), comment='请求地址')
    # 定义一个名为 request_params 的列，数据类型为字符串，最大长度为 255 个字符，用于存储 URL 参数，comment 参数为该列添加注释
    request_params = database.Column(database.String(255), comment='URL参数')
    # 定义一个名为 request_headers 的列，数据类型为文本类型，使用 utf8_general_ci 字符集排序规则，用于存储请求头信息，comment 参数为该列添加注释
    # request_headers = database.Column(database.Text(collation='utf8_general_ci'), comment='请求头')
    request_headers = database.Column(database.Text(), comment='请求头')
    # 定义一个名为 debug_vars 的列，数据类型为文本类型，使用 utf8_general_ci 字符集排序规则，用于存储调试参数，comment 参数为该列添加注释
    # debug_vars = database.Column(database.Text(collation='utf8_general_ci'), comment='调试参数')
    debug_vars = database.Column(database.Text(), comment='调试参数')
    # 定义一个名为 request_form_datas 的列，数据类型为字符串，最大长度为 255 个字符，用于存储 form-data 格式的数据，comment 参数为该列添加注释
    request_form_datas = database.Column(database.String(255), comment='form-data')
    # 定义一个名为 request_www_form_datas 的列，数据类型为字符串，最大长度为 255 个字符，用于存储 www-form-data 格式的数据，comment 参数为该列添加注释
    request_www_form_datas = database.Column(database.String(255),comment='www-form-data')
    # 定义一个名为 requests_json_data 的列，数据类型为字符串，最大长度为 255 个字符，用于存储 JSON 格式的数据，comment 参数为该列添加注释
    requests_json_data = database.Column(database.String(255), comment='json数据')
    # 定义一个名为 pre_request 的列，数据类型为字符串，最大长度为 255 个字符，用于存储执行请求前需要执行的事件，comment 参数为该列添加注释
    pre_request = database.Column(database.String(255), comment='执行前事件')
    # 定义一个名为 post_request 的列，数据类型为字符串，最大长度为 255 个字符，用于存储执行请求后需要执行的事件，comment 参数为该列添加注释
    post_request = database.Column(database.String(255), comment='执行后事件')
    # 定义一个名为 create_time 的列，数据类型为日期时间类型，设置 unique 为 True 表示该列的值必须唯一，comment 参数为该列添加注释
    create_time = database.Column(database.DateTime, unique=True)

    # 反向引用，方便从接口访问其下的用例
    cases = database.relationship('ApiCase', backref='api')