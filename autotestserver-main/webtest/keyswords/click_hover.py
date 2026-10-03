from time import sleep
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

class click_hover:
    def __init__(self, driver):
        self.driver = driver
    # 查找元素方法封装
    def click_hover(self,**kwargs):
        sleep(1)
        by = kwargs["定位方式"]
        value = kwargs["目标对象"]
        # 使用显示等待 查找元素
        element =  WebDriverWait(self.driver, timeout= 30, poll_frequency= 0.5, ignored_exceptions=None).until(lambda x:x.find_element(by=by, value=value))
        ActionChains(self.driver).move_to_element(element).perform()
        sleep(1)

