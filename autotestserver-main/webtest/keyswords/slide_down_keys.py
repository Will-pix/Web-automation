from selenium.webdriver import ActionChains, Keys


class slide_down_keys:

    def __init__(self, driver):
        self.driver = driver
    # 向下滚动
    def slide_down_keys(self, **kwargs):
        value = kwargs["滚动次数"]
        value = int(value)
        actions = ActionChains(self.driver)
        # 模拟按下10次向下箭头键
        for _ in range(value):
            actions.send_keys(Keys.ARROW_DOWN).perform()
