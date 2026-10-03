from selenium.webdriver import ActionChains, Keys


class swipe_upwards_keys:

    def __init__(self, driver):
        self.driver = driver
    # 向下滚动
    def swipe_upwards_keys(self, **kwargs):
        value = kwargs["滚动次数"]
        value = int(value)
        actions = ActionChains(self.driver)
        # 模拟按下10次向下箭头键
        for _ in range(value):
            actions.send_keys(Keys.ARROW_UP).perform()
