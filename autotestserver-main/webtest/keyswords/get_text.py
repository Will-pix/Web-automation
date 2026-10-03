from webtest.tool.webrun.core.globalContext import g_context
import time


class get_text:

    def __init__(self, driver):
        self.driver = driver

    # 元素操作-输入内容
    def get_text(self, **kwargs):
        # 要设置的变量名
        time.sleep(1)
        var_name = kwargs["var_name"]
        element = self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"])
        text = element.text
        print("获取的文本:",text)
        g_context().set_dict(var_name, text)
        print(f"完整响应存入变量 '{var_name}': {text}")