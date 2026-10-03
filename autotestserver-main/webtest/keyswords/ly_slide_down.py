class ly_slide_down:
    def __init__(self, driver):
        self.driver = driver
    # 向下滚动
    def ly_slide_down(self, **kwargs):
        right_scroll_container = self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"])
        self.driver.execute_script(f"arguments[0].scrollTop += {kwargs['滚动距离']}", right_scroll_container)