from webtest.tool.webrun.core.globalContext import g_context


class get_value:

    def __init__(self, driver):
        self.driver = driver

    # 元素操作-输入内容
    def get_value(self, **kwargs):
        # 要设置的变量名
        var_name = kwargs["var_name"]
        # 使用 value 属性获取按钮文本
        element = self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"])
        text = element.get_attribute("value")  # 百度按钮文本通常在 value 属性中
        g_context().set_dict(var_name, text)
        print(f"完整响应存入变量 '{var_name}': {text}")