class slide_down:

    def __init__(self, driver):
        self.driver = driver
    # 向下滚动
    def slide_right(self, **kwargs):
        value = kwargs["滚动距离"]
        self.driver.execute_script(f"window.scrollBy({value}, 0);")