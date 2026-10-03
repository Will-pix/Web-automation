import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
import allure
from webtest.tool.webrun.core.globalContext import g_context
from webtest.tool.webrun.utils.VarRender import refresh


class Keywords:
    driver = None
    def __init__(self,webdriver:WebDriver):
        self.driver = webdriver


    # 浏览器操作- 打开浏览器
    def open_browser(self,**kwargs):
        self.driver.get(kwargs["数据内容"])

    # 浏览器操作- 关闭浏览器
    def quit_browser(self,**kwargs):
        self.driver.quit()

    # 浏览器操作- 关闭当前窗口
    def close_browser(self,**kwargs):
        self.driver.close()

    # 浏览器操作- 最大化当前窗口
    def maximized_browser(self,**kwargs):
        self.driver.maximize_window()

    # 元素操作-输入内容
    def input_context(self,**kwargs):
        # self.driver.find_element(kwargs["定位方式"],kwargs["目标对象"]).send_keys(kwargs["数据内容"])
        by = kwargs["定位方式"]
        value = kwargs["目标对象"]
        element =  WebDriverWait(self.driver, timeout= 30, poll_frequency= 0.5, ignored_exceptions=None).until(lambda x:x.find_element(by=by, value=value))
        element.clear()  # 清空输入框
        element.send_keys(kwargs["数据内容"])


    # 元素操作-点击元素
    def option_click(self,**kwargs):
        # self.driver.find_element(kwargs["定位方式"],kwargs["目标对象"]).click()
        by = kwargs["定位方式"]
        value = kwargs["目标对象"]
        # 使用显示等待 查找元素
        element =  WebDriverWait(self.driver, timeout= 30, poll_frequency= 0.5, ignored_exceptions=None).until(lambda x:x.find_element(by=by, value=value))
        element.click()

    # 等待-强制等待
    def wait_sleep(self,**kwargs):
        time.sleep(int(kwargs["数据内容"]))

    # 等待-隐式等待
    def im_sleep(self,**kwargs):
        self.driver.implicitly_wait(int(kwargs["数据内容"]))

    # 等待-显示等待
    def ec_sleep(self,**kwargs):
        wait = WebDriverWait(self.driver, int(kwargs["数据内容"]))
        element = wait.until(EC.presence_of_element_located(kwargs["目标对象"]))

    # 断言处理 - 断言浏览器标题
    def assert_title(self,**kwargs):
        assert EC.title_is(kwargs["数据内容"])(self.driver)

    # 断言处理 - 断言当前Url
    def assert_url(self,**kwargs):
        assert EC.url_to_be(kwargs["数据内容"])(self.driver)

    # 断言处理 - 相等
    def assert_text_eql(self,**kwargs):
        # 预期值
        target = kwargs["数据内容"]
        # 当前值
        current = self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"]).text
        print(f"判断是否相等,{target} - {current}")
        assert current == target

    # 断言处理 - 不相等
    def assert_text_noeql(self, **kwargs):
        assert self.driver.find_element(kwargs["定位方式"],kwargs["目标对象"]).text != kwargs["数据内容"]

    # 断言处理 - 包含
    def assert_text_in(self, **kwargs):
        assert kwargs["数据内容"] in self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"]).text

    # 断言处理 - 大于
    def assert_text_gre(self, **kwargs):
        assert self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"]).text > kwargs["数据内容"]

    # 断言处理 - 小于assert_text_eql
    def assert_text_less(self, **kwargs):
        assert self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"]).text < kwargs["数据内容"]

    # 断言处理 - 不包含
    def assert_text_notin(self, **kwargs):
        assert kwargs["数据内容"] not in self.driver.find_elements(kwargs["定位方式"], kwargs["目标对象"])

    def 截图(self):
        allure.attach(self.driver.get_screenshot_as_png(), "截图快照", allure.attachment_type.PNG)  # 截图

    def mysql_sql_exec(self, **kwargs):
        # print("执行SQL:", kwargs["sql语句"])
        # sql_value = kwargs["sql语句"]
        # all_context = g_context().show_dict()
        # sql_value = refresh(sql_value,all_context)
        # print("转换后的sql",sql_value)

        import pymysql
        from pymysql import cursors
        config = {"cursorclass": cursors.DictCursor}
        # 读取全局变量 - 根据选择的数据 读取指定的数据库配置 连接对应的数据库
        db_config = g_context().get_dict("_database")[kwargs["数据库"]]
        config.update(db_config)
        con = pymysql.connect(**config)
        cur = con.cursor()
        cur.execute(kwargs["sql语句"])
        rs = cur.fetchall()
        cur.close()
        con.close()
        print("数据库查询结果:", rs)

        # var_names = kwargs["引用变量"]
        var_names = kwargs["引用变量"].split(',')  # 关键转换：按逗号分割字符串
        print("var_names",var_names)

        result = {}
        for i, data in enumerate(rs, start=1):
            for j, value in enumerate(var_names):
                result[f'{var_names[j]}_{i}'] = data.get(var_names[j]) # 根据变量名称找读取出来的内容
        print("数据库拿到的数据是：",result)
        g_context().set_by_dict(result)


    def postgresql_sql_exec(self, **kwargs):
        """执行PostgreSQL数据库SQL语句（极简版，结构与MySQL方法一致）"""
        import psycopg2
        from psycopg2 import extras

        # 打印执行的SQL语句（与原方法一致）
        # print("执行SQL:", kwargs["sql语句"])
        # sql_value = kwargs["sql语句"]
        # all_context = g_context().show_dict()
        # sql_value = refresh(sql_value, all_context)
        # print("转换后的sql", sql_value)

        # 配置数据库连接（使用DictCursor获取字典结果）
        config = {"cursor_factory": extras.DictCursor}
        db_config = g_context().get_dict("_database")[kwargs["数据库"]]
        config.update(db_config)

        # 建立连接并执行SQL
        con = psycopg2.connect(**config)
        cur = con.cursor()
        cur.execute(kwargs["sql语句"])
        rs = cur.fetchall()  # 仅处理查询结果，不区分语句类型

        # 关闭连接（与原方法一致）
        cur.close()
        con.close()
        print("数据库查询结果:", rs)

        # 处理变量引用（与原方法一致）
        var_names = kwargs["引用变量"].split(',')
        print("var_names", var_names)

        result = {}
        for i, data in enumerate(rs, start=1):
            # for j, value in enumerate(var_names):
            #     result[f'{var_names[j]}_{i}'] = data.get(var_names[j])
            # 检查data是否为字典类型（PostgreSQL DictCursor应该返回字典）
            if isinstance(data, dict):
                for j, value in enumerate(var_names):
                    result[f'{var_names[j]}_{i}'] = data.get(var_names[j])
            else:
                # 如果不是字典，尝试按位置索引获取值
                for j, value in enumerate(var_names):
                    if j < len(data):  # 确保索引不越界
                        result[f'{var_names[j]}_{i}'] = data[j]
                    else:
                        result[f'{var_names[j]}_{i}'] = None

        print("数据库拿到的数据是：", result)
        g_context().set_by_dict(result)




