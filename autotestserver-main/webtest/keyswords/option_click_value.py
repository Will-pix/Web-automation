from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from webtest.tool.webrun.core.globalContext import g_context
from webtest.tool.webrun.utils.VarRender import refresh

class option_click_value:
    def __init__(self, driver):
        self.driver = driver
    # 元素操作-点击元素
    def option_click_value(self,**kwargs):
        all_context = g_context().show_dict()

        by = kwargs["定位方式"]
        value = kwargs["目标对象"]
        print("替换前的点击元素是:",value)
        value = refresh(value,all_context)
        print("替换后的点击元素是:",value)

        # 使用显示等待 查找元素
        element =  WebDriverWait(self.driver, timeout= 30, poll_frequency= 0.5, ignored_exceptions=None).until(lambda x:x.find_element(by=by, value=value))
        element.click()